"""Local delivery only; no network publishing or paid calls."""
from pathlib import Path
import json, shutil, hashlib, zipfile

W=Path(__file__).resolve().parents[1]
R=W.parent
V=Path.home()/'Desktop/AI_Video/MaeMorKratai'
H=R/'halloween-2026'
D=V/'animations/halloween-2026'
F=V.parent/'FinalResult'
date='2026-10-15'

def write(p,s):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
def copy(a,b):
    b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(a,b)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def archive(src,dst):
    with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(src.rglob('*')):
            if p.is_file() and not p.is_symlink():z.write(p,p.relative_to(src))

write(W/'VERIFY.md','''# ผลตรวจต้นแบบ — 2026-10-15

- Next.js production build, TypeScript และ static export ผ่าน
- Chromium จริง: desktop1440px และ mobile390px ไม่มีล้นแนวนอน, browser error หรือ failed request
- กดดูดวงเล่นสับไพ่/หยิบ/พลิกสำเร็จ; ภาพไพ่ในมือกับชื่อและคำอ่านตรงกัน ตรวจครบ5ใบ
- ตรวจคำอ่าน5ใบ×6สถานะ=30ช่องตรงกับ lib/cards.json ที่สกัดจากแชทต้นทาง
- แกลเลอรี5ใบ: finite GSAP timeline6วินาที600×960; HyperFrames lint ทั้ง5ผ่าน0errors0warnings
- ตรวจ modal keyboard focus cycle / Escape และ reduced motion ผ่าน
- ตรวจภาพ desktop, mobile, modal และ5card previews ด้วยสายตาแล้ว
- คลังต้นทาง78ใบไม่ซ้ำ/6สถานะต่อใบ=468ช่อง; คำอ่านยังรอเจ้าของตรวจเชิงเนื้อหาก่อนบริการจริง

หลักฐาน artifacts/web-check.json, cards-check.json, desktop.png, mobile.png, card-detail.png; QAสุ่มแบบบังคับเฉพาะbrowserทดสอบเพื่อครอบคลุม5ใบ โค้ดจริงใช้WebCryptoสุ่มตามปกติ

ยังไม่ได้ทดสอบบนบัญชีHostingerหรืออุปกรณ์Safariจริง และยังไม่ได้deploy. งานนี้0เครดิต ไม่มีbackend/บัญชีผู้ใช้/ชำระเงิน. ไพ่ภาพครบ5ใบ ส่วนอีก73ใบยังไม่ออกแบบ.
''')
write(H/'VERIFY.md','''# Verification — Halloween v3, 2026-10-15

เพิ่ม blink ที่0.8/3.9/7.5/10.7s ด้วยชั้นเปลือกตาใช้textureจากภาพเดิม. ช่วงปิดประมาณ0.14sก่อนเปิด0.065s. เก็บท่าสับสามรอบ1.1–4.34s, รวบ4.42–5.05s, ยก5.1–6.6s, พลิก6.35–7.05sและถือโชว์ถึง12sจากv2.

HyperFrames lint/runtime/layout/contrast0errors0warnings; check-v3.json. MP4:12s,1080×1920,30fps,360frames,H264,yuv420p,silent. Full decode/blackdetectผ่านไม่มีช่วงดำ. Chromiumเล่นจนended12s, Range206, iframe scrub10.8sและmobile390ผ่านไม่มีbrowser/media errors. ตรวจencoded blink/contact sheet/heroด้วยสายตาแล้ว.

หลักฐานcheck-v3.json,probe.json,playback-check.json,renders/encoded-blink-v3.png. เก็บcheck-v2.jsonกับbuild_scene_v2.pyไว้เทียบ; MP4v1/v2คงอยู่. ภาพcharacter.jpgเดิมไม่เปลี่ยน.0Higgsfieldเครดิต ไม่อัปโหลด.
''')
readme=(H/'README.md').read_text().replace('--output renders/MaeMorKratai_Halloween_2026_v2.mp4','--output renders/MaeMorKratai_Halloween_2026_v3.mp4').replace('Current export: renders/MaeMorKratai_Halloween_2026_v2.mp4.','Current export: renders/MaeMorKratai_Halloween_2026_v3.mp4.').replace('Current builder produces v2.','Current builder produces v3; build_scene_v2.py preserves v2.')
readme+='\n## V3: blinking eyes\nAdded four brief blinks using local texture eyelids, preserving the v2 shuffle/show routine. See VERIFY.md and check-v3.json. This is the scene reused by the tarot web prototype.\n'
write(H/'README.md',readme)
with (H/'STORYBOARD.md').open('a') as f:f.write('\n## V3 blink\nBlink starts0.8/3.9/7.5/10.7s; original v2 card performance remains.\n')
for name in ['build_scene.py','build_scene_v2.py','index.html','README.md','STORYBOARD.md','VERIFY.md','check-v3.json','preview.html','preview_server.py','check_playback.py','verify_encoded.sh','probe.json','playback-check.json']:
    copy(H/name,D/name)
movie='MaeMorKratai_Halloween_2026_v3.mp4'
for dest in [D/'renders'/movie,F/movie]:copy(H/'renders'/movie,dest)
for name in ['encoded-blink-v3.png','encoded-contact-sheet.jpg','encoded-hero.png']:copy(H/'renders'/name,D/'renders'/name)
copy(H/'renders/encoded-hero.png',F/'MaeMorKratai_Halloween_2026_v3_preview.png')

web=V/'web/tarot';web.mkdir(parents=True,exist_ok=True)
for name in ['app','lib','public','scripts','artifacts']:
    shutil.copytree(W/name,web/name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','deliver.py','ingest_vault.py'))
for name in ['package.json','package-lock.json','next.config.ts','tsconfig.json','next-env.d.ts','.gitignore','DESIGN.md','README.md','HOSTINGER.md','VERIFY.md']:
    copy(W/name,web/name)
# Helper QA scripts target this Mac; the app itself is portable via npm ci / npm run build.
with (web/'README.md').open('a') as f:f.write('\nQA scripts contain this Mac’s runtime paths. They are evidence/reproduction helpers; npm ci/build/dev does not depend on them. Source ingestion stays private in the runtime; clean source provenance is in the vault.\n')
archive(W/'out',V/'web/maemorkratai-hostinger-static.zip')
archive(web,V/'web/maemorkratai-tarot-source.zip')
cards=V/'animations/tarot-pilot'
shutil.copytree(R/'tarot-cards',cards,dirs_exist_ok=True)
write(cards/'README.md','''# ไพ่แม่หมอกระต่าย — 5 ใบทดลอง

The Fool / Three of Wands / The Lovers / The Hanged Man / Queen of Swords

สุ่ม5จาก78แบบไม่ซ้ำครั้งเดียวและบันทึกไว้ในrawคลังความรู้. ภาพใช้ตัวละครเดิมจากMMKT_Hallow.JPGและฉากSVGวาดเพิ่ม ไม่มีการเจนเสียเครดิต. การตีความภาพเป็นงานออกแบบใหม่ของแม่หมอกระต่าย; คำอ่านมาจากแชทเจ้าของ.

แต่ละโฟลเดอร์มีartwork.svg,preview.png,index.html,assets/gsap.min.js,DESIGN.md,meta.json,hyperframes.json. Composition600×960,6s,30fps,finite paused timelineตามHyperFrames. ดูภาพเคลื่อนไหวผ่านแกลเลอรีเว็บ127.0.0.1:3010 หรือเปิดโฟลเดอร์ด้วยHyperFrames preview. HTMLหยุดเมื่อเปิดตรงเพื่อให้engineควบคุมเวลา.

Renderเมื่อจำเป็น: hyperframes render <card-folder> --output <card>.mp4 --fps 30 --quality high
ต้นฉบับสร้างภาพ: ../../web/tarot/scripts/build_cards.py. ยังไม่สร้างภาพอีก73ใบ.
''')

evidence={'date':date,'credits_used':0,'deployed':False,'web_preview':'http://127.0.0.1:3010','knowledge_cards':78,'meaning_cells':468,'pilot_cards':[c['id'] for c in json.loads((W/'lib/cards.json').read_text())],'web_checks':json.loads((W/'artifacts/web-check.json').read_text()),'card_checks':json.loads((W/'artifacts/cards-check.json').read_text()),'video_checks':json.loads((H/'playback-check.json').read_text()),'files':{str(p.relative_to(V.parent)):sha(p) for p in [F/movie,V/'web/maemorkratai-hostinger-static.zip',V/'web/maemorkratai-tarot-source.zip']}}
raw=V/'raw/2026-10-15-tarot-web-and-blink-delivery.json'
assert not raw.exists(),'raw is append only'
write(raw,json.dumps(evidence,ensure_ascii=False,indent=2))

source='tarot-web-delivery-source-2026-10-15'
write(V/f'wiki/sources/{source}.md',f'''---
type: source
title: "หลักฐานเว็บไพ่ทดลองและ Halloween v3"
aliases: []
tags: [domain/maemorkratai, web, animation]
created: '{date}'
updated: '{date}'
source_type: note
author: เจ้าของโครงการ / Codex
published: '{date}'
url: ''
raw_path: raw/2026-10-15-tarot-web-and-blink-delivery.json
ingested: '{date}'
---

# การส่งมอบและตรวจจริง

ตามคำขอเจ้าของ เพิ่มกระพริบตาในคลิปv3 และสร้างเว็บไพ่ในart styleเดิม พร้อมไพ่ทดลอง5ใบจากแชทที่ให้มา. ใช้Next.js static export, HyperFramesและGSAP; ไม่ใช้เครดิตหรือเผยแพร่. หลักฐานhashและQA: [[2026-10-15-tarot-web-and-blink-delivery]].

เว็บผ่านproductionbuildและChromium1440/390px,ตรวจ5draws/30readings,modal/reducedmotion. คลิปผ่านdecode/blackdetect/playbackครบ12s. ผลละเอียดอยู่[web VERIFY](../../web/tarot/VERIFY.md) และ[animation VERIFY](../../animations/halloween-2026/VERIFY.md).

ขอบเขต: ข้อมูล78ใบ/468ช่อง ภาพออกแบบ5ใบ อีก73ใบยังรอ. ไม่ได้ทดสอบHostingerบัญชีจริง. คำอ่านจากแชทเจ้าของยังต้องทบทวน; ดู[[tarot-love-chat-source-2026-10-15]].
''')
write(V/'wiki/analyses/tarot-web-prototype.md',f'''---
type: analysis
title: "เว็บดูดวงแม่หมอกระต่าย — ต้นแบบไพ่ 5 ใบ"
aliases: []
tags: [domain/maemorkratai, web, tarot]
created: '{date}'
updated: '{date}'
status: prototype
sources:
  - '[[{source}]]'
  - '[[tarot-love-chat-source-2026-10-15]]'
---

# เว็บดูดวงแม่หมอกระต่าย

เปิดทดลอง http://127.0.0.1:3010 เมื่อserverทำงาน. หน้าเว็บNext.jsใช้ฉาก[[halloween-2026-endcard]]แบบiframeควบคุมGSAP: แม่หมอกระพริบตาขณะรอ → เลือกสถานะความรัก → กดดูดวง → สับ/หยิบ/พลิก → ไพ่ในมือและคำอ่านตรงผลสุ่ม. รูปแบบภาพเดิมใช้ตัวละครเจ้าของและฉากSVGเพิ่ม ([[{source}]])

## สำรับทดลอง

สุ่มจาก78ใบแบบไม่ซ้ำเพื่อเลือก5ใบออกแบบครั้งนี้; การดูดวงแต่ละครั้งสุ่ม1ใน5และอาจซ้ำครั้งก่อนได้ ([[{source}]])

- [[tarot-the-fool]] — การเริ่มต้น
- [[tarot-three-of-wands]] — การรอคอย
- [[tarot-the-lovers]] — ความรักและการเลือก
- [[tarot-the-hanged-man]] — การรอและการหยุดนิ่ง
- [[tarot-queen-of-swords]] — ขอบเขตและความเด็ดขาด

## ไฟล์และการตรวจ

- [ต้นฉบับ Next.js](../../web/tarot/README.md)
- [ผลตรวจ](../../web/tarot/VERIFY.md):5ไพ่/30คำอ่านตรงกัน,desktop/mobileผ่าน
- [ไพ่ HyperFrames + GSAP](../../animations/tarot-pilot/README.md)
- [ชุด Hostinger static](../../web/maemorkratai-hostinger-static.zip)
- [คู่มือนำขึ้น Hostinger ภายหลัง](../../web/tarot/HOSTINGER.md)

ทุกข้อข้างต้นอ้าง[[{source}]]. ไม่ได้deploy,ไม่มีbackend/สมาชิก/การชำระเงิน/PostgreSQLในต้นแบบ,0เครดิต. แยกจากsocialdashboard3000.

## คลังความรู้และงานต่อ

[[tarot-knowledge-base]]มี78ใบ×6สถานะจากแชทเจ้าของ พร้อมmessage/บรรทัดและraw; ไม่มีชุดไพ่กลับหัวครบ จึงไม่เพิ่มเอง. เจ้าของทบทวนคำอ่านก่อนบริการจริง ([[tarot-love-chat-source-2026-10-15]])

ข้อเสนอขั้นต่อไป: ทบทวน5ภาพ/คำอ่านและจังหวะเว็บไซต์ → ออกแบบอีก73ใบ → เลือกโดเมน/แพ็กเกจHostingerจริง → ค่อยเพิ่มbackend/PostgreSQLตามฟีเจอร์ที่จำเป็น. ยังไม่อนุมัติการเผยแพร่หรือการเจนเสียเครดิต.
''')
p=V/'wiki/analyses/halloween-2026-endcard.md'
s=p.read_text().replace('sources:\n',f"sources:\n  - '[[{source}]]'\n",1).replace('## ฉบับล่าสุด v2 — สับไพ่และโชว์ไพ่','## ประวัติ v2 — สับไพ่และโชว์ไพ่')
s=s.replace('# MaeMorKratai Halloween 2026\n',f'''# MaeMorKratai Halloween 2026

## ฉบับล่าสุด v3 — กระพริบตา

เพิ่มกระพริบตาที่0.8/3.9/7.5/10.7s ใช้textureจากภาพเดิมทำเปลือกตา เก็บท่าสับและถือโชว์จากv2.12s/1080×1920/30fps/เงียบ/0เครดิต. ตรวจencodedvideoและเล่นครบผ่าน ([[{source}]])

- [คลิป v3](../../../FinalResult/MaeMorKratai_Halloween_2026_v3.mp4)
- [ผลตรวจล่าสุด](../../animations/halloween-2026/VERIFY.md)
- ใช้ฉากนี้ต่อยอด[[tarot-web-prototype]]ที่127.0.0.1:3010

''',1)
write(p,s)
with (V/'index.md').open('a') as f:f.write(f'\n- [[{source}]] — หลักฐานเว็บไพ่และคลิปกระพริบตา\n')
with (V/'log.md').open('a') as f:f.write(f'\n## [{date}] implement / verify | เว็บไพ่5ใบและHalloween v3\n\nส่งมอบ[[tarot-web-prototype]]พร้อมstaticHostingerZIPและ[[halloween-2026-endcard]]v3กระพริบตา;5ภาพHyperFrames/GSAP,ตรวจ5draws/30readingsและmobileผ่าน. หลักฐาน[[{source}]];78หน้าไพ่/468ช่องคำอ่านในคลัง.0เครดิต ยังไม่deploy.\n')
with (V/'HANDOFF.md').open('a') as f:f.write('''
### ล่าสุด — เว็บไพ่ + Halloween v3, 2026-10-15

- [[halloween-2026-endcard]]: v3กระพริบตา4ครั้ง เก็บสับ/โชว์จากv2; FinalResult/MaeMorKratai_Halloween_2026_v3.mp4; preview3004
- [[tarot-web-prototype]]: Next.jsแยกบน3010; runtime~/AIVideoLocal/maemorkratai/tarot-web; portable source web/tarot; staticZIP web/maemorkratai-hostinger-static.zip ยังไม่deploy
- [[tarot-knowledge-base]]:78ใบ468ช่องจากแชทเจ้าของ;ภาพทดลอง5ใบอยู่animations/tarot-pilot อีก73ใบยังไม่ออกแบบ;คำอ่านรอเจ้าของทบทวน
- QAproductionbuild/5draws/30readings/mobile/modal/reducedmotionผ่าน;0เครดิต. SocialAPI/adminเดิมคงสถานะเดิม
''')
print(json.dumps({'delivered':True,'movie':str(F/movie),'web':str(web),'static_zip':str(V/'web/maemorkratai-hostinger-static.zip')},ensure_ascii=False))
