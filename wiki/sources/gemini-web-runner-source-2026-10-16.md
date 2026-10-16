---
type: source
title: "ตัวช่วยเจนไพ่ผ่านหน้าเว็บ Gemini"
aliases: []
tags: [domain/maemorkratai, tarot, automation]
created: '2026-10-16'
updated: '2026-10-16'
source_type: note
author: เจ้าของโครงการ / Codex
published: '2026-10-16'
url: 'https://support.google.com/gemini/answer/14286560?hl=en'
raw_path: raw/2026-10-16-gemini-web-card-runner.json
ingested: '2026-10-16'
---

# คำขอและผลส่งมอบ

เจ้าของขอตัวช่วยอัตโนมัติในแชทGeminiที่ล็อกอินอยู่ พร้อมแนบIMG_5392.JPGทุกครั้ง และไม่ใช้APIเสียเงิน. ส่งมอบส่วนขยายChromeManifestV3รวม78พรอมต์/JPGต้นฉบับ โดยใช้เฉพาะUIแชทc1051ca2e5090320. ค่าเริ่มต้นข้าม5ภาพเดิมและทำครั้งละ1ใบ.

ส่งทีละใบ รอภาพใหม่และดาวน์โหลดเสร็จก่อนถัดไป;หยุดเมื่อquota/error/องค์ประกอบหน้าไม่ชัดเจน;เก็บงานค้างโดยไม่ส่งซ้ำหลังreload. เจ้าของยืนยันSAVED/UNSENT/RETRYได้. ไม่กดอัปเกรด ไม่เรียกAPI ไม่อ่าน.env.

ทดสอบ8กรณีผ่านในDOMจำลองและ5กรณีserviceworkerด้วยmock ChromeAPI;0browsererrors. ยังไม่ทดสอบเจนในบัญชีเจ้าของจริง จึงต้องติดตั้งและเริ่ม1ใบก่อน. ไม่ได้รับประกันselectorsหน้าGeminiหรือจำนวนภาพที่โควตายอมให้สร้าง.

[คู่มือและติดตั้ง](../../tools/gemini-web-runner/README_TH.md) · [ZIP](../../tools/MaeMorKratai_Gemini_Web_Runner.zip) · [[gemini-web-card-runner]]

หลักฐาน/hash: [[2026-10-16-gemini-web-card-runner]]. เอกสารวิธีใช้Gemini/Chromeที่ใช้พัฒนามีURLในraw ไม่ใช่หลักฐานว่าบัญชีเจ้าของทำงานจริงผ่านแล้ว.0ภาพเจน/0APIcalls.
