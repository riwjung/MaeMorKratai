---
type: analysis
title: "ฉาก Halloween 2026 แม่หมอกระต่าย"
aliases: []
tags: [domain/maemorkratai, animation]
created: '2026-10-15'
updated: '2026-10-15'
status: complete
sources:
  - '[[tarot-web-delivery-source-2026-10-15]]'
  - '[[halloween-v2-shuffle-source-2026-10-15]]'
  - '[[illustrated-animation-delivery-source-2026-10-15]]'
---

# MaeMorKratai Halloween 2026

## ฉบับล่าสุด v3 — กระพริบตา

เพิ่มกระพริบตาที่0.8/3.9/7.5/10.7s ใช้textureจากภาพเดิมทำเปลือกตา เก็บท่าสับและถือโชว์จากv2.12s/1080×1920/30fps/เงียบ/0เครดิต. ตรวจencodedvideoและเล่นครบผ่าน ([[tarot-web-delivery-source-2026-10-15]])

- [คลิป v3](../../../FinalResult/MaeMorKratai_Halloween_2026_v3.mp4)
- [ผลตรวจล่าสุด](../../animations/halloween-2026/VERIFY.md)
- ใช้ฉากนี้ต่อยอด[[tarot-web-prototype]]ที่127.0.0.1:3010


## ประวัติ v2 — สับไพ่และโชว์ไพ่

เจ้าของอนุมัติภาพรวมv1และขอปรับการแสดงมือ: สับสำรับสามรอบ รวบไพ่ หยิบหนึ่งใบ พลิกหน้าไพ่แล้วถือโชว์ข้างหน้า ช่วงชื่อขึ้นยังถือไพ่ค้างอยู่ ฉากเดิมและความยาว12sคงเดิม ([[halloween-v2-shuffle-source-2026-10-15]])

- [คลิป v2](../../../FinalResult/MaeMorKratai_Halloween_2026_v2.mp4)
- [ภาพตัวอย่าง v2](../../../FinalResult/MaeMorKratai_Halloween_2026_v2_preview.png)
- [เทมเพลตปัจจุบัน](../../animations/halloween-2026/README.md)
- [ผลตรวจ v2](../../animations/halloween-2026/VERIFY.md)

ใช้ภาพเดิมแยกชั้นมือและสร้างส่วนอกที่ถูกบังในSVG;0เครดิต ตรวจการเล่นMP4ครบ12sและรอยต่อสับ/หยิบ/พลิกแล้วผ่าน ([[halloween-v2-shuffle-source-2026-10-15]])

## ประวัติฉบับ v1


ส่งออกคลิปเงียบ12วินาที 1080×1920 30fps ใช้ MMKT_Hallow.JPG เดิมครบหมวก เสื้อคลุม ใบหน้า และไพ่ในมือ ในห้องปรุงยาสีม่วง–ส้ม–ดำ มีเทียนไหว ผีขาวลอยสองตัว หม้อยาและไพ่เคลื่อนไหว ก่อนชื่อ MaeMorKratai / Halloween 2026 ปรากฏ ([[illustrated-animation-delivery-source-2026-10-15]])

เทคนิคเป็นฉาก2.5D: ชั้นภาพในพื้นที่CSS3D + SVG + GSAP เพื่อรักษาภาพวาด ไม่ใช่ตัวละครmesh3Dหมุนรอบตัวได้ ภาพอ้างอิงยังเหมือนเดิมระดับhash; ฉากและพร็อพวาดเพิ่มในโค้ด ([[illustrated-animation-delivery-source-2026-10-15]])

- [คลิปสำเร็จ](../../../FinalResult/MaeMorKratai_Halloween_2026_v1.mp4)
- [ภาพตัวอย่าง](../../../FinalResult/MaeMorKratai_Halloween_2026_preview.png)
- [เทมเพลตและวิธีแก้](../../animations/halloween-2026/README.md)
- [ผลตรวจ](../../animations/halloween-2026/VERIFY.md)
- Previewเมื่อserverเปิด: http://127.0.0.1:3004
- HyperFrames Studioเมื่อserverเปิด: http://localhost:3005/#project/halloween-2026

จังหวะ: เปิดห้อง0–2.4s → ไพ่ขยับ2.4–4.8s → ไพ่ลอย4.8–8.6s → ชื่อปรากฏ7.7–9.45s → ค้างชื่อถึง12s; ไม่มีเสียง ไม่มีการใช้เครดิตหรืออัปโหลด ([[illustrated-animation-delivery-source-2026-10-15]])

ผลตรวจ: HyperFrames lint/runtime/layout/contrast ผ่าน; ตรวจภาพจากMP4,ถอดรหัสทั้งคลิปและเล่นจนจบผ่าน; ไม่มีblack interval รายละเอียดอยู่ในVERIFY.md ([[illustrated-animation-delivery-source-2026-10-15]])

เชื่อมโยง: [[brand]] · [[illustrated-endcard]] · [[character-and-silent-animation-brief]]
