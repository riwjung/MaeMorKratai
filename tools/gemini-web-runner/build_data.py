"""Rebuild title-v1 prompts + extension data without generating images.
Work in runtime; --prompts-dir chooses a staged copy or the vault source.
"""
from pathlib import Path
import argparse, json, shutil, hashlib, re
P=Path(__file__).resolve().parent
V=Path.home()/'Desktop/AI_Video/MaeMorKratai'
a=argparse.ArgumentParser();a.add_argument('--prompts-dir',type=Path,default=V/'animations/tarot-pilot/prompts-78');args=a.parse_args();S=args.prompts_dir
m=json.loads((S/'manifest.json').read_text())
legacy=(S/'LEGACY_STYLE_LOCK.txt').read_text().strip()
spec=re.search(r'const spec = `([\s\S]+?)`;', (P/'extension/title-workflow.js').read_text()).group(1)
quality=re.search(r'const quality = `([\s\S]+?)`;', (P/'extension/title-workflow.js').read_text()).group(1)
style=legacy.replace("If an approved card is also attached, use that second image only to match the deck's frame, spacing, palette and level of detail.", "Use MMKT_APPROVED_TITLE_REF, when attached, only for consistent typography; do not copy its scene or card identity.")
style=style.replace('Leave the bottom 12% visually quiet so the website can add a title later. No words, letters, printed numbers, logos, signatures or watermarks.', 'Reserve the bottom 12% for the card title specified below. Keep other artwork out of this title band.')+'\n\n'+spec+'\n\n'+quality
(S/'STYLE_LOCK.txt').write_text(style+'\n');(S/'cards').mkdir(exist_ok=True)
rows=[];sections=[]
for c in m['cards']:
 scene='\n\nCARD SCENE: '+c['name'].upper()+'\n\n'+c['scene']
 prompt=style+scene+'\n\nCARD TITLE: '+c['name'].upper()+'\nReturn one finished card in the original reference art style with this exact title.\n'
 old=legacy+scene+'\n\nReturn one finished card illustration in the attached reference style. Do not add the card name or a number to the artwork.\n'
 (S/c['prompt_file']).write_text(prompt)
 rows.append({k:c[k] for k in ['sequence','id','name','existing_generated_image']}|{'prompt':prompt,'legacyPrompt':old})
 sections.append(f"## {c['sequence']:02d}. {c['name']} — {c['id']}\n\n```text\nCARD SCENE: {c['name'].upper()}\n{c['scene']}\n\nCARD TITLE: {c['name'].upper()}\n```\n")
assert len(rows)==len({r['id'] for r in rows})==78
m['title_system']={'version':'title-v1','language':'English uppercase','capital_height_canvas':0.024,'baseline_canvas':0.92,'approved_reference_required_after_candidate':True}
(S/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
(S/'GEMINI_PROMPTS_78.md').write_text('# พรอมต์ Gemini ไพ่แม่หมอกระต่าย 78 ใบ — พร้อมชื่อ\n\nแนบ IMG_5392.JPG ทุกครั้ง; หลังอนุมัติต้นแบบชื่อ ให้แนบภาพนั้นด้วยชื่อ MMKT_APPROVED_TITLE_REF เป็น reference ตัวอักษรทุกใบ ใช้ cards/*.txt เพื่อคัดลอกพรอมต์ครบชุด หรือใช้ส่วนกลางด้านล่างต่อด้วยฉากและชื่อแต่ละใบ\n\nสำหรับเติมชื่อภาพเดิม ใช้โหมดเพิ่มชื่อภาพเดิมใน runner เพื่อแนบภาพเป้าหมายและสั่งแก้เฉพาะตัวหนังสือ ไม่ใช้พรอมต์สร้างฉากใหม่\n\n## สไตล์กลาง\n\n```text\n'+style+'\n```\n\n'+'\n'.join(sections))
(P/'extension/deck-data.js').write_text('globalThis.MMKT_DECK = '+json.dumps(rows,ensure_ascii=False)+';\n')
ref=P/'extension/assets/IMG_5392.JPG'
if not ref.exists():shutil.copy2(V/'wiki/Images/IMG_5392.JPG',ref)
(P/'reference.json').write_text(json.dumps({'reference_image':'wiki/Images/IMG_5392.JPG','sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),'cards':78,'title_system':'title-v1','approved_title_reference':'owner imports and approves in UI; not bundled','imported_images':'memory only; reselect after refresh'},indent=2)+'\n')
print('Built 78 title prompts + preserved legacy prompts; no generation requests')
