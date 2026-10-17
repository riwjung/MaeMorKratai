---
type: source
title: "ตั้งค่า Pro และซ่อมกรอบ/คิ้วบนภาพไพ่เดิม"
aliases: []
tags: [domain/maemorkratai, tarot, automation]
created: '2026-10-17'
updated: '2026-10-17'
source_type: note
author: เจ้าของโครงการ / Codex
published: '2026-10-17'
url: 'https://support.google.com/gemini/answer/14286560?hl=en'
raw_path: raw/2026-10-17-gemini-pro-card-repair.md
ingested: '2026-10-17'
---

# Pro และซ่อมเฉพาะตำหนิ

เจ้าของขอ Pro เป็นค่าเริ่มต้น และต้องการแก้ภาพที่มีตำหนิโดยรักษาภาพสวยเดิมไว้ ภาพตัวอย่างที่เปิดดู: The Emperor มีกรอบขาดใต้ชื่อ; The Chariot มีคิ้วข้างเดียว ([[2026-10-17-gemini-pro-card-repair]])

runner 1.4.0 เลือกและตรวจ Pro ใน model picker ก่อนทุกงานและก่อนส่ง ถ้าไม่พบ/ยืนยันไม่ได้ให้หยุด ไม่ fallback หรือซื้อแพ็กเกจ เพิ่มโหมดซ่อมภาพเดิมซึ่งมีตัวเลือกกรอบ/คิ้ว/ทั้งสอง/คำอธิบายอื่น, แนบภาพเดิมเป็นฐาน, รักษาชื่อและองค์ประกอบนอกตำหนิ คิวซ่อมและโฟลเดอร์ cards-repaired/v1 แยกจากภาพเดิม; การซ่อมซ้ำหลัง downloaded เป็น attempt ใหม่ที่ผู้ใช้สั่งเอง เก็บ history และไฟล์เก่า ([โค้ด](../../tools/gemini-web-runner/extension/content.js), [คู่มือ](../../tools/gemini-web-runner/README_TH.md))

เลือก Pro ในแชทไม่ได้ยืนยันว่า image engine เป็น Nano Banana Pro เสมอ: เอกสาร Google ระบุ Pro/Flash สำหรับ Nano Banana 2 ส่วน Nano Banana Pro ใช้ More → Redo with Pro ตามสิทธิ์บัญชี ตัวช่วยยังไม่กดขั้น Redo เพิ่มเอง ([Google Help](https://support.google.com/gemini/answer/14286560?hl=en), ตรวจ 2026-10-17)

พรอมต์สร้างใหม่เพิ่มกรอบครบทั้งสี่ด้านและคิ้วเป็นคู่เมื่อมีคิ้ว แต่การดาวน์โหลดสำเร็จเป็น owner-review-required ยังไม่มีตัวตรวจ pixels อัตโนมัติ และไม่มีการเจนซ้ำวนเอง ผลการทดสอบใช้ fixture: tests/artifacts/pro-repair-check.json, รายงาน regression เดิม และ real-extension-download-check.json ไม่ยืนยัน live Gemini DOM/คุณภาพภาพใหม่ และไม่ได้สร้างภาพจริงในบัญชีเจ้าของในงานนี้

[[gemini-web-card-runner]]
