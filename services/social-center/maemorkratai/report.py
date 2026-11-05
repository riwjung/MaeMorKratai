import json
import uuid
from collections import Counter
from pathlib import Path
import yaml
from . import analysis, store
from .config import VAULT, ROOT, now

def safe_text(value):
    return str(value or '').replace('|', '\\|').replace('\n', ' ').replace('[[', '(').replace(']]', ')')

def display(value):
    return 'ไม่มีข้อมูล' if value is None else f'{value:,.0f}'

def coverage_summary(items, account_id):
    # The Desktop vault receives aggregate endpoint coverage, never individual comment IDs.
    counts = Counter()
    for item in items:
        endpoint = item['endpoint']
        if endpoint == account_id or endpoint.startswith(account_id+'/'):
            endpoint = 'account/' + endpoint.split('/')[-1] if '/' in endpoint else 'account/profile'
        elif '/' in endpoint:
            endpoint = 'content-or-thread/' + endpoint.rsplit('/',1)[1]
        counts[(endpoint,item['metric'],item['status'])] += 1
    return [{'endpoint':e,'metric':m,'status':s,'detail':f'{n} endpoint(s); ดูรายละเอียดในแดชบอร์ดบนเครื่อง'}
            for (e,m,s),n in counts.items()]

def page(kind, title, body, sources=(), **extra):
    today = now()[:10]
    front = {'type': kind, 'title': title, 'aliases': [], 'tags': ['domain/maemorkratai'],
             'created': today, 'updated': today}
    if kind != 'source':
        front.update(status='draft', sources=[f'[[{s}]]' for s in sources])
    front.update(extra)
    return '---\n' + yaml.safe_dump(front, allow_unicode=True, sort_keys=False) + '---\n\n' + body

def rebuild_index():
    entries = []
    for p in sorted((VAULT/'wiki').rglob('*.md')):
        meta = yaml.safe_load(p.read_text().split('---', 2)[1])
        entries.append(f'- [[{p.stem}]] — {meta["title"]}')
    (VAULT/'index.md').write_text('# แม่หมอกระต่าย — สารบัญ\n\nโดเมน: `domain/maemorkratai`\n\n' + '\n'.join(entries) + '\n')

def write_report():
    import fcntl
    with (ROOT/'data/report.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        return _write_report()

def _write_report():
    from .verify import verify_samples
    stamp = now().replace(':', '').replace('+', '-').replace('T', '-')
    slug = 'social-audit-' + stamp + '-' + uuid.uuid4().hex[:6]
    source_slug = slug + '-source'
    verification = verify_samples()
    payload = {'generated_at': now(), 'source_verification':verification, 'accounts': {}, 'limitations':
               ['เป็นข้อมูลที่ API/CSV เปิดให้เข้าถึง ไม่รับรองประวัติทั้งหมดของบัญชี',
                'ยอดสะสมโพสต์ไม่ใช่ยอดที่เกิดใน 30 วัน',
                'หัวข้อและธีมคอมเมนต์เป็นการจัดหมวดด้วยคำสำคัญ ไม่ใช่ข้อสรุปเชิงเหตุผล']}
    lines = [f'# สถานะ Social Media แม่หมอกระต่าย — {now()[:10]}',
             f'\nข้อมูลรอบนี้อ้างอิง [[{source_slug}]] เก็บถึง {now()}\n']
    for platform in ('facebook', 'instagram'):
        overview, posts, findings = analysis.overview(platform), analysis.content(platform), analysis.findings(platform)
        overview['coverage'] = coverage_summary(overview['coverage'],
                                                overview['account']['account_id'] if overview['account'] else '')
        # Export aggregate comment themes only, not individual comment text or names.
        payload['accounts'][platform] = {'overview': overview, 'content': posts[:10], 'findings': findings}
        lines += [f'## {platform.title()}', f'\nโพสต์ที่มีในระบบ: {overview["post_count"]} ชิ้น',
                  f'ช่วงปัจจุบัน: {overview["window_start"]} ถึง {overview["window_end"]} (ไม่รวมปลายช่วง)',
                  f'ช่วงเปรียบเทียบ: {overview["previous_start"]} ถึง {overview["window_start"]}\n',
                  '| ตัวชี้วัด | ปัจจุบัน | ก่อนหน้า |', '|---|---:|---:|']
        for card in overview['cards']:
            if card['metric'] == 'followers':
                lines.append(f'| ผู้ติดตามล่าสุด | {display(card["value"])} | ไม่ใช่ยอดรายเดือน |')
            else:
                lines.append(f'| {card["label"]} | {display(card["current"]["value"])} | {display(card["previous"]["value"])} |')
        check = verification[platform]
        lines.append(f'\nตรวจตัวอย่างเทียบ snapshot ต้นทาง: {check["posts_checked"]}/{check["required"]} โพสต์; {check["status"]} '
                     '(ไม่ใช่การเทียบกับหน้าจอ Meta Business Suite)\n')
        ranked = [p for p in posts if p['ranking_value'] is not None][:10]
        lines += ['\n### คอนเทนต์ตามยอดดูสะสม', '\n| โพสต์ | อายุโพสต์ | ยอดดูสะสม | ที่มา |', '|---|---:|---:|---|']
        for p in ranked:
            url = p['permalink']
            link = f'[เปิดโพสต์]({url})' if url.startswith(('https://', 'http://')) else 'ไม่มี permalink'
            lines.append(f'| {safe_text(p["hook"] or p["post_id"])} | {display(p["age_days"])} วัน | '
                         f'{display(p["ranking_value"])} | {link}; snapshot `{p["metrics"]["views"]["source_id"]}` |')
        if not ranked:
            lines.append('| ยังไม่มีข้อมูลยอดดูสะสม | — | — | รอ API/CSV |')
        lines += ['\n### ข้อสังเกตและช่องว่าง', f'\n**ข้อสังเกต:** หมวดจากคำสำคัญในโพสต์: {safe_text(findings["content_topics"])}',
                  f'ธีมคอมเมนต์แบบรวม: {safe_text(findings["comment_themes"])}; อ่าน {findings["comments_analyzed"]} คอมเมนต์',
                  findings['method'], '\nข้อจำกัดการอ่าน:']
        problems = [c for c in overview['coverage'] if c['status'] not in ('complete','available')]
        lines += [f'- `{c["endpoint"]}` / `{c["metric"]}`: {safe_text(c["status"])} — {safe_text(c["detail"])}'
                  for c in problems[:25]] or ['- ยังไม่มีรายการข้อจำกัดที่บันทึก หรือยังไม่ได้ทดสอบ API']
    lines += ['\n## แผนทดลอง 30 วัน — สมมติฐานที่ต้องตรวจ',
              '\nยังไม่กำหนดเป้ายอดผู้ติดตามเป็นตัวเลขจนมี baseline ของช่อง',
              '\n| ช่วง | งาน | วิธีวัด |', '|---|---|---|',
              '| วันที่ 1–7 | เจ้าของตรวจหมวดและเลือกหัวข้อจากข้อมูลเดิม เตรียมคู่คลิปที่หัวข้อ/ความยาวใกล้กัน | บันทึก baseline และ metric ที่อ่านได้ |',
              '| วันที่ 8–14 | ทดลองประโยคเปิดสองแบบ เปลี่ยนเฉพาะประโยคเปิด | เปรียบเทียบยอดดูเมื่ออายุคลิปครบ 7 วัน |',
              '| วันที่ 15–21 | ทดลองรูปแบบภาพ/มาสคอตหนึ่งตัวแปร หลังอนุมัติงบเจน | ดูยอดดู แชร์ บันทึก และ watch time ที่มี |',
              '| วันที่ 22–30 | ทบทวนคู่ทดลองและเลือกทำซ้ำ | วัดอายุคลิปเท่ากัน ไม่ใช้ยอดสะสมเก่าตัดสิน |',
              '\nการเผยแพร่และการใช้เครดิตยังต้องมีคำสั่งจากเจ้าของ ไม่มีการโพสต์อัตโนมัติในระบบนี้']
    raw_path = VAULT / 'raw' / (now()[:10] + '-' + source_slug + '.json')
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    # Preserve immutable report evidence, with native-metric/source IDs and coverage.
    with raw_path.open('x') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    source_ids = set()
    for values in payload['accounts'].values():
        for p in values['content']:
            source_ids.add(p['source_id'])
            source_ids.update(m['source_id'] for m in p['metrics'].values() if m)
            source_ids.update(m['source_id'] for m in p['ranged_metrics'])
        for card in values['overview']['cards']:
            if card.get('source_id'):
                source_ids.add(card['source_id'])
            source_ids.update(card.get('current',{}).get('sources',[]))
            source_ids.update(card.get('previous',{}).get('sources',[]))
        source_ids.update(r['source_id'] for r in values['overview']['follower_trend'] if r['source_id'])
    source_ids.update(m['source_id'] for checks in verification.values() for p in checks['checks'] for m in p['metrics'])
    manifest = '\n'.join(f'- snapshot `{s["id"]}` → `{s["path"]}`; SHA256 `{s["sha256"]}`'
                         for s in store.rows('SELECT * FROM sources') if s['id'] in source_ids)
    body = f'# หลักฐานรายงาน {slug}\n\nสร้างจาก SQLite และ snapshot ในเครื่องเมื่อ {now()}\n\n{manifest}\n\nต้นฉบับ: [[{raw_path.stem}]]\n'
    (VAULT/'wiki/sources').mkdir(parents=True, exist_ok=True)
    (VAULT/'wiki/analyses').mkdir(parents=True, exist_ok=True)
    (VAULT/'wiki/sources'/f'{source_slug}.md').write_text(page('source', 'หลักฐานรายงาน Social Audit', body,
        source_type='data', author='ระบบ MaeMorKratai', published=now()[:10], url='',
        raw_path=str(raw_path.relative_to(VAULT)), ingested=now()[:10]))
    report_path = VAULT/'wiki/analyses'/f'{slug}.md'
    report_path.write_text(page('analysis', 'สถานะ Social Media และแผนทดลอง 30 วัน', '\n'.join(lines)+'\n',
                               [source_slug], question='เพิ่มผู้ติดตามและยอดดูจากสถานะปัจจุบันอย่างไร', format='markdown'))
    rebuild_index()
    with (VAULT/'log.md').open('a') as f:
        f.write(f'\n## [{now()}] query | รายงาน Social Audit\n\nเพิ่ม [[{slug}]] จาก [[{source_slug}]]; ไม่มีการเจนหรือเผยแพร่\n')
    (ROOT/'data/latest-report.json').write_text(json.dumps({'path':str(report_path), 'generated_at':now()}))
    return {'path': str(report_path), 'generated_at': now()}
