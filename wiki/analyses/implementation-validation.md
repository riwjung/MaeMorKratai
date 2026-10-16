---
type: analysis
title: ผลตรวจระบบและขั้นตอนเชื่อมบัญชีจริง
aliases: []
tags:
- domain/maemorkratai
created: '2026-10-14'
updated: '2026-10-14'
status: draft
sources:
- '[[implementation-validation-source-195143]]'
question: ระบบพร้อมแค่ไหน และยังขาดอะไรเพื่อวิเคราะห์ช่องจริง
format: markdown
---

# ผลตรวจและสิ่งที่ยังรอข้อมูล

ระบบ Python/FastAPI/SQLite/Plotly พร้อมเปิดบน http://127.0.0.1:8787 และรองรับ Meta API / CSV / รายงาน Obsidian ([[implementation-validation-source-195143]])

## ตรวจแล้ว

- pytest 25 ข้อผ่าน: pagination, resume, expired token, request budget, idempotent imports, daily/range/lifetime, source reconciliation, privacy, local request guards ([[implementation-validation-source-195143]])
- ตรวจหน้าเว็บ 1440px และ 390px ผ่าน; ไม่มี browser JavaScript errors; ทดสอบ CSV/mapping/filters/source/chart/report ด้วยฐานข้อมูลชั่วคราว ([[implementation-validation-source-195143]])
- ตัวอย่าง CSV สังเคราะห์ 10 โพสต์เทียบต้นฉบับตรง และข้อมูล 60 วันให้ 300 เทียบ 150 (+100%); เป็นข้อมูลทดสอบ ไม่ใช่ตัวเลขช่อง ([[implementation-validation-source-195143]])
- LaunchAgent `ai.maemorkratai.daily-sync` ติดตั้งแล้ว ตั้ง 08:00 และข้ามการเรียก Meta เมื่อยังไม่เลือกเพจ ([[implementation-validation-source-195143]])
- ฐานข้อมูลใช้งานจริงยังมีบัญชี 0, โพสต์ 0, คอมเมนต์ 0, metric 0 รายการ; ไม่มี fixtures แทรกเข้าไป ([[implementation-validation-source-195143]])
- ใช้เครดิต Higgsfield 0 และไม่มีการเผยแพร่/ส่งข้อความจากงานนี้ ([[implementation-validation-source-195143]])

## ยังไม่ผ่านการตรวจบัญชีจริง

Meta App, Page/IG IDs, Page tasks, professional IG และสิทธิ์แต่ละ metric ยังรอเจ้าของตั้งค่าในหน้าเชื่อมบัญชี
จึงยังไม่มีรายงานข้อสรุปสถานะช่องจากข้อมูล live และยังไม่ผ่านเกณฑ์เทียบ 10 โพสต์จริง ([[implementation-validation-source-195143]])

## เปิดและทำต่อ

ใช้ `tools/open-center.command` → เมนูเชื่อมบัญชี → เตรียม Meta App/User token/API version → เลือกเพจ → ซิงก์
หรือใช้เมนู CSV เพื่อเริ่มจากไฟล์จริง โดยตรวจช่วงวัดและการจับคู่คอลัมน์ก่อน
โค้ด/ข้อมูลในเครื่อง: `/Users/sawettachatsuthum/AIVideoLocal/maemorkratai`; สำรองเฉพาะโค้ด `tools/social-center-source.zip` ไม่มี token/DB/comment snapshots
