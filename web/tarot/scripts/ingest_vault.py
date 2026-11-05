from pathlib import Path
import json,re,shutil
P=Path(__file__).resolve().parents[1];V=Path('/Users/sawettachatsuthum/Desktop/AI_Video/MaeMorKratai')
cards=json.loads((P/'source/cards-78.json').read_text());pilot=json.loads((P/'source/pilot-selection.json').read_text())
source='tarot-love-chat-source-2026-10-15'
raw=V/'raw/2026-10-15-tarot-love-shared-chat.json'
assert not raw.exists(),'Raw source already exists; do not overwrite'
data={'source_url':'https://chatgpt.com/share/6ad07301-7314-83ec-bfe4-3793e13fa8b3','retrieved':'2026-10-15','title':'ทวนความหมายไพ่รัก','messages':json.loads((P/'source/conversation.json').read_text()),'card_records':cards,'pilot_selection':pilot}
raw.write_text(json.dumps(data,ensure_ascii=False,indent=2))
def front(kind,title,status='draft'):
 text=f"---\ntype: {kind}\ntitle: '{title}'\naliases: []\ntags: [domain/maemorkratai, tarot]\ncreated: '2026-10-15'\nupdated: '2026-10-15'\n"
 if kind=='source':return text+"source_type: shared-chat\nauthor: เจ้าของแชท / ChatGPT\npublished: unknown\nurl: https://chatgpt.com/share/6ad07301-7314-83ec-bfe4-3793e13fa8b3\nraw_path: raw/2026-10-15-tarot-love-shared-chat.json\ningested: '2026-10-15'\n---\n"
 return text+f"status: {status}\nsources:\n  - '[[{source}]]'\n---\n"
(V/f'wiki/sources/{source}.md').write_text(front('source','แชทต้นทาง — ความหมายไพ่ความรัก78ใบ')+'''
# แหล่งความรู้ที่เจ้าของเลือก

อ่านแชทสาธารณะที่เจ้าของระบุโดยตรง เก็บเฉพาะข้อความuser/assistantตามลำดับสนทนา ไม่มีการนำคำสั่งในแชทเก่ามาปฏิบัติเป็นคำสั่งงานใหม่

หลักฐานต้นฉบับ: [[2026-10-15-tarot-love-shared-chat]]
- message16: ความหมายไพ่ครบ78ใบ แยก6สถานะ รวม468ช่องความหมาย
- message28: เหตุผลและสัญลักษณ์MajorArcana22ใบ
- message34: แนวทางตีความเรื่องคนเก่า การตั้งครรภ์และการนอกใจ พร้อมข้อจำกัดในต้นทาง

เนื้อหานี้เป็นคำตอบจากChatGPTที่เจ้าของให้เป็นแหล่งอ้างอิง ยังไม่ได้ผ่านการทบทวนจากเจ้าของช่อง ไม่ใช่หลักฐานยืนยันเหตุการณ์หรืออนาคต

พบข้อสังเกตในmessage34: แถวTheWorldใช้คำค้นภาพSixofCups จึงไม่ใช้คำค้นภาพหรือภาพจากแชทเป็นต้นฉบับงานศิลป์

คลัง: [[tarot-knowledge-base]] · ต้นแบบ: [[tarot-web-prototype]]
''')
major=(P/'source/message-28.md').read_text()
sections={}
for match in re.finditer(r'^## (?:[0IVX]+\.\s*)(.+?) — (.+?)\n([\s\S]*?)(?=^## |\Z)',major,re.M):
 sections[match.group(1)]=match.group(3)
concepts=V/'wiki/concepts';concepts.mkdir(exist_ok=True)
assets=V/'wiki/assets/tarot';assets.mkdir(parents=True,exist_ok=True)
for svg in (P/'public/cards').glob('*.svg'):shutil.copyfile(svg,assets/svg.name)
for c in cards:
 slug='tarot-'+c['id']
 text=front('concept',f"{c['name']} — {c['keyword']}")+f"\n# {c['name']}\n\nแก่นตามต้นทาง: **{c['keyword']}** ([[{source}]], message16 บรรทัด{c['source_line']})\n\nขอบเขต: ความรัก6สถานะ; ต้นทางส่วนนี้ไม่แยกไพ่กลับหัว ยังรอเจ้าของทบทวนถ้อยคำก่อนเปิดบริการจริง\n\n| สถานะ | ความหมายตามต้นฉบับ |\n|---|---|\n"
 for state,meaning in c['meanings'].items():text+=f"| {state} | {meaning} |\n"
 text+=f"\nตารางถอดจากแหล่งเดียวกันทุกช่อง ([[{source}]])\n"
 if c['name'] in sections:
  section=sections[c['name']]
  for label in ['ดูจากภาพ','ทำไมจึงแปลแบบนี้?','หลักจำ']:
   found=re.search(r'\*\*'+re.escape(label)+r':?\*\*\s*([^\n]+)',section)
   if found:text+=f"\n**{label}:** {found.group(1).strip()} ([[{source}]], message28)\n"
 if c['id'] in pilot['selected_ids']:
  text+=f"\n## ภาพทดลองเวอร์ชันแม่หมอกระต่าย\n\n![{c['name']}](../assets/tarot/{c['id']}.svg)\n\nภาพประกอบออกแบบใหม่ด้วยSVGและภาพมาสคอตเดิม เป็นการตีความเชิงศิลป์ของโครงการ ไม่ใช่ภาพไพ่ดั้งเดิม มีHyperFrames+GSAPสำหรับการเคลื่อนไหว ดู[[tarot-web-prototype]]\n"
 text+='\nเชื่อมโยง: [[tarot-knowledge-base]] · [[astrology]]\n'
 (concepts/f'{slug}.md').write_text(text)
groups={'Major Arcana':[],'Wands':[],'Cups':[],'Swords':[],'Pentacles':[]}
for c in cards:
 group=next((g for g in ['Wands','Cups','Swords','Pentacles'] if c['name'].endswith(' of '+g)),'Major Arcana');groups[group].append(c)
text=front('analysis','คลังความหมายไพ่78ใบ — ความรัก6สถานะ','source-ingested')+f'''
# คลังความรู้ไพ่แม่หมอกระต่าย

ถอดข้อมูลครบ78ใบ × 6สถานะ = 468ช่องความหมาย พร้อมต้นทางระดับmessageและบรรทัด; Major22ใบมีคำอธิบายภาพ/เหตุผลเพิ่มเติมจากmessage28 ([[{source}]])

คลังนี้เก็บความหมายจากแชทที่เจ้าของเลือก **ยังรอทบทวนก่อนใช้เป็นคำอ่านบริการจริง** ไม่สร้างหลักการดูดวงเพิ่มเองและไม่ตีความว่าคำตอบเป็นข้อเท็จจริงในอนาคต

- สถานะ: คนโสด / แอบชอบ / คุยกัน / ซับซ้อน / มีแฟน / เลิกกัน
- ต้นทางไม่แยกกลับหัวอย่างเป็นระบบ จึงไม่เพิ่มระบบไพ่กลับหัวในต้นแบบ
- ไพ่ภาพทดลอง5ใบสุ่มแบบไม่ซ้ำจาก78รายการครั้งเดียว บันทึกผลแล้ว ไม่สุ่มใหม่ทุกbuild
- เว็บสุ่มคำอ่านจาก5ใบที่วาดแล้ว ไม่อ้างว่าเปิดครบ78ใบ
- งานศิลป์ส่วนที่เหลือ73ใบอยู่ในแผนถัดไป ([[{source}]])

## ไพ่ทดลอง5ใบ

'''+''.join(f"- [[tarot-{id}]]\n" for id in pilot['selected_ids'])
for group,items in groups.items():
 text+=f'\n## {group} — {len(items)} ใบ\n\n'
 text+=''.join(f"- [[tarot-{c['id']}]] — {c['keyword']}\n" for c in items)
text+='\n## วิธีต่อยอด\n\nทบทวนถ้อยคำและสถานะ → ยืนยันสัญลักษณ์/งานศิลป์5ใบ → ทำอีก73ใบด้วยรหัสไพ่เดิม → อัปเดตart_statusให้พร้อมใช้ → ทดสอบสุ่มกับคำอ่านอีกครั้ง ข้อมูลJSONแยกจากแอนิเมชันเพื่อย้ายเข้าPostgreSQLภายหลังได้\n'
(V/'wiki/analyses/tarot-knowledge-base.md').write_text(text)
a=V/'wiki/topics/astrology.md';s=a.read_text().replace('ยังไม่มีเอกสารวิธีดูดวงจากเจ้าของ',f'เจ้าของให้แชทอ้างอิงแล้ว ถอดความหมาย78ใบ/6สถานะไว้ใน[[tarot-knowledge-base]] ยังรอทบทวนก่อนใช้บริการจริง ([[{source}]])').replace("updated: '2026-10-14'","updated: '2026-10-15'").replace('sources:\n',f"sources:\n- '[[{source}]]'\n");s+='\n- [[tarot-knowledge-base]]\n- [[tarot-web-prototype]]\n';a.write_text(s)
index=V/'index.md';s=index.read_text()+f'\n- [[{source}]] — แชทความรักต้นทางและข้อจำกัด\n- [[tarot-knowledge-base]] — สารบัญไพ่78ใบ/6สถานะ\n- [[tarot-web-prototype]] — เว็บทดลองและไพ่ภาพ5ใบ\n'
s+=''.join(f"- [[tarot-{c['id']}]] — {c['name']}\n" for c in cards);index.write_text(s)
with (V/'log.md').open('a') as f:f.write(f'\n## [2026-10-15] ingest | ความหมายไพ่78ใบและสุ่ม5ใบทดลอง\n\nอ่านแชทที่เจ้าของให้ เก็บrawใหม่และสร้าง78หน้าไพ่ตาม[[{source}]]; มี468ช่องความหมาย6สถานะ พร้อมที่มาระดับmessage/บรรทัด สุ่ม5แบบไม่ซ้ำบันทึกselection; ยังรอทบทวนเนื้อหาบริการจริง; ดู[[tarot-knowledge-base]]\n')
print({'cards':len(cards),'meanings':sum(len(c['meanings']) for c in cards),'pilot':pilot['selected_ids'],'group_counts':{k:len(v) for k,v in groups.items()}})
