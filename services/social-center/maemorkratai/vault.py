from .config import VAULT, ROOT, now
from .report import page, rebuild_index

BRIEF = '''# ข้อกำหนดที่เจ้าของอนุมัติ — แม่หมอกระต่าย

บันทึกสรุปจากคำสั่งและแผนที่เจ้าของให้ implement วันที่ 2026-10-14 (ไม่ใช่สำเนาคำสั่งแบบคำต่อคำ)

- ช่องของแฟนชื่อ แม่หมอกระต่าย; IG @maemorkratai
- Facebook URL ที่เจ้าของให้: https://www.facebook.com/share/19uKRMF1xD/?mibextid=wwXIfr
- IG URL: https://www.instagram.com/maemorkratai/
- เป้าหมาย: เพิ่มผู้ติดตามและยอดดูคอนเทนต์
- ข้อมูลรอบแรก: โพสต์/Reels/Insights/คอมเมนต์
- เจ้าของแจ้งว่ามีสิทธิ์ แต่ยังไม่แน่ใจรายละเอียด ต้องตรวจผ่าน Meta
- เริ่มบน Mac: Python + FastAPI + SQLite + Plotly; token ใน macOS Keychain
- Meta API โดยตรงผ่าน Facebook Login; Page ID/IG ID ต้องค้นหาจากบัญชีจริง
- เก็บ raw แบบเพิ่มไฟล์ใหม่ แยก lifetime กับ daily/range; ข้อมูลไม่พร้อมต้องไม่แทนด้วยศูนย์
- เปรียบเทียบ 30 วัน/30 วันก่อนหน้า และแนวโน้ม 90 วันเฉพาะข้อมูลครบ
- รายงานคอนเทนต์เด่นและแผนทดลอง 30 วัน พร้อมแหล่งอ้างอิง
- ซิงก์รายวัน 08:00 Asia/Bangkok เมื่อ Mac พร้อม และซิงก์เองได้
- ไม่รวม DMs, โพสต์อัตโนมัติ, เจนภาพ/วิดีโอ หรือเว็บลูกค้า; ไม่ใช้เครดิต Higgsfield
- ระยะถัดไป: มาสคอต/แอนิเมชันน่ารัก และเว็บดูดวงออนไลน์
'''

def initialize():
    for folder in ('raw','wiki/topics','wiki/sources','wiki/entities','wiki/concepts','wiki/analyses','wiki/assets','tools'):
        (VAULT/folder).mkdir(parents=True, exist_ok=True)
    raw = VAULT/'raw/2026-10-14-maemorkratai-project-brief.md'
    if not raw.exists():
        with raw.open('x') as f:
            f.write(BRIEF)
    docs = {
        'AGENTS.md': '''# AGENTS.md — แม่หมอกระต่าย

อ่าน CLAUDE.md → HANDOFF.md → index.md → log.md ล่าสุดก่อนทำงาน
คุยภาษาไทย โปรเจกต์นี้แยกจาก AI-Video-Project ไม่ยืมแนวภาพ Zack โดยอัตโนมัติ
โค้ด/ฐานข้อมูล/snapshot อยู่ ~/AIVideoLocal/maemorkratai/
ห้ามบันทึก token หรือคอมเมนต์รายบุคคลใน vault; ใช้ macOS Keychain
raw เพิ่มได้อย่างเดียว ทุกการเขียนวิกิต้องอัปเดต index.md และเพิ่ม log.md
ห้ามใช้เครดิต Higgsfield ก่อนตรวจ get_cost และได้รับอนุมัติ
ห้ามโพสต์ ตอบคอมเมนต์ หรือส่งข้อความโดยไม่มีคำสั่งจากเจ้าของ
ข้อมูลยังไม่เชื่อมต้องรายงานว่ารอข้อมูล ไม่เติมตัวเลขสมมติ
''',
        'CLAUDE.md': '''# กติกาคลังความรู้ แม่หมอกระต่าย

- ภาษาไทย; slug อังกฤษ kebab-case; wikilink ภายใน [[slug]]
- raw/ เพิ่มได้อย่างเดียว ห้ามแก้ ย้าย หรือลบ; ไม่แตะ .obsidian/
- wiki ทุกหน้ามี YAML: type,title,aliases,tags,created,updated และ status/sources สำหรับหน้าสังเคราะห์
- type: source เพิ่ม source_type,author,published,url,raw_path,ingested
- ทุกข้อเท็จจริงอ้าง source; ข้อสังเกต/สมมติฐานติดป้ายชัดเจน
- ทุก mutation วิกิอัปเดต index.md และเพิ่มท้าย log.md; lint ด้วย tools/wiki-lint.py
- แยก brand/content/analytics/astrology; ความรู้ดูดวงมาจากเจ้าของ ไม่แต่งวิธีหรือคำทำนายเป็นข้อเท็จจริง
- ข้อมูลส่วนบุคคลอยู่ในเครื่อง ไม่ส่งออกไปบริการภายนอก; วิกิมีเฉพาะธีมคอมเมนต์รวม
- token ใช้ Keychain เท่านั้น; ไม่บันทึกใน raw, code, logs หรือรายงาน
- งานหนักอยู่ ~/AIVideoLocal/maemorkratai/; การใช้เครดิต Higgsfield ต้องตรวจราคาและขออนุมัติ
''',
        'HANDOFF.md': f'''# สถานะส่งต่องาน — {now()[:10]}

ระบบ local social center อยู่ `{ROOT}`; เปิดด้วย tools/open-center.command
คู่มือการเชื่อมและนำเข้าอยู่ README.md; โค้ดสำรองอยู่ tools/social-center-source.zip

**สถานะบัญชี: ยังไม่ได้สร้าง/ยืนยัน Meta App หรือเชื่อม token ผ่านเซสชันนี้**
Page ID / IG ID / สิทธิ์ / Insights ยังไม่ผ่านการตรวจบัญชีจริง
ไม่มีข้อสรุปยอดผู้ติดตาม ยอดดู หรือโพสต์ที่ดีที่สุดจนกว่าจะซิงก์/นำเข้า CSV

ขั้นถัดไป: เปิดหน้าตั้งค่า → เจ้าของสร้าง Meta App/User token → เลือกเพจที่ IG ตรง @maemorkratai → ซิงก์
ไฟล์ CSV ใช้เริ่มงานระหว่างเตรียมสิทธิ์ได้ แต่ต้องตรวจ mapping และช่วงวัด
ใช้เครดิต Higgsfield: 0 ในการสร้างระบบนี้
ผลตรวจโค้ดอยู่ใน [[implementation-validation]]; รายงานใหม่เพิ่มเป็นหน้าแยก ไม่ทับ raw เดิม
''',
        'README.md': f'''# แม่หมอกระต่าย — ศูนย์ข้อมูลและ Second Brain

ดับเบิลคลิก `tools/open-center.command` หรือเปิด http://127.0.0.1:8787 หลังรันระบบ
โค้ดและข้อมูลส่วนตัว: `{ROOT}`
อ่านคู่มือเต็ม: [{ROOT}/README.md]({ROOT}/README.md)

1. เมนูเชื่อมบัญชี: เตรียม Meta App, User token และ API version จาก Meta
2. วาง token ในเว็บบนเครื่องเท่านั้น เลือกเพจและ IG ที่ถูกต้อง แล้วกดซิงก์
3. หากรอสิทธิ์ ใช้เมนูนำเข้า CSV และตรวจชื่อคอลัมน์/ช่วงวันที่
4. รายงานอยู่ wiki/analyses/ พร้อมหลักฐานใน raw/ และ source pages

เปิดโฟลเดอร์นี้เป็น vault ใน Obsidian ได้ ไม่จำเป็นต้องแก้ .obsidian/
ระบบไม่เจนสื่อ ไม่ใช้เครดิต และไม่เผยแพร่คอนเทนต์
''',
    }
    for name, body in docs.items():
        p = VAULT/name
        if not p.exists():
            p.write_text(body)
    source='maemorkratai-project-brief'
    source_path=VAULT/'wiki/sources'/f'{source}.md'
    if not source_path.exists():
        source_path.write_text(page('source','ข้อกำหนดและเป้าหมายที่เจ้าของอนุมัติ',
            f'# ข้อกำหนดโครงการ\n\nเป้าหมายเพิ่มผู้ติดตามและยอดดู เริ่มจากข้อมูลช่องบน Mac\n\nต้นฉบับสรุป: [[{raw.stem}]]\n',
            source_type='note',author='เจ้าของโครงการ',published='2026-10-14',url='',raw_path=str(raw.relative_to(VAULT)),ingested=now()[:10]))
    topics={
        'brand':('แบรนด์แม่หมอกระต่าย','ช่องชื่อแม่หมอกระต่าย IG @maemorkratai ต้องการแนวแอนิเมชันน่ารัก\n\nยังรอโลโก้ สีแบรนด์ และมาสคอตที่เจ้าของเลือก'),
        'content':('คอนเทนต์และการทดลอง','เป้าหมายเพิ่มผู้ติดตามและยอดดู\n\n**สมมติฐาน:** ใช้ผลวิเคราะห์คอนเทนต์เดิมเลือกคู่ทดลอง ไม่รับรองว่าจะเพิ่มยอดได้'),
        'analytics':('ข้อมูลและการวิเคราะห์','เก็บโพสต์/Reels/Insights/คอมเมนต์ แยกแพลตฟอร์มและช่วงวัด\n\nยังไม่เชื่อมข้อมูลจริง ดู [[implementation-validation]] สำหรับผลตรวจระบบ'),
        'astrology':('คลังความรู้ดูดวง','ยังไม่มีเอกสารวิธีดูดวงจากเจ้าของ\n\nเก็บเอกสารที่เจ้าของให้เป็น source ก่อนสังเคราะห์ ไม่สร้างคำทำนายเป็นความรู้ยืนยัน'),
    }
    for slug,(title,body) in topics.items():
        p=VAULT/'wiki/topics'/f'{slug}.md'
        if not p.exists():
            p.write_text(page('topic',title,f'# {title}\n\n{body} ([[{source}]])\n',[source]))
    p=VAULT/'wiki/overview.md'
    if not p.exists():
        p.write_text(page('overview','แม่หมอกระต่าย — ภาพรวม',
            f'# แม่หมอกระต่าย\n\nศูนย์คอนเทนต์และคลังความรู้ของช่อง เป้าหมายเพิ่มผู้ติดตามและยอดดู ([[{source}]])\n\n'
            '- [[brand]]\n- [[content]]\n- [[analytics]]\n- [[astrology]]\n',[source]))
    rebuild_index()
    log=VAULT/'log.md'
    if not log.exists():
        log.write_text(f'# บันทึกโครงการ\n\n## [{now()}] schema | เริ่ม vault\n\n'
                       f'สร้างคลังแยกตาม [[{source}]] ยังไม่เชื่อมบัญชีหรือใช้เครดิต\n')
