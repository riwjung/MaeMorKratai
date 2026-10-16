---
type: analysis
title: ผลตรวจ Next.js และสถานะการเชื่อมจริง
aliases: []
tags:
- domain/maemorkratai
created: '2026-10-14'
updated: '2026-10-14'
status: verified-local-live-meta-pending
sources:
- '[[nextjs-validation-source-2026-10-14-211907-0700-e3302c]]'
---

# ผลตรวจ Next.js และขั้นถัดไป

เปลี่ยนหน้าเว็บหลักเป็น Next.js/React/TypeScript ที่ 127.0.0.1:3000; FastAPI/SQLite ยังเป็น backend ภายใน8787 **ยังไม่ได้ย้าย PostgreSQL**

- pytest 33 tests ผ่าน รวม pagination/idempotency/expiration/metric periods/privacy, live-verify semantics, additive media migration, optional media fallback และการแยก CSV ออกจาก Meta samples
- production build ของ Next.js ที่ติดตั้งจริงผ่าน
- browser test บนฐานทดสอบตรวจนำเข้า 10 โพสต์และ daily60วัน 300/150 (+100%) พร้อม source inspection ไม่ใช้ตัวเลขนี้ในฐานจริง
- browser บนระบบจริงตรวจหน้าเชื่อม/gallery3ภาพ/เล่นวิดีโอ/390px responsive/media ranges/proxy guards ไม่มี page errors
- production account/post/comment/metric counts = 0; connected=false; ownerยังไม่มีMetaApp; ใช้เครดิต0

หลังเจ้าของให้สิทธิ์ ต้องตรวจบัญชีจริง/coverage และเทียบ metric อย่างน้อย10โพสต์ก่อนถือว่าการเชื่อมครบเกณฑ์ ภาพและคลิปจากเจ้าของยังไม่ใช่ผลวิเคราะห์โพสต์จริงทั้งช่อง

หลักฐาน: [[nextjs-validation-source-2026-10-14-211907-0700-e3302c]]
คู่มือ: [[social-api-connection-guide]]
แนวภาพ: [[character-and-silent-animation-brief]] และ [[silent-animation-prompts]]
