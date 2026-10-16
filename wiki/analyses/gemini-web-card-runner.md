---
type: analysis
title: "เจนไพ่ในแชท Gemini แบบอัตโนมัติ"
aliases: []
tags: [domain/maemorkratai, tarot, automation]
created: '2026-10-16'
updated: '2026-10-16'
status: prototype
sources:
  - '[[gemini-web-runner-blob-source-2026-10-16]]'
  - '[[gemini-web-runner-dom-source-2026-10-16]]'
  - '[[gemini-web-runner-recovery-source-2026-10-16]]'
  - '[[gemini-web-runner-source-2026-10-16]]'
  - '[[tarot-gemini-prompts-source-2026-10-15]]'
---

# เจนไพ่ในแชท Gemini

ใช้[ส่วนขยายChromeในเครื่อง](../../tools/gemini-web-runner/README_TH.md)ช่วยแนบภาพต้นฉบับและส่งพรอมต์จาก[[tarot-knowledge-base]]ทีละใบในแชทที่เจ้าของเลือก ไม่ใช้.env.localหรือGeminiAPI. การสร้างภาพอยู่ภายใต้โควตาและแพ็กเกจเว็บของเจ้าของ ไม่รับประกันว่าฟรีหรือครบ78ใบได้ในวันเดียว ([[gemini-web-runner-source-2026-10-16]])

ติดตั้งผ่านchrome://extensions → Developer mode → Load unpacked → เลือกtools/gemini-web-runner/extension → รีเฟรชแชท → เริ่มอัตโนมัติ1ใบ. เมื่อผ่านแล้วจึงเพิ่มจำนวน. ตั้งค่าเริ่มต้นข้าม5ใบที่มีภาพแล้ว. พักหลังใบปัจจุบันและบันทึกสถานะได้ ([[gemini-web-runner-source-2026-10-16]])

ระบบแนบIMG_5392.JPGใหม่ทุกคำขอ รอภาพใหม่/ดาวน์โหลดก่อนเริ่มใบถัดไป. ไฟล์อยู่โฟลเดอร์ดาวน์โหลดChrome/MaeMorKratai/cards. เป็นภาพตามURLที่เว็บแสดง อาจไม่ใช่ขนาดเต็มสูงสุด;ใช้Download full sizeของGeminiเมื่อต้องการ. ยังไม่เพิ่มภาพในเว็บ[[tarot-web-prototype]]อัตโนมัติ ([[gemini-web-runner-source-2026-10-16]])

เมื่อquotaหมดจะหยุด ไม่กดซ้ำ. หลังreloadจะไม่ส่งงานค้างอีกเอง เจ้าของตรวจแล้วเลือกSAVED/UNSENT/RETRYตามคู่มือ. ตรวจด้วยChromium/DOMจำลอง8กรณีและserviceworker5กรณีผ่าน;ยังไม่ได้กดเจนจริงในบัญชีเจ้าของ จึงต้องตรวจ1ใบจริงหลังติดตั้ง ([[gemini-web-runner-source-2026-10-16]])

[ดาวน์โหลดZIP](../../tools/MaeMorKratai_Gemini_Web_Runner.zip) · [ผลทดสอบจำลอง](../../tools/gemini-web-runner/tests/artifacts/qa-report.json)

## รุ่น1.0.1 เมื่อกดเริ่มแล้วมีใบค้าง

เจ้าของพบguardมีใบค้างTheMagician;ยังไม่ทราบสาเหตุของครั้งแรก. รุ่นนี้แสดงขั้นค้างและรักษาสาเหตุเดิมไว้. ถ้าตรวจแล้วว่าไม่เคยส่งและช่องพิมพ์/ภาพแนบว่าง ให้ยืนยันใบค้าง→UNSENT→เตรียมใบถัดไป. หากส่งแล้วรอภาพ/ดาวน์โหลดแล้วใช้SAVED ไม่ใช้UNSENT. อัปเดตextensionด้วยReloadแล้วรีเฟรชแชทเมื่อไม่ได้กำลังส่ง. ตรวจregression9กรณีผ่าน ยังไม่เจนจริงในบัญชีเจ้าของ ([[gemini-web-runner-recovery-source-2026-10-16]])

## รุ่น1.1.0 ตามภาพช่องพิมพ์0

ภาพผู้ใช้ยืนยันdetectorหาช่องAskGeminiไม่พบและUNSENTล้มเหลวตาม. เพิ่มค้นหลายรูปแบบและปุ่มเลือกช่องพิมพ์;รองรับfileinputที่สร้างหลัง+และpasteภาพ. Reloadextension/รีเฟรชGemini→เลือกช่องพิมพ์→คลิกAskGemini→หากไม่เคยส่งและช่องว่างให้กดยังไม่ได้ส่ง–ปลดใบค้าง→เริ่ม1ใบ. หากเคยส่งแล้วให้จัดการSAVEDตามจริง. ทดสอบจำลอง13กรณีผ่าน ยังไม่ยืนยันบัญชีจริงหลังแก้ ([[gemini-web-runner-dom-source-2026-10-16]])

## รุ่น1.2.0 บันทึกภาพblobอัตโนมัติ

progressจริงยืนยันสาเหตุดาวน์โหลดล้มเหลว: ลิงก์blobถูกปฏิเสธก่อนสร้างdownloadId. แก้ให้อ่านbytesจากหน้าแล้วChromeบันทึกตามชนิดจริง. หลังReloadextension/refreshGeminiกดบันทึกภาพใบค้างเพื่อเก็บTheEmpressที่เจนแล้ว;ถ้าจับคู่ไม่ได้ให้คลิกภาพนั้นและยืนยัน ไม่ต้องเจนใหม่. เปิดตำแหน่งไฟล์จากpathจริงได้. เมื่อเริ่มbatchระบบจะเก็บgeneratedเดิมก่อน แล้วทำใบถัดไป ([[gemini-web-runner-blob-source-2026-10-16]])

ทดสอบดาวน์โหลดblobด้วยส่วนขยายจริงในChromiumบนหน้าDOMจำลองแล้วไฟล์bytesตรง. ไม่ทดสอบgenบัญชีเจ้าของ/ไม่เสียAPI. โฟลเดอร์MaeMorKratai/cardsเกิดเมื่อดาวน์โหลดสำเร็จครั้งแรกใต้DownloadsจริงของChrome นามสกุล.jpg/.pngตามMIME ไม่บังคับ.pngทุกภาพ ([[gemini-web-runner-blob-source-2026-10-16]])
