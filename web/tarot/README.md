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

บนเครื่องนี้node_modulesเชื่อมกับruntimeเดิมเพื่อไม่ติดตั้งซ้ำ ZIPต้นฉบับไม่รวมsymlink; เครื่องใหม่ใช้npm ci.

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
