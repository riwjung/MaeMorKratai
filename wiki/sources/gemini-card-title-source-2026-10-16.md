---
type: source
title: "ชื่ออังกฤษบนภาพไพ่และภาพอ้างอิงตัวอักษร"
aliases: []
tags: [domain/maemorkratai, tarot, automation]
created: '2026-10-16'
updated: '2026-10-16'
source_type: note
author: เจ้าของโครงการ / Codex
published: '2026-10-16'
url: ''
raw_path: raw/2026-10-16-gemini-card-title-request.md
ingested: '2026-10-16'
---

# เพิ่มชื่ออังกฤษบนภาพไพ่

เจ้าของขอชื่อไพ่ที่ใช้รูปแบบ/ขนาดเดียวกันทั้งชุด และยืนยันภาษาอังกฤษตามชื่อเดิม ภาพที่เจนแล้วให้แนบเป็นเป้าหมายแก้เฉพาะชื่อ ใช้ผลชื่อรุ่นแรกที่เจ้าของยอมรับเป็น ref ตัวอักษรควบคู่ art style เดิม ([[2026-10-16-gemini-card-title-request]])

การนำไปใช้: [[gemini-web-card-runner]] รุ่น 1.3.0 และพรอมต์ 78 ใบ ข้อกำหนด title-v1: uppercase, narrow rounded sans-serif medium, สีครีม #FFF4E4, ความสูง capital 2.4% ของภาพ, baseline 92%, centered ไม่ย่อ/ขยายตามความยาวคำ เป็นสเปกพรอมต์ ไม่ใช่ผลวัดตัวอักษรจริง ([โค้ดสเปก](../../tools/gemini-web-runner/extension/title-workflow.js))

มีโหมดสร้างพร้อมชื่อ/เพิ่มชื่อภาพเดิม/คิวเก่า, แนบ 2–3 ภาพตามบทบาท, อนุมัติ ref ด้วยมือ, candidate จำกัดหนึ่งใบ, จับคู่ชื่อไฟล์กับ card id, คิวชื่อแยกจากเดิมและโฟลเดอร์ cards-titled/v1 แยกจาก cards ภาพนำเข้าเก็บในหน่วยความจำแท็บและต้องเลือกใหม่หลัง refresh ไม่ auto-approve จากการดาวน์โหลด ([คู่มือ](../../tools/gemini-web-runner/README_TH.md))

หลักฐานตรวจอยู่ tests/artifacts ของ runner: prompt-contract-check.json (78 ใบ), title-workflow-check.json, qa-report.json, dom-variants-check.json, blob-recovery-check.json, background-check.json และ real-extension-download-check.json เป็น offline fixtures รวม MV3 downloads จริงในโปรไฟล์ทดสอบ ไม่มีการเจนภาพในบัญชีเจ้าของ ยังต้องตรวจความสม่ำเสมอของตัวอักษรจากผล Gemini จริง
