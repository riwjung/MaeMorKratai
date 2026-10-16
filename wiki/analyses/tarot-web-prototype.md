---
type: analysis
title: "เว็บดูดวงแม่หมอกระต่าย — ไพ่หนึ่งใบและห้องไพ่สามใบ"
aliases: []
tags: [domain/maemorkratai, web, tarot]
created: '2026-10-15'
updated: '2026-10-16'
status: prototype
sources:
  - '[[tarot-three-card-source-2026-10-16]]'
  - '[[generated-deck-reveal-source-2026-10-15]]'
  - '[[tarot-web-delivery-source-2026-10-15]]'
  - '[[tarot-love-chat-source-2026-10-15]]'
---

# เว็บดูดวงแม่หมอกระต่าย

## ล่าสุด: ห้องไพ่สามใบ — 2026-10-16

หน้าใหม่ /reading/ เชื่อมจากลูกศรหน้าเดิม เลือกหมวด/สถานการณ์ → สับจนกดหยุด → เลือก3จาก78ในพัดหรือกริด → เปิดอดีต/ปัจจุบัน/อนาคต → ปลดล็อกคำอ่านdemo. ใช้ลายไพ่/มาสคอต/สีเดิม ภาพจริง5ใบ อีก73เป็นกรอบสำรอง ไม่เปลี่ยนภาพไพ่ผิดใบ. ([[tarot-three-card-source-2026-10-16]])

ตรวจbuild/typecheck/domain7/UI12และregressionเดิม11กลุ่มผ่าน พร้อมรองรับreducedmotion,keyboard,mobile360/390/430px. [เอกสารและโครงสร้างสำหรับSecond Brain](../../web/tarot/READING.md). ยังไม่มีAI API/ชำระเงินจริง/deploy และคำอ่านรอเจ้าของทบทวน. ([[tarot-three-card-source-2026-10-16]])

## ประวัติ: ภาพไพ่จริงและเปิดไพ่กลางจอ

ใช้ภาพJPEG5ใบที่เจ้าของเจนมาแทนSVGในเว็บ รักษาภาพเต็ม. หลังแม่หมอสับและเปิด ไพ่ลอยขึ้นกลางจอพร้อมแสงนุ่ม/ดาว และคำอ่านตามสถานะที่เลือก. ปิดด้วย×/พื้นหลัง/Escapeแล้วไพ่พลิกหลังกลับเข้ามือ;แตะไพ่ในมือ ปุ่มใต้ฉาก หรือไพ่ด้านล่างเพื่อดูใบเดิมซ้ำโดยไม่สุ่มใหม่. รายละเอียด6สถานะยังอยู่ด้านล่าง ([[generated-deck-reveal-source-2026-10-15]])

ตรวจ5ภาพตรงต้นฉบับและ30คำอ่าน,desktop/mobile,keyboard/reducedmotionผ่าน. [ผลตรวจล่าสุด](../../web/tarot/VERIFY.md). ไฟล์1.jpeg/2.jpegเป็นภาพฉากแบรนด์ ไม่รวมสำรับสุ่ม.0เครดิต ยังไม่deploy ([[generated-deck-reveal-source-2026-10-15]])

## ต้นแบบและโครงสร้างเดิม

เปิดทดลอง http://127.0.0.1:3010 เมื่อserverทำงาน. หน้าเว็บNext.jsใช้ฉาก[[halloween-2026-endcard]]แบบiframeควบคุมGSAP: แม่หมอกระพริบตาขณะรอ → เลือกสถานะความรัก → กดดูดวง → สับ/หยิบ/พลิก → ไพ่ในมือและคำอ่านตรงผลสุ่ม. รูปแบบภาพเดิมใช้ตัวละครเจ้าของและฉากSVGเพิ่ม ([[tarot-web-delivery-source-2026-10-15]])

## สำรับทดลอง

สุ่มจาก78ใบแบบไม่ซ้ำเพื่อเลือก5ใบออกแบบครั้งนี้; การดูดวงแต่ละครั้งสุ่ม1ใน5และอาจซ้ำครั้งก่อนได้ ([[tarot-web-delivery-source-2026-10-15]])

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

ทุกข้อข้างต้นอ้าง[[tarot-web-delivery-source-2026-10-15]]. ไม่ได้deploy,ไม่มีbackend/สมาชิก/การชำระเงิน/PostgreSQLในต้นแบบ,0เครดิต. แยกจากsocialdashboard3000.

## คลังความรู้และงานต่อ

[[tarot-knowledge-base]]มี78ใบ×6สถานะจากแชทเจ้าของ พร้อมmessage/บรรทัดและraw; ไม่มีชุดไพ่กลับหัวครบ จึงไม่เพิ่มเอง. เจ้าของทบทวนคำอ่านก่อนบริการจริง ([[tarot-love-chat-source-2026-10-15]])

ข้อเสนอขั้นต่อไป: ทบทวน5ภาพ/คำอ่านและจังหวะเว็บไซต์ → ออกแบบอีก73ใบ → เลือกโดเมน/แพ็กเกจHostingerจริง → ค่อยเพิ่มbackend/PostgreSQLตามฟีเจอร์ที่จำเป็น. ยังไม่อนุมัติการเผยแพร่หรือการเจนเสียเครดิต.
