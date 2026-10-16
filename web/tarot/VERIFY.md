# ผลตรวจต้นแบบ SVG รุ่นแรก — 2026-10-15

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


## รอบภาพที่เจ้าของเจน + เอฟเฟคเปิดไพ่ — 2026-10-15

- Build production/TypeScriptผ่านในรุ่นส่งมอบ; หยุดidleฉากขณะมีoverlayเพื่อลดภาระการวาดภาพ
- ภาพJPEG5ใบคงbytesตรงต้นฉบับ1632×2624; manifestระบุชื่อเดิมและSHA256
- ตรวจภาพdesktop1440×1000/mobile390×844ด้วยตาแล้ว: ไพ่ครบไม่ครอป คำอ่านอยู่ใต้ไพ่ และรายละเอียด6สถานะอยู่ด้านล่าง
- ปิดแล้วพลิกกลับ,เปิดซ้ำโดยไม่สุ่ม,กดไพ่ในมือ/ไพ่ด้านล่าง,focus trap,Escape/backdrop,shortmobile/reducedmotion: ผลอัตโนมัติรอบล่าสุดอยู่ artifacts/reveal/reveal-check.json (อ้างpassedในไฟล์)
- สคริปต์ปัจจุบัน: scripts/check_reveal.py; รูปและQAเก่าในartifactsรากเป็นรุ่นก่อนหน้า
- ไม่มีการเจนภาพเพิ่มเติมหรือใช้เครดิต ไม่deploy. ภาพ1.jpeg/2.jpegเป็นฉากแบรนด์ ไม่รวมเป็นไพ่สุ่ม

ผลรอบล่าสุด: reveal-check.jsonผ่าน11กลุ่มตรวจ,0browsererrors/404s/externalrequests;ตรวจ5ไพ่30คำอ่าน. rapid-check.jsonผ่านการปิดก่อนเปิดเสร็จและเปลี่ยนreducedmotionขณะปิดโดยยังเลื่อนไปคำอ่านถูกต้อง. ดูภาพที่artifacts/reveal/.


## หน้าไพ่สามใบ — 2026-10-16

- Production build และ npm run typecheck ผ่าน; static route `/reading/` พร้อมหน้าเดิม `/`.
- Domain suite `node scripts/check_reading.cjs` ผ่าน7กลุ่ม:78รหัส/468ความหมาย/ภาพจริง5ใบ,500รอบสุ่มไม่ซ้ำหรือหาย,rejection sampling,state guard/rapid duplicate/ไม่เกิน3ใบ,คืนไพ่/แก้คำถาม/กันcallbackค้าง,ตรวจทุกความหมายรัก6สถานะตามตำแหน่ง,เปลี่ยนใบ2/3หรือสถานะแล้วsummaryเปลี่ยน.
- Chromium UI ผ่าน12กลุ่ม: ลูกศรจากหน้าเดิม,สับจริงเกิน60วินาที,หยุดโดยคงposeแล้วรวม/กาง,78ใบและกริดร่วม,เลือก/คืน/เรียง/เปิด/ปลดล็อกตรงชุดเดิม,รีเฟรชล้างคำถาม,มือถือ360/390/430พร้อมtouch/reducedmotion,keyboard/resize,เปลี่ยนreducedmotionขณะสับ,GSAPโหลดไม่ได้ยังเลือกได้.
- ไม่พบpageerror,HTTPerrorหรือexternalrequestในUI suite. ใช้browser contextทดสอบแยก;การจำลองลากทดสอบguardผ่านpointer events ไม่ใช่การวัดสัมผัสบนโทรศัพท์จริง.
- Regressionหน้าไพ่เดิมผ่าน11กลุ่มตาม artifacts/reveal-three-card-regression/reveal-check.json.
- ตรวจภาพUIด้วยตาหลังแก้ช่องไพ่ว่างและปรับขนาดโต๊ะ/ปุ่มมือถือแล้ว. หลักฐานล่าสุด artifacts/reading/ui-check.json,domain-check.txt และภาพ12ไฟล์.
- ภาพพร้อม5ใบ อีก73ใช้กรอบพร้อมชื่อ. คำอ่านรักจากแชทเดิมยังรอเจ้าของทบทวน;บทสรุปเชื่อมเวลาเป็นdemo หมวดอื่นรอข้อมูล. ไม่มีAI API,การเก็บเงินจริงหรือdeploy.
- ยังไม่ตรวจSafariบนอุปกรณ์จริงหรือHostinger;ไม่มีการวัดFPSบนโทรศัพท์จริง.
