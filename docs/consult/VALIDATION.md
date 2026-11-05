# ผลตรวจชุดส่ง consult — 5 พฤศจิกายน 2026

ตรวจใน isolated checkout จาก `origin/main` เพื่อจัดชุด source โดยไม่ stage งานอื่นของ vault. Runtime ของเครื่องตรวจ: Node.js 24.21.0 / Python 3.14.7.

| งานตรวจ | ผล |
|---|---|
| `web/tarot`: `npm ci` แล้ว `npm run build` | ผ่าน; สร้าง static `/` และ `/reading` โดยไม่ใช้ API key |
| `web/workshop-standalone`: `npm ci`, `npm test`, `npm run typecheck` | ผ่าน 5 tests รวม Postgres RPC isolation/idempotency/audio/withdrawal, CSRF และ review rules |
| `services/social-center`: pytest จาก source snapshot | ผ่าน 33 tests; มี Starlette/httpx deprecation warning 1 รายการ |
| ลิงก์ relative ใน README/CONTRIBUTING/docs/consult | ผ่าน; ปลายทางมีในชุด Git |
| `git diff --cached --check` | ผ่าน |
| `tools/check_public_release.py` กับ staged blobs | ใช้ตรวจ blocked files/credential patterns/อีเมลส่วนตัว; ผ่านก่อน commit. มี exception เฉพาะ synthetic URL rejection fixture ที่ตรวจแล้ว |

นี่เป็นการตรวจซอร์สสำหรับ consult. ไม่ได้รันทดสอบ hosted workshop กับฐานจริง, อ่านหรือรับรองคำตอบส่วนตัว, render คลิปจาก clone, load test, เปลี่ยน schema หรือเรียก paid generation provider. หลักฐาน QA ของเว็บที่เผยแพร่ก่อนหน้านี้อยู่ใน `web/tarot/*CHECK*.json` ตามวันที่ของไฟล์นั้น.

เว็บหลักล่าสุดเป็น static export ที่ deploy จาก CLI snapshot. ชุด consult นี้ไม่ได้ตั้งค่า Vercel Git integration ใหม่. รายงานนี้ไม่ยืนยันสิทธิ์บัญชีของผู้รับ Git และไม่ใช่การตรวจความปลอดภัยทั้งประวัติ repository.
