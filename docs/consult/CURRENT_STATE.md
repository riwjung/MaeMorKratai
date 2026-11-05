# สถานะที่ตรวจได้ ณ 5 พฤศจิกายน 2026

## 1. เว็บลูกค้า: ออนไลน์แล้ว

- URL: https://mae-mor-kratai.vercel.app/ · `web/tarot`
- Next.js 16.4.2 / React 19 / TypeScript, static export บน Vercel; GSAP และ Three.js สำหรับฉาก/การเลือกไพ่
- หน้าแรกสุ่มไพ่รายวัน 78 ใบด้วย WebCrypto. แสดงภาพรวม งาน เงิน รักตามสถานะ ข้อความแม่หมอ สี และคำยืนยันจากแชทที่เจ้าของแจ้งว่าแฟนตรวจแล้วในวันที่ 5 พ.ย.
- ข้อมูลเผยแพร่จริง: `lib/daily-cards.json`; ภาพใช้ `lib/reading-cards.json` + `public/cards/v3/manifest.json`. ไม่เรียก LLM เพื่อเขียนรายวันใหม่
- ภาพพร้อม 74/78; ขาด Six of Wands, Nine of Wands, Page of Pentacles, King of Pentacles. Major Arcana 22 ใบไม่มีข้อความรักซับซ้อนในต้นทาง จึงแจ้งว่ายังไม่มีคำอ่าน
- ปุ่มเปิดไพ่เป็นแคปซูลสีเหลืองทองใต้ฉาก; กรอบใช้ขนาดภาพจริง. The Magician สัดส่วนต่างจากใบอื่น ดู [รายงาน](../../web/tarot/CARD_DIMENSIONS.md)
- `/reading/` เปิดประสบการณ์เลือกอดีต–ปัจจุบัน–อนาคต 3 ใบ เป็น **demo**. `lib/reading.ts` ใช้ความหมายรักเดิม และหมวดอื่นยังมีข้อความรอความรู้. ไม่ใช่ engine ที่อ่านคำถามอิสระครบทุกหมวด และยังไม่มีใบขยายที่ 4 ในเว็บลูกค้า
- ยังไม่มีระบบสมาชิก/ประวัติลูกค้า/คำสั่งซื้อ/เครดิต/การรับเงินจริงในเว็บนี้

หลักฐาน: [daily QA 78 ใบ](../../web/tarot/DAILY_LAUNCH_CHECK_20261105.json), [UX QA](../../web/tarot/UX_CHECK_20261105.json). Deployment ล่าสุดก่อนชุด consult: `dpl_HGeZhAmQdZw2riVWFSBEpryDf73Z` (5 พ.ย.), Vercel alias ข้างต้น. ตรวจสีปุ่มบน WebKit มือถือหลัง deploy แล้ว. ไม่เท่ากับการ load test หรือทดสอบมือถือจริงทุกเครื่อง.

## 2. ห้องทดลอง: ออนไลน์แล้ว

- URL: https://maemorkratai-workshop.vercel.app/ · `web/workshop-standalone`
- Next.js full stack + Supabase Auth/Postgres/private Storage. Login ด้วยอีเมลและรหัสผ่าน; มี active membership และ role `owner` / `reader`
- catalog 60 เคส/4 หมวด; baseline 3 ใบ → seal → followup ใบที่ 4 → ส่งทบทวน พร้อมข้อความ/เสียงและประวัติ revision
- อ่านที่มาของข้อมูลจาก `lib/cases.json`; ตารางจริงจาก migrations 001–003. `/review` ให้ owner ตรวจข้อความ/รับรอง/เก็บประวัติใน private bucket แยก
- หลักฐาน intake ล่าสุดในแผนเดิม (26 ต.ค.): owner ส่ง 60/60 เคส; เตรียม development 40 / holdout 20 และถอดเสียง 6 ไฟล์ในเครื่องแล้ว. **รอบ Git consult นี้ไม่ได้อ่านคำตอบจริงหรือเช็กจำนวน approved ล่าสุด** จึงต้องให้ owner ตรวจสถานะก่อนทำ engine
- การรับรองตัวอย่างเคสใน `/review` ไม่ได้สร้าง generalized card rules หรือ publish คำตอบสู่ลูกค้าเอง
- อนุมัติคำอ่านรายวันวันที่ 5 พ.ย. ครอบคลุมแชทรายวัน ไม่ใช่การอนุมัติคลัง 3+1 ใบทั้งหมด

หลักฐาน: [REVIEW_IMPLEMENTATION](../../web/workshop-standalone/REVIEW_IMPLEMENTATION.md), [VALIDATION](../../web/workshop-standalone/VALIDATION.md), [แผน intake](../../backend/INTAKE_PREPARATION.md). คำตอบและเสียงจริงไม่อยู่ใน repo.

## 3. Dashboard และคลิป: มีส่วนประกอบในเครื่อง

- `services/social-center`: Next.js UI port 3000 + FastAPI port 8787 + SQLite; อ่าน Meta API/CSV เพื่อดูข้อมูลช่องและทำรายงาน. Token ใช้ macOS Keychain. เป็น local application; ยังไม่ใช่ admin บนเว็บที่รองรับหลายคน
- ตัวอย่าง pipeline คลิปมี Blender, ffmpeg, Rhubarb, HyperFrames/GSAP และเสียง Sai ที่เจ้าของเลือก. ล่าสุด Expression Cut v1 เป็นคลิป 61 วินาที 1080×1920/30fps; source อ้างอิงอยู่ `animations/TheFools_Type/funmaxxing-expression-cut-v1`
- ยังไม่มี API สั่งงานคลิป, job queue, cloud render worker, dashboard ติดตามต้นทุน หรือ web generation service. ปุ่ม generate บนเว็บและการโพสต์สู่ช่องยังต้องสร้าง

## ตำแหน่งปัจจุบันใน roadmap

**หน้าเว็บทดลองและเก็บตัวอย่างเสร็จ → กำลังเข้าสู่ขั้นรับรองความรู้/สร้าง engine ที่ประเมินได้.** งานถัดไปให้ปิด knowledge release และแบบข้อมูล/สิทธิ์/transaction ก่อนเปิด paid beta. งานคลิปเริ่ม pilot คู่ขนานได้ด้วย template หนึ่งแบบ แต่ต้องมี job/cost/review workflow ก่อนเปิดให้ผู้ใช้อื่น.
