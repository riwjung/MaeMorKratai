# Git ของแม่หมอกระต่าย

Repository: https://github.com/riwjung/MaeMorKratai

Branch หลัก: `main` · remote: `origin` · repository เป็น public

## ใช้งานจากโฟลเดอร์นี้

```sh
git status
git add <ไฟล์ที่ต้องการ>
git commit -m "Describe the change"
git push origin main
```

ต้นฉบับเว็บอยู่ `web/tarot/`; วิธี build และเปิดหน้าทดลองอยู่ใน README ของเว็บ ส่วนงาน runtime บนเครื่องเจ้าของอยู่ `~/AIVideoLocal/maemorkratai/` ต้องสำรองการแก้กลับเข้าโฟลเดอร์นี้ก่อน commit

## ไฟล์ที่คงไว้ในเครื่อง

`.gitignore` กัน `.env*`, กุญแจ/credentials, ฐานข้อมูล, `raw/`, source ingestion ส่วนตัว, dependency/cache/build, ZIP, วิดีโออ้างอิง/วิดีโอเรนเดอร์ และฟอนต์ระบบออกจาก Git ไฟล์เหล่านี้ไม่ถูกลบ ส่วน `.env.example` อนุญาตให้เก็บเฉพาะตัวอย่างที่ไม่มีค่าจริง

ลิงก์ในวิกิบางรายการอ้าง raw, วิดีโอ หรือ ZIP ที่มีเฉพาะเครื่องเจ้าของ จึงเปิดจาก clone สาธารณะไม่ได้ หน้าเว็บใช้ภาพและข้อมูลคำอ่านที่คัดไว้ใน `public/` กับ `lib/` และ build ได้โดยไม่ต้องนำข้อมูลส่วนตัวขึ้น repository

Git metadata ของ checkout บนเครื่องเจ้าของอยู่ `~/AIVideoLocal/maemorkratai/repositories/MaeMorKratai.git/` เพื่อลดงานเขียนบน iCloud Desktop; `.git` ในโฟลเดอร์นี้เป็นไฟล์ชี้ตำแหน่ง ใช้ `git` และ VS Code จากโฟลเดอร์นี้ตามปกติ เมื่อย้ายเครื่องให้ clone จาก GitHub ใหม่ ไม่คัดลอก `.git` pointer ข้ามเครื่อง
