# แม่หมอกระต่าย — เว็บดูดวงต้นแบบ

เว็บลูกค้า Next.js แยกจาก social dashboard port3000. Preview: http://127.0.0.1:3010
งานหนัก: ~/AIVideoLocal/maemorkratai/tarot-web

## สิ่งที่ทำแล้ว
- ห้องแม่หมอจากคลิปHalloweenพร้อมกระพริบตา แปลงเป็นiframeที่ควบคุมด้วยGSAP
- เลือกสถานะความรัก6แบบ → กดดูดวง → สับ/หยิบ/พลิกไพ่ → คำอ่านตรงกับไพ่ในมือ
- สุ่มหนึ่งใบอย่างสม่ำเสมอจากสำรับทดลอง5ใบด้วยWebCryptoและrejection sampling; อาจได้ใบเดิมในคนละครั้ง
- สำรับภาพ: TheFool / ThreeofWands / TheLovers / TheHangedMan / QueenofSwords
- แกลเลอรีภาพJPEGที่เจ้าของเจนมา ใช้ภาพครบไม่ครอป มีปุ่มเล่น/หยุดการลอยเบา ๆ
- เปิดไพ่กลางจอด้วยGSAPพร้อมแสงและดาว; ปิดแล้วพลิกหลังกลับเข้ามือ; แตะไพ่ในมือ/ปุ่ม/ไพ่ด้านล่างเพื่อเปิดใบเดิมซ้ำโดยไม่สุ่ม
- คำอ่านปัจจุบันอยู่ใต้ไพ่ในdialog และรายละเอียดครบ6สถานะอยู่ด้านล่างหน้าเว็บ
- รองรับมือถือและprefers-reduced-motion ไม่มีฟอร์มข้อมูลส่วนบุคคล ไม่มีการเก็บประวัติ
- ข้อมูล78ใบ468ช่องอยู่ในObsidian แยกจากหน้าเว็บซึ่งใช้เฉพาะ5ใบ; ความหมายตามแชทเจ้าของ ยังรอทบทวนก่อนใช้งานจริง

## พัฒนา / build
ใช้Nodeตามenginesในpackage.json:
1. npm ci
2. npm run dev — 127.0.0.1:3010
3. npm run build — สร้างout/แบบstatic export
4. python3 -m http.server 3010 --bind 127.0.0.1 --directory out

tarot-webมีnode_modulesของตัวเองแล้ว (เพิ่ม three สำหรับสำรับ WebGL หน้า /reading/) ไม่ได้เชื่อมกับ runtime Social Center (`../web/node_modules`) อีก; เครื่องใหม่ใช้npm ci.

- app/page.tsx: state,สถานะความรัก,random draw,ผลไพ่
- public/scene/controller.js: handshake/idle/draw/reveal กับiframe
- public/scene/index.html: compositionจากคลิปv3
- public/cards/*.jpeg + manifest.json: ภาพไพ่จริงจากเจ้าของ5ใบและhashต้นฉบับ
- public/cards/card-back.svg: ภาพหลังไพ่ร่วมกันในมือและหน้าต่างกลางจอ
- app/CardReveal.tsx: เอฟเฟคแสง/flip/return, focus trap และreduced motion
- scripts/build_cards.py: สคริปต์SVGรุ่นทดลองเดิม; ไม่ได้ใช้ทับJPEGชุดใหม่
- lib/cards.json: คำอ่าน5ใบพร้อมmessage/บรรทัดต้นทาง
- source/: ชุดข้อมูลต้นทางในเครื่อง ไม่อยู่ในstatic export
- แก้คลิปหลักให้build_scene.pyในhalloween-2026 แล้วรันscripts/build_web_scene.pyเพื่ออัปเดตiframe
- scripts/check_reveal.py: ทดสอบUIปัจจุบันบนChromium; scripts/check_web.py/check_cards.py เป็นQAรุ่นSVGเดิม

## ขอบเขต
ต้นแบบนี้ไม่มีbackend,บัญชีผู้ใช้,การชำระเงินหรือPostgreSQL. โครงสร้างcardid/meanings/sourceแยกจากUIเพื่อย้ายเข้าฐานข้อมูลภายหลังได้. ยังไม่deploy. ตั้งnoindexไว้จนเจ้าของพร้อมเผยแพร่. ไฟล์เว็บไม่มีfontระบบที่ต้องแจกต่อ ใช้fontfallbackของอุปกรณ์.

ดูHOSTINGER.mdและVERIFY.md. ความหมายต้นทาง: https://chatgpt.com/share/6ad07301-7314-83ec-bfe4-3793e13fa8b3

QA scripts contain this Mac’s runtime paths. They are evidence/reproduction helpers; npm ci/build/dev does not depend on them. Source ingestion stays private in the runtime; clean source provenance is in the vault.

## หน้าเปิดไพ่ 3 ใบ — 2026-10-16

หน้าใหม่ `/reading/` เชื่อมจากลูกศรในหน้าแรก เลือกหมวด/สถานการณ์ → สับจนกดหยุด → เลือก 3 จาก 78 → เปิดอดีต/ปัจจุบัน/อนาคต → ปลดล็อกคำอ่านสาธิต ภาพจริง5ใบและกรอบสำรองอีก73 ไม่ใช้APIหรือเก็บเงินจริง รายละเอียดข้อจำกัด โครงสร้างข้อมูล และวิธีตรวจอยู่ใน [READING.md](READING.md).

## /reading/ — กระต่ายเคลื่อนไหวและไพ่ลอย 3D (2026-10-17)

เพิ่ม portrait mode ของฉากหน้าแรก, CSS 3D front/back/edges, การลอย/พลิกไพ่ และปุ่มหยุด/เล่นทั้งหน้า. อ่านโครงสร้าง/ข้อจำกัดใน [READING.md](READING.md) และผลตรวจใน [VERIFY.md](VERIFY.md). ภาพกับคลิปอยู่ `artifacts/reading-motion/` (ไฟล์ตรวจในเครื่อง ไม่อยู่ใน Git). ไม่เพิ่มบริการภายนอกหรือเผยแพร่เว็บ.

## Vercel

`vercel.json` ตั้ง framework เป็น Other แล้วเสิร์ฟ `out/` จาก `npm run build` ตรง ๆ เหมือน static server ในเครื่อง. ถ้าใช้ preset Next.js, Vercel ให้ไฟล์ `.html` ใน `public/` เป็น clean URL ทำให้ `/scene/index.html` และ `/card-scenes/<id>.html` ที่ฝังเป็น iframe ตอบ 404 (ฉากห้องกระต่าย มาสคอต และฉากไพ่ไม่ขึ้น). ตั้งโปรเจกต์ Vercel ให้ Root Directory เป็น `web/tarot`; push `main` แล้ว deploy ใหม่อัตโนมัติ.

ภาพหน้าไพ่ใหม่: วางต้นฉบับที่ `public/cards/<id>.jpeg` และใส่ `art` ใน `lib/reading-cards.json` แล้วรัน `python3 scripts/make_web_cards.py` เพื่อสร้าง WebP ขนาดเว็บใน `public/cards/web/`.

วิดีโอหน้าแรกสำหรับมือถือ (`public/scene/idle-loop.mp4` กระต่ายขยับระหว่างรอ และ `public/scene/draw-shuffle.mp4` สับและชูไพ่) สร้างใหม่เมื่อแก้ฉาก: เปิด static server แล้วรัน `MMKT_TEST_URL=http://127.0.0.1:3010 ../.venv/bin/python scripts/build_scene_videos.py` (ต้องมี ffmpeg; ใช้เวลาราว 10 นาที; ใส่ `idle` หรือ `draw` เพื่อทำเฉพาะไฟล์นั้น).
