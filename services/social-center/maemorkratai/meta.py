"""Only GET requests to graph.facebook.com. No publishing or messaging endpoints."""
import hashlib
import json
import time
from datetime import datetime, timedelta
from urllib.parse import urlsplit, parse_qs
import httpx
from . import store
from .config import TZ, now

class MetaError(Exception):
    def __init__(self, category, code=None):
        self.category, self.code = category, code
        texts = {
            'expired': 'Token หมดอายุหรือถูกยกเลิก กรุณาเชื่อมใหม่จากหน้าตั้งค่า',
            'permission': 'สิทธิ์ไม่พอ ตรวจ Page tasks / App roles / permissions ใน Meta',
            'unsupported': 'API ไม่รองรับ field/metric นี้สำหรับบัญชีหรือชนิดคอนเทนต์นี้',
            'rate_limit': 'Meta จำกัดการเรียก ระบบเก็บจุดต่อไว้แล้ว ลองซิงก์ใหม่ภายหลัง',
            'network': 'ติดต่อ Meta ไม่สำเร็จ ลองใหม่เมื่อเครือข่ายพร้อม',
            'budget': 'ถึงจำนวนคำขอต่อรอบแล้ว ซิงก์ครั้งถัดไปเพื่อเก็บต่อ',
            'response': 'รูปแบบผลตอบกลับ Meta ไม่ตรงที่รองรับ ตรวจ API version',
        }
        super().__init__(texts.get(category, 'Meta API ตอบกลับข้อผิดพลาด') + (f' (code {code})' if code else ''))

class Graph:
    def __init__(self, version, token, platform='meta', budget=500, transport=None, sleeper=time.sleep):
        self.version, self.token, self.platform = version, token, platform
        self.budget, self.requests, self.sleep = budget, 0, sleeper
        self.client = httpx.Client(base_url=f'https://graph.facebook.com/{version}/',
                                   timeout=30, transport=transport)

    def close(self):
        self.client.close()

    def get(self, endpoint, params=None):
        # No absolute URLs/paging-next URLs: credentials only travel to the fixed Graph origin.
        if '://' in endpoint or endpoint.startswith('/') or '..' in endpoint:
            raise ValueError('invalid graph endpoint')
        params = dict(params or {})
        for key in ('access_token', 'appsecret_proof'):
            params.pop(key, None)
        for attempt in range(3):
            if self.requests >= self.budget:
                raise MetaError('budget')
            self.requests += 1
            try:
                r = self.client.get(endpoint, params=params, headers={'Authorization': f'Bearer {self.token}'})
                body = r.json()
            except (httpx.HTTPError, ValueError):
                if attempt == 2:
                    raise MetaError('network') from None
                self.sleep(2 ** attempt)
                continue
            error = body.get('error', {}) if isinstance(body, dict) else {}
            code = error.get('code')
            if code == 190:
                raise MetaError('expired', code)
            if code in (4, 17, 32, 613) or r.status_code == 429 or r.status_code >= 500:
                if attempt == 2:
                    raise MetaError('rate_limit', code)
                try:
                    pause = min(30, max(1, float(r.headers.get('retry-after', 2 ** attempt))))
                except ValueError:
                    pause = 2 ** attempt
                self.sleep(pause)
                continue
            if error or r.is_error:
                raise MetaError('permission' if code in (10, 200, 294) else 'unsupported', code)
            if not isinstance(body, dict):
                raise MetaError('response')
            sid = store.snapshot(self.platform, endpoint, params, body, self.version, secrets=(self.token,))
            return body, sid
        raise MetaError('network')

    def pages(self, endpoint, params=None, key=None):
        params = dict(params or {})
        cursor = store.checkpoint(key) if key else {'cursor': None, 'complete': 0}
        if cursor['complete']:
            return
        if cursor['cursor']:
            params['after'] = cursor['cursor']
        seen = set()
        while True:
            body, sid = self.get(endpoint, params)
            data = body.get('data')
            if not isinstance(data, list):
                raise MetaError('response')
            paging = body.get('paging', {})
            after = paging.get('cursors', {}).get('after')
            has_next = bool(paging.get('next'))
            if has_next and not after:
                after = parse_qs(urlsplit(paging['next']).query).get('after', [None])[0]
            if has_next and (not after or after in seen or after == params.get('after')):
                raise MetaError('response')
            yield data, sid
            # Commit cursor only after the caller has ingested the entire page.
            if key:
                store.save_checkpoint(key, after if has_next else None, not has_next)
            if not has_next:
                break
            seen.add(after)
            params['after'] = after

def discovery(graph):
    granted, _ = graph.get('me/permissions')
    permissions = [p['permission'] for p in granted.get('data', []) if p.get('status') == 'granted']
    pages = []
    for batch, _ in graph.pages('me/accounts', {'fields': 'id,name,tasks,instagram_business_account', 'limit': 100}):
        for p in batch:
            ig = p.get('instagram_business_account')
            result = {**p, 'ig_username': '', 'ig_status': 'not_linked' if not ig else 'linked'}
            if ig:
                try:
                    info, _ = graph.get(str(ig['id']), {'fields': 'id,username'})
                    result['ig_username'] = info.get('username', '')
                except MetaError as e:
                    result['ig_status'] = e.category
            pages.append(result)
    return {'pages': pages, 'permissions': permissions}

# These are candidate metrics, not assertions of availability. Each is probed independently.
CANONICAL = {
    'page_media_view': 'views', 'page_media_views': 'views', 'post_media_view': 'views',
    'post_media_views': 'views', 'views': 'views', 'total_views': 'views',
    'total_interactions': 'interactions', 'saved': 'saves', 'shares': 'shares',
    'likes': 'likes', 'comments': 'comments', 'ig_reels_avg_watch_time': 'watch_time',
}

def ingest_insight(platform, aid, oid, name, body, source):
    count = 0
    for series in body.get('data', []):
        native = series.get('name', name)
        canonical = CANONICAL.get(native, native)
        period = series.get('period', 'lifetime')
        unit = 'milliseconds' if native == 'ig_reels_avg_watch_time' else 'count'
        values = series.get('values', [])
        if 'total_value' in series:
            values = [{'value': series['total_value'].get('value')}]
        for item in values:
            value = item.get('value')
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                continue
            end = item.get('end_time', '')
            start = ''
            if period == 'day' and end:
                start = (datetime.fromisoformat(end.replace('Z', '+00:00')) - timedelta(days=1)).isoformat()
            store.metric(platform, aid, oid, canonical, native, period, start, end, value, source, unit=unit)
            count += 1
    return count
