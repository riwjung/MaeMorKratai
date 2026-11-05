from collections import Counter
from datetime import datetime, timedelta
from . import store
from .config import TZ, now

LABELS = {'views': 'ยอดดู', 'followers': 'ผู้ติดตาม', 'interactions': 'ปฏิสัมพันธ์',
          'shares': 'แชร์', 'saves': 'บันทึก', 'likes': 'ถูกใจ', 'comments': 'คอมเมนต์',
          'reactions': 'ปฏิกิริยา', 'watch_time': 'เวลารับชมเฉลี่ย'}
TOPICS = {'ความรัก': ('รัก', 'แฟน', 'คู่', 'โสด'), 'การงาน': ('งาน', 'อาชีพ', 'ธุรกิจ'),
          'การเงิน': ('เงิน', 'โชค', 'รายได้', 'รวย'), 'ไพ่/เลือกกอง': ('ไพ่', 'เลือกกอง', 'pick a'),
          'ราศี/วันเกิด': ('ราศี', 'วันเกิด', 'เกิดวัน'), 'คำแนะนำ/กำลังใจ': ('กำลังใจ', 'แนะนำ', 'สู้')}

def dt(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(TZ) if value else None

def current_accounts():
    return store.rows('SELECT * FROM accounts')

def data(platform):
    account = store.rows('SELECT * FROM accounts WHERE platform=?', (platform,))
    aid = account[0]['account_id'] if account else ''
    records = store.rows('SELECT * FROM metrics WHERE platform=? AND account_id=? ORDER BY observed_at', (platform, aid))
    return (account[0] if account else None), records

def choose(rows):
    # Prefer a current available value over a previous empty/unsupported probe.
    valid = [r for r in rows if r['status'] == 'available' and r['value'] is not None]
    return max(valid, key=lambda r: (r['end_at'] if r['period']=='snapshot' else '',
                                     r['observed_at'], r['end_at'], r['start_at'])) if valid else None

def window(records, oid, metric, start, end):
    candidates = [r for r in records if r['object_id'] == oid and r['metric'] == metric]
    exact = choose([r for r in candidates if r['period'] == 'total_over_range'
                    and dt(r['start_at']) == start and dt(r['end_at']) == end])
    if exact:
        return {'value': exact['value'], 'complete': True, 'days': (end-start).days,
                'sources': [exact['source_id']], 'basis': 'total_over_range'}
    daily = {}
    for r in candidates:
        if r['period'] != 'day' or r['status'] != 'available' or r['value'] is None:
            continue
        s, e = dt(r['start_at']), dt(r['end_at'])
        # Only aggregate exact daily buckets within the requested window.
        if s and e and start <= s < end and e == s + timedelta(days=1) and s.hour == 0 and s.minute == 0:
            daily[s.date()] = r
    expected = (end-start).days
    complete = len(daily) == expected
    return {'value': sum(r['value'] for r in daily.values()) if complete else None,
            'complete': complete, 'days': len(daily),
            'sources': sorted({r['source_id'] for r in daily.values()}), 'basis': 'day'}

def overview(platform, at=None):
    account, records = data(platform)
    today = (at or datetime.now(TZ)).replace(hour=0, minute=0, second=0, microsecond=0)
    aid = account['account_id'] if account else ''
    records = [r for r in records if r['object_id']==aid]
    cards = []
    for name in ('views', 'interactions'):
        cur = window(records, aid, name, today-timedelta(days=30), today)
        prev = window(records, aid, name, today-timedelta(days=60), today-timedelta(days=30))
        delta = ((cur['value']-prev['value']) / prev['value'] * 100
                 if cur['value'] is not None and prev['value'] not in (None, 0) else None)
        cards.append({'metric': name, 'label': LABELS[name], 'current': cur, 'previous': prev, 'change_pct': delta})
    followers = choose([r for r in records if r['metric']=='followers' and r['object_id']==aid and r['period']=='snapshot'])
    cards.insert(0, {'metric': 'followers', 'label': 'ผู้ติดตามล่าสุด',
                    'value': followers['value'] if followers else account.get('followers') if account else None,
                    'observed_at': followers['observed_at'] if followers else None,
                    'measured_at': followers['end_at'] if followers else None,
                    'source_id': followers['source_id'] if followers else None})
    trend = []
    for i in range(90, 0, -1):
        start = today - timedelta(days=i)
        row = {'date': str(start.date())}
        for name in ('views', 'interactions'):
            w = window(records, aid, name, start, start+timedelta(days=1))
            row[name] = w['value']
        trend.append(row)
    snapshots = [r for r in records if r['metric']=='followers' and r['period']=='snapshot' and r['object_id']==aid]
    follower_days = {}
    for r in snapshots:
        key = r['end_at'][:10]
        previous = follower_days.get(key)
        if previous is None or r['observed_at'] >= previous['observed_at']:
            follower_days[key] = r
    follower_trend = []
    for i in range(89,-1,-1):
        day = str((today-timedelta(days=i)).date())
        found = follower_days.get(day)
        follower_trend.append({'date':day,'value':found['value'] if found else None,
                               'source_id':found['source_id'] if found else None})
    snapshot_end = datetime.fromisoformat(followers['end_at'][:10]).replace(tzinfo=TZ) if followers else today
    baseline = choose([r for r in snapshots if r['end_at'][:10] == str((snapshot_end-timedelta(days=30)).date())])
    growth = followers['value']-baseline['value'] if followers and baseline else None
    return {'platform': platform, 'account': account, 'cards': cards, 'trend': trend,
            'follower_trend': follower_trend, 'follower_growth_30d': growth,
            'window_start': (today-timedelta(days=30)).isoformat(), 'window_end': today.isoformat(),
            'previous_start': (today-timedelta(days=60)).isoformat(), 'timezone': 'Asia/Bangkok',
            'definitions': {'views': 'ยอดดูตามนิยามแพลตฟอร์ม รวมเฉพาะช่วงที่มีข้อมูลครบ',
                'interactions': 'total_interactions จากต้นทาง ไม่เติมส่วนประกอบที่ขาด',
                'followers': 'จำนวนล่าสุด; การเปลี่ยนแปลงใช้ snapshot ต้นช่วงและปลายช่วงเท่านั้น'},
            'coverage': store.rows('SELECT * FROM coverage WHERE platform=? AND account_id=? ORDER BY updated_at DESC', (platform, aid)),
            'post_count': len(store.rows('SELECT post_id FROM posts WHERE platform=? AND account_id=?', (platform, aid)))}

def content(platform, ranking='views', age=0, kind='all', at=None):
    if ranking not in LABELS:
        raise ValueError('ตัวชี้วัดไม่ถูกต้อง')
    account, records = data(platform)
    aid = account['account_id'] if account else ''
    today = at or datetime.now(TZ)
    posts = store.rows('SELECT * FROM posts WHERE platform=? AND account_id=?', (platform, aid))
    by_object = {}
    for r in records:
        by_object.setdefault(r['object_id'], {}).setdefault(r['metric'], []).append(r)
    result = []
    for p in posts:
        published = dt(p['published_at'])
        days = max(0, (today-published).days) if published else None
        if age and (days is None or days > age):
            continue
        if kind != 'all' and p['media_type'] != kind:
            continue
        metrics = {}
        for name in LABELS:
            m = choose([r for r in by_object.get(p['post_id'],{}).get(name,[]) if r['period']=='lifetime'])
            metrics[name] = {'value': m['value'], 'source_id': m['source_id'], 'native_metric': m['native_metric'],
                             'observed_at': m['observed_at'], 'unit': m['unit']} if m else None
        # Do not silently rank ranged metrics alongside lifetime metrics.
        ranged = [r for values in by_object.get(p['post_id'],{}).values() for r in values if r['period']=='total_over_range']
        tags = [tag for tag, words in TOPICS.items() if any(word in p['text'].lower() for word in words)]
        result.append({**p, 'age_days': days, 'metrics': metrics, 'ranged_metrics': ranged,
                       'topic_tags': tags or ['ยังไม่จัดหมวด'], 'hook': p['text'].split('\n')[0][:180],
                       'ranking_value': metrics[ranking]['value'] if metrics[ranking] else None})
    result.sort(key=lambda p: (p['ranking_value'] is not None, p['ranking_value'] or 0), reverse=True)
    return result

def findings(platform):
    posts = content(platform)
    counts = Counter(tag for p in posts for tag in p['topic_tags'])
    account, _ = data(platform)
    aid = account['account_id'] if account else ''
    comments = store.rows('SELECT text FROM comments WHERE platform=? AND account_id=?', (platform, aid))
    themes = Counter()
    for c in comments:
        for tag, words in TOPICS.items():
            if any(word in c['text'].lower() for word in words):
                themes[tag] += 1
    ranked = [p for p in posts if p['ranking_value'] is not None]
    return {'content_topics': dict(counts), 'comment_themes': dict(themes), 'comments_analyzed': len(comments),
            'hooks': [{'post_id': p['post_id'], 'hook': p['hook'], 'permalink': p['permalink']} for p in ranked[:10]],
            'method': 'จัดหมวดด้วยคำสำคัญ หนึ่งโพสต์/คอมเมนต์อาจอยู่หลายหมวด ต้องตรวจความหมายโดยเจ้าของช่อง',
            'hypothesis': 'ทดลองประโยคเปิดและรูปแบบจากคอนเทนต์ที่มีข้อมูลดี โดยคงหัวข้อและความยาวให้ใกล้กัน'}
