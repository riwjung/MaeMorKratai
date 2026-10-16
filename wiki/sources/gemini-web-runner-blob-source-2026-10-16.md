---
type: source
title: "Gemini runner แก้ดาวน์โหลดภาพ blob"
aliases: []
tags: [domain/maemorkratai, automation]
created: '2026-10-16'
updated: '2026-10-16'
source_type: note
author: เจ้าของโครงการ / Codex
published: '2026-10-16'
url: 'https://developer.chrome.com/docs/extensions/reference/api/downloads'
raw_path: raw/2026-10-16-gemini-web-runner-blob-download.json
ingested: '2026-10-16'
---

# สาเหตุที่ต้องเซฟมือ

ไฟล์progressที่เจ้าของส่งออกในDownloadsแสดงTheMagician/HighPriestessถูกยืนยันSAVEDด้วยมือ ส่วนTheEmpressค้างgenerated ทุกใบerrorลิงก์ภาพต้องดาวน์โหลดเองและไม่มีdownloadId. ลิงก์ภาพเป็นblob:แต่backgroundเดิมรับเฉพาะhttps: จึงยังไม่เริ่มดาวน์โหลด ไม่พบโฟลเดอร์MaeMorKratai/cardsในDownloadsตอนตรวจ.

รุ่น1.2.0อ่านbytesภาพblobจากหน้าGemini ส่งdataURIให้Chromeดาวน์โหลด ตรวจsignature/MIMEและตั้งนามสกุลจริง. ไม่แปลง/ครอปภาพ ไม่เก็บbase64ในprogress. เพิ่มบันทึกภาพใบค้างโดยไม่เจนซ้ำ,เลือกภาพด้วยคลิกเมื่อจับคู่ไม่ได้,แสดงชื่อไฟล์จริงและเปิดตำแหน่งไฟล์. เริ่มคิวอีกครั้งจะพยายามบันทึกgeneratedเดิมก่อนใบใหม่.

ผ่านfixtureเดิม9+DOM4+blob recovery3และbackground8กรณี. ทดสอบMV3จริงในChromiumโปรไฟล์ชั่วคราวบนDOMจำลอง อ่านblob→Chromeดาวน์โหลดสำเร็จbytesตรงJPGต้นฉบับ. การทดสอบไม่ได้เจนในบัญชีเจ้าของและไม่ได้เรียกGeminiAPI. หลักฐาน [[2026-10-16-gemini-web-runner-blob-download]].

[[gemini-web-card-runner]] · [คู่มือ1.2.0](../../tools/gemini-web-runner/README_TH.md)
