import fcntl
import uuid
from datetime import datetime, timedelta
from . import store
from .config import ROOT, TZ, Secrets, now, settings
from .meta import Graph, MetaError, ingest_insight

def is_running():
    with (ROOT/'data/sync.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return False
        except BlockingIOError:
            return True

def collect(graph, platform, aid, endpoint, fields, callback, key, fallback_fields=None):
    try:
        for batch, sid in graph.pages(endpoint, {'fields': fields, 'limit': 100}, key):
            for item in batch:
                callback(item, sid)
        store.coverage(platform, aid, endpoint, 'complete', 'เก็บครบทุกหน้าที่ API ส่งกลับ')
    except MetaError as e:
        if fallback_fields and e.category == 'unsupported':
            collect(graph, platform, aid, endpoint, fallback_fields, callback, key)
            store.coverage(platform, aid, endpoint, 'unsupported',
                           'เก็บข้อมูลพื้นฐานแล้ว แต่ API ไม่รองรับภาพตัวอย่าง/URL สื่อในคำขอรอบนี้', 'media_preview')
            return
        store.coverage(platform, aid, endpoint, e.category, str(e))
        if e.category not in ('unsupported', 'permission'):
            raise

def insights(graph, platform, aid, oid, names, start=None, end=None):
    endpoint = f'{oid}/insights'
    for name in names:
        params = {'metric': name}
        if start:
            params.update(period='day', since=start.isoformat(), until=end.isoformat())
            if platform == 'instagram':
                params['metric_type'] = 'time_series'
        else:
            params['period'] = 'lifetime'
        try:
            try:
                body, source = graph.get(endpoint, params)
            except MetaError as e:
                if platform == 'instagram' and start and e.category == 'unsupported':
                    params['metric_type'] = 'total_value'
                    body, source = graph.get(endpoint, params)
                else:
                    raise
            # Preserve requested bounds for an account total-over-range response.
            if start:
                for series in body.get('data', []):
                    if 'total_value' in series:
                        series['period'] = 'total_over_range'
                        series['values'] = [{'value': series['total_value'].get('value'),
                                             'end_time': end.isoformat()}]
                        series.pop('total_value', None)
            count = ingest_insight(platform, aid, oid, name, body, source)
            if start:
                with store.db() as c:
                    c.execute("UPDATE metrics SET start_at=? WHERE source_id=? AND period='total_over_range'",
                              (start.isoformat(), source))
            store.coverage(platform, aid, endpoint, 'available' if count else 'empty',
                           f'{start or "lifetime"} → {end or ""}; {count} จุดข้อมูล', name)
        except MetaError as e:
            store.coverage(platform, aid, endpoint, e.category, str(e), name)
            if e.category not in ('unsupported', 'permission'):
                raise

def sync_platform(graph, platform, aid, cfg):
    # If a profile field is unsupported, still collect posts; do not redefine fans as followers.
    fields = 'id,name,followers_count' if platform == 'facebook' else 'id,name,username,followers_count'
    try:
        body, source = graph.get(aid, {'fields': fields})
    except MetaError as e:
        if e.category != 'unsupported':
            raise
        body, source = graph.get(aid, {'fields': 'id,name' if platform == 'facebook' else 'id,username'})
        store.coverage(platform, aid, aid, 'unsupported', 'อ่านจำนวนผู้ติดตามไม่ได้', 'followers_count')
    store.account(platform, aid, body.get('name', cfg.get('page_name', '')), body.get('username', ''),
                  body.get('followers_count'), source)
    today = datetime.now(TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    # Page daily data can be fetched for the full 90 days. IG windows are split to <=30 days.
    for offset in (90, 60, 30):
        start, end = today - timedelta(days=offset), today - timedelta(days=offset - 30)
        insights(graph, platform, aid, aid, cfg[f'{platform}_account_metrics'], start, end)

    def accept(item, source):
        if platform == 'facebook':
            item = dict(item)
            item['thumbnail_url'] = item.get('full_picture', '')
            item['media_type'] = 'VIDEO' if any('video' in a.get('media_type', '').lower()
                for a in item.get('attachments', {}).get('data', [])) else 'POST'
        store.post(platform, aid, item, source)
        pairs = [('likes', 'like_count'), ('comments', 'comments_count')] if platform == 'instagram' else []
        for canonical, native in pairs:
            if item.get(native) is not None:
                store.metric(platform, aid, str(item['id']), canonical, native, 'lifetime', '', '',
                             item[native], source)
        if platform == 'facebook':
            for native in ('shares', 'comments', 'reactions'):
                value = (item.get(native, {}).get('count') if native == 'shares' else
                         item.get(native, {}).get('summary', {}).get('total_count'))
                if value is not None:
                    store.metric(platform, aid, str(item['id']), native, native, 'lifetime', '', '', value, source)

    endpoint = f'{aid}/published_posts' if platform == 'facebook' else f'{aid}/media'
    base_fields = ('id,created_time,message,permalink_url,shares,comments.limit(0).summary(true),'
              'reactions.limit(0).summary(true),attachments{media_type}' if platform == 'facebook' else
              'id,timestamp,caption,media_type,media_product_type,permalink,like_count,comments_count')
    fields = base_fields + (',full_picture' if platform=='facebook' else ',media_url,thumbnail_url')
    key = f'{platform}:{aid}:posts:backfill'
    was_complete = store.checkpoint(key)['complete']
    if not was_complete:
        collect(graph, platform, aid, endpoint, fields, accept, key, base_fields)
    else:
        # Refresh newest pages; ordered media/posts stop at a 90-day content cutoff.
        def refresh_pages():
            try:
                yield from graph.pages(endpoint, {'fields': fields, 'limit': 100})
            except MetaError as e:
                if e.category!='unsupported':
                    raise
                store.coverage(platform, aid, endpoint, 'unsupported',
                               'URL ภาพตัวอย่างอ่านไม่ได้ ใช้ข้อมูลโพสต์พื้นฐานแทน', 'media_preview')
                yield from graph.pages(endpoint, {'fields': base_fields, 'limit': 100})
        for batch, sid in refresh_pages():
            stop = False
            for item in batch:
                stamp = item.get('timestamp') or item.get('created_time')
                if stamp and datetime.fromisoformat(stamp.replace('Z', '+00:00')) < today - timedelta(days=90):
                    stop = True
                    continue
                accept(item, sid)
            if stop:
                break

    if platform == 'facebook':
        def accept_reel(item, source):
            item = dict(item)
            ident = str(item['id'])
            item['id'] = ident if '_' in ident else f'{aid}_{ident}'
            item['message'] = item.get('description', '')
            item['media_type'] = 'REELS'
            store.post(platform, aid, item, source)
        reel_key = f'{platform}:{aid}:reels:{"backfill" if not was_complete else today.date()}'
        collect(graph, platform, aid, f'{aid}/video_reels', 'id,created_time,description,permalink_url',
                accept_reel, reel_key)

    posts = store.rows('SELECT * FROM posts WHERE platform=? AND account_id=? ORDER BY published_at DESC', (platform, aid))
    for p in posts:
        oid = p['post_id']
        comments_key = f'{platform}:{aid}:{oid}:comments:backfill'
        complete = store.checkpoint(comments_key)['complete']
        stamp = p.get('published_at')
        recent = bool(stamp and datetime.fromisoformat(stamp.replace('Z', '+00:00')) >= today - timedelta(days=90))
        if not complete or recent:
            fields = 'id,message,created_time' if platform == 'facebook' else 'id,text,timestamp'
            collect(graph, platform, aid, f'{oid}/comments', fields,
                    lambda item, source: store.comment(platform, aid, oid, item, source),
                    comments_key if not complete else comments_key + ':' + str(today.date()))
        insight_key = f'{platform}:{aid}:{oid}:insights:backfill'
        if not store.checkpoint(insight_key)['complete']:
            insights(graph, platform, aid, oid, cfg[f'{platform}_post_metrics'])
            store.save_checkpoint(insight_key, None, True)
        elif recent:
            refresh_key = insight_key + ':' + str(today.date())
            if not store.checkpoint(refresh_key)['complete']:
                insights(graph, platform, aid, oid, cfg[f'{platform}_post_metrics'])
                store.save_checkpoint(refresh_key, None, True)
    # Import all available replies independently; failures are visible in coverage.
    parents = store.rows("SELECT * FROM comments WHERE platform=? AND account_id=? AND parent_id=''", (platform, aid))
    for parent in parents:
        endpoint = f'{parent["comment_id"]}/' + ('comments' if platform == 'facebook' else 'replies')
        fields = 'id,message,created_time' if platform == 'facebook' else 'id,text,timestamp'
        collect(graph, platform, aid, endpoint, fields,
                lambda item, source: store.comment(platform, aid, parent['post_id'], item, source, parent['comment_id']),
                f'{platform}:{aid}:{parent["comment_id"]}:replies:{today.date()}')

def run_sync(secret_store=None):
    cfg, secrets = settings(), secret_store or Secrets()
    if not cfg['page_id'] or not cfg['api_version']:
        raise ValueError('เลือกเพจและ API version ในหน้าตั้งค่าก่อน')
    lock = (ROOT / 'data/sync.lock').open('a')
    try:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('มีงานซิงก์กำลังทำอยู่') from None
        ident = uuid.uuid4().hex
        with store.db() as c:
            c.execute("UPDATE jobs SET status='partial',ended_at=?,message='งานเดิมหยุดก่อนเสร็จ เริ่มเก็บต่อ' WHERE status='running'", (now(),))
            c.execute('INSERT INTO jobs VALUES(?,?,?,?,?)', (ident, now(), None, 'running', 'กำลังอ่าน Meta API'))
        status, message = 'complete', 'ซิงก์เสร็จ ตรวจข้อจำกัดแต่ละ endpoint ในแดชบอร์ด'
        try:
            token = secrets.get('page')
            if not token:
                raise ValueError('ยังไม่มี Page token ใน Keychain กรุณาเชื่อมบัญชี')
            for platform, aid in (('facebook', cfg['page_id']), ('instagram', cfg['ig_id'])):
                if not aid:
                    continue
                graph = Graph(cfg['api_version'], token, platform, cfg['request_budget'])
                try:
                    sync_platform(graph, platform, aid, cfg)
                except MetaError as e:
                    store.coverage(platform, aid, 'sync', e.category, str(e))
                    if e.category == 'expired':
                        raise
                    status, message = 'partial', str(e)
                    # One platform exhausting its budget must not starve the other platform.
                else:
                    store.coverage(platform, aid, 'sync', 'complete', 'จบรอบอ่านข้อมูลของแพลตฟอร์มนี้')
                finally:
                    graph.close()
            issues = store.rows("SELECT status FROM coverage WHERE status NOT IN ('complete','available') AND account_id IN (?,?)",
                                (cfg['page_id'], cfg['ig_id']))
            if issues:
                status, message = 'partial', 'เก็บข้อมูลแล้ว แต่บาง endpoint/metric ยังอ่านไม่ได้ ดูรายการข้อจำกัด'
        except MetaError as e:
            status, message = ('reconnect' if e.category == 'expired' else 'partial'), str(e)
        except ValueError as e:
            status, message = 'blocked', str(e)
        except Exception:
            # Never include raw HTTP/keychain errors or credentials in a job log.
            status, message = 'error', 'งานหยุดจากข้อผิดพลาดภายใน ตรวจระบบและซิงก์ใหม่เพื่อเก็บต่อ'
        with store.db() as c:
            c.execute('UPDATE jobs SET ended_at=?,status=?,message=? WHERE id=?', (now(), status, message, ident))
        return {'id': ident, 'status': status, 'message': message}
    finally:
        lock.close()
