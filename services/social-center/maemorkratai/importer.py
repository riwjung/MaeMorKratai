import csv
import hashlib
import io
import json
import math
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from . import store
from .config import TZ, now

ALIASES = {
    'post_id': ['post id', 'media id', 'id', 'รหัสโพสต์', 'content id'],
    'published_at': ['publish time', 'published at', 'created time', 'date', 'วันที่', 'เวลาเผยแพร่'],
    'text': ['description', 'caption', 'post message', 'message', 'คำบรรยาย', 'text'],
    'permalink': ['permalink', 'post link', 'url', 'ลิงก์โพสต์'],
    'media_type': ['post type', 'media type', 'content type', 'ประเภทโพสต์'],
    'views': ['views', 'video views', 'ยอดดู', 'จำนวนการดู'],
    'likes': ['likes', 'ถูกใจ'], 'reactions': ['reactions', 'ปฏิกิริยา'],
    'comments': ['comments', 'ความคิดเห็น'], 'shares': ['shares', 'แชร์'],
    'saves': ['saves', 'saved', 'บันทึก'],
    'interactions': ['total interactions', 'interactions', 'ปฏิสัมพันธ์'],
    'followers': ['followers', 'followers count', 'ผู้ติดตาม'],
    'watch_time': ['average watch time', 'average watch time seconds', 'เวลารับชมเฉลี่ย'],
    'comment_id': ['comment id', 'รหัสคอมเมนต์'],
}

def read_csv(content):
    if len(content) > 20 * 1024 * 1024:
        raise ValueError('ไฟล์ CSV ต้องไม่เกิน 20 MB')
    text = None
    for encoding in ('utf-8-sig', 'utf-16', 'cp874'):
        try:
            text = content.decode(encoding)
            break
        except UnicodeError:
            continue
    if text is None:
        raise ValueError('อ่าน encoding ไม่ได้ กรุณาส่งออกเป็น CSV UTF-8')
    try:
        dialect = csv.Sniffer().sniff(text[:8192], delimiters=',;\t')
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    headers = reader.fieldnames or []
    if not headers or len(headers) != len(set(headers)):
        raise ValueError('ไม่มีชื่อคอลัมน์หรือชื่อคอลัมน์ซ้ำ')
    if any(h.strip().lower().replace(' ', '_') in store.SECRET_KEYS for h in headers):
        raise ValueError('ไฟล์มีคอลัมน์ token/secret กรุณาลบคอลัมน์นั้นก่อนนำเข้า')
    records = list(reader)
    if not records:
        raise ValueError('ไฟล์ไม่มีแถวข้อมูล')
    if any(None in r for r in records):
        raise ValueError('จำนวนช่องใน CSV ไม่ตรงกับหัวคอลัมน์')
    return headers, records

def guess_mapping(headers):
    clean = {h.strip().lower().replace('_', ' '): h for h in headers}
    return {key: next((clean[a] for a in [key.replace('_', ' ')] + names if a in clean), '')
            for key, names in ALIASES.items()}

def preview(content):
    headers, records = read_csv(content)
    return {'headers': headers, 'mapping': guess_mapping(headers), 'rows': len(records), 'fields': list(ALIASES)}

def number(value):
    if value is None or str(value).strip() in ('', '-', '—', 'N/A', 'n/a'):
        return None
    try:
        result = float(str(value).strip().replace(',', '').replace('%', ''))
    except ValueError:
        raise ValueError('ค่าตัวชี้วัดต้องเป็นตัวเลข ไม่รองรับเลขย่อ เช่น 1.2K') from None
    if not math.isfinite(result) or result < 0:
        raise ValueError('ค่าตัวชี้วัดต้องไม่ติดลบและเป็นค่าจำกัด')
    return result

def stamp(value, timezone='Asia/Bangkok'):
    if not value:
        return ''
    parsed = None
    try:
        parsed = datetime.fromisoformat(value.strip().replace('Z', '+00:00'))
    except ValueError:
        candidates = []
        for fmt in ('%m/%d/%Y %H:%M', '%m/%d/%Y', '%d/%m/%Y %H:%M', '%d/%m/%Y'):
            try:
                candidates.append(datetime.strptime(value.strip(), fmt))
            except ValueError:
                pass
        if len(set(candidates)) > 1:
            raise ValueError('วันที่แบบ slash กำกวม กรุณาแปลงเป็น YYYY-MM-DD ก่อนนำเข้า')
        if candidates:
            parsed = candidates[0]
    if parsed is None:
        raise ValueError('อ่านวันที่ไม่ได้ ใช้ YYYY-MM-DD หรือวันที่ตามรูปแบบส่งออก Meta')
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=ZoneInfo(timezone))
    return parsed.isoformat()

def import_csv(content, platform, account_id, kind='content', mapping=None,
               timezone='Asia/Bangkok', period='lifetime', start='', end='', name='CSV export'):
    if platform not in ('facebook', 'instagram') or kind not in ('content', 'daily', 'comments'):
        raise ValueError('แพลตฟอร์มหรือชนิดข้อมูลไม่ถูกต้อง')
    if not account_id:
        raise ValueError('กรอก Account/Page ID หรือชื่อชุดข้อมูลที่แยกบัญชีชัดเจน')
    ZoneInfo(timezone)
    headers, records = read_csv(content)
    mapping = mapping or guess_mapping(headers)
    if any(v and v not in headers for v in mapping.values()):
        raise ValueError('ชื่อคอลัมน์ที่จับคู่ไม่มีในไฟล์')
    if period not in ('lifetime', 'total_over_range'):
        raise ValueError('ช่วงวัดไม่ถูกต้อง')
    start, end = stamp(start, timezone), stamp(end, timezone)
    if period == 'total_over_range' and (not start or not end or start >= end):
        raise ValueError('ระบุวันเริ่มและวันสิ้นสุดแบบไม่รวมวันสุดท้ายให้ครบ')
    fingerprint = hashlib.sha256(content + json.dumps([platform, account_id, kind, mapping, timezone,
                                                     period, start, end], sort_keys=True).encode()).hexdigest()
    previous = store.rows('SELECT * FROM imports WHERE sha256=?', (fingerprint,))
    if previous:
        return {'status': 'unchanged', 'source_id': previous[0]['source_id'], 'rows': 0}
    prepared = []
    # Validate every row before making any database changes.
    for i, row in enumerate(records, 2):
        def get(key):
            return (row.get(mapping.get(key, ''), '') or '').strip()
        try:
            published = stamp(get('published_at'), timezone)
            oid = get('post_id')
            if kind == 'content' and not oid:
                if not get('permalink'):
                    raise ValueError('ต้องมี post_id หรือ permalink')
                oid = 'url-' + hashlib.sha256(get('permalink').encode()).hexdigest()[:24]
            if kind == 'daily' and not published:
                raise ValueError('ข้อมูลรายวันต้องมีวันที่')
            if kind == 'comments' and (not oid or not get('comment_id')):
                raise ValueError('คอมเมนต์ต้องมี post_id และ comment_id')
            metrics = {key: number(get(key)) for key in
                       ('views', 'likes', 'reactions', 'comments', 'shares', 'saves', 'interactions', 'followers', 'watch_time')}
            prepared.append({'id': oid, 'timestamp': published, 'caption': get('text'),
                             'permalink': get('permalink'), 'media_type': get('media_type') or 'POST',
                             'comment_id': get('comment_id'), 'metrics': metrics})
        except ValueError as e:
            raise ValueError(f'แถว {i}: {e}') from None
    known = store.rows('SELECT * FROM accounts WHERE platform=?', (platform,))
    if known and known[0]['account_id'] != account_id:
        raise ValueError('ชุดข้อมูลนี้คนละบัญชีกับที่เลือกไว้ กรุณาใช้ ID บัญชีเดิม')
    source = store.snapshot(platform, 'csv-import', {'account_id': account_id, 'kind': kind,
        'mapping': mapping, 'timezone': timezone, 'period': period, 'start': start, 'end': end,
        'filename': name, 'fingerprint': fingerprint}, {'headers': headers, 'rows': records}, kind='csv')
    if not known:
        store.account(platform, account_id, 'ข้อมูลนำเข้า CSV — ยังไม่ยืนยันผ่าน API', '', None, source)
    for item in prepared:
        if kind == 'comments':
            store.comment(platform, account_id, item['id'], {'id': item['comment_id'],
                          'text': item['caption'], 'timestamp': item['timestamp']}, source)
            continue
        oid = account_id if kind == 'daily' else item['id']
        if kind == 'content':
            store.post(platform, account_id, item, source)
        for key, value in item['metrics'].items():
            if value is None:
                continue
            p, s, e = period, start, end
            if kind == 'daily':
                dt = datetime.fromisoformat(item['timestamp'])
                s = dt.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
                e = (datetime.fromisoformat(s) + timedelta(days=1)).isoformat()
                p = 'snapshot' if key == 'followers' else 'day'
                if key == 'followers':
                    s, e = '', dt.isoformat()
            store.metric(platform, account_id, oid, key, mapping[key], p, s, e, value, source,
                         unit='seconds' if key == 'watch_time' else 'count')
    with store.db() as c:
        c.execute('INSERT INTO imports VALUES(?,?,?)', (fingerprint, source, now()))
    store.coverage(platform, account_id, 'csv-import', 'imported',
                   f'{len(prepared)} แถว; {kind}; {period}; ขอบเขตตามไฟล์ ไม่ยืนยันว่าครบทั้งบัญชี')
    return {'status': 'imported', 'source_id': source, 'rows': len(prepared)}
