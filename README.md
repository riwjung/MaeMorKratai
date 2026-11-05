# แม่หมอกระต่าย · MaeMorKratai

เว็บดูดวงสไตล์แม่หมอกระต่าย พร้อมห้องเก็บความรู้ของแม่หมอ และเป้าหมายทำ Dashboard บริหารเว็บ/ช่อง รวมถึงสั่งผลิตซีรีส์ไพ่จากหน้าเว็บในอนาคต

**เพื่อน dev เริ่มที่ [คู่มือ consult](docs/consult/START_HERE.md)** — สถานะ ณ 5 พฤศจิกายน 2026, โครงสร้างระบบ, roadmap, จุดที่ต้องช่วยตัดสินใจ และวิธีเปิดโค้ด

| ส่วน | สถานะ | ซอร์ส |
|---|---|---|
| [เว็บดูดวง](https://mae-mor-kratai.vercel.app/) | ออนไลน์: รายวัน 78 ใบ; หน้า 3 ใบเป็น demo | [web/tarot](web/tarot) |
| [ห้องทดลอง](https://maemorkratai-workshop.vercel.app/) | ออนไลน์: สมาชิก/เสียงส่วนตัว/ตรวจคำอ่านโดย owner | [web/workshop-standalone](web/workshop-standalone) |
| Social Center | Dashboard ในเครื่อง: Next.js + FastAPI + SQLite + Meta read API | [services/social-center](services/social-center) |
| ระบบตอบ 3+1 ใบ/เครดิต/จ่ายเงิน/แดชบอร์ดรวม | วางแผนและรอพัฒนา | [Roadmap](docs/consult/ROADMAP.md) |
| สร้างซีรีส์ไพ่บนเว็บ | มี pipeline คลิปในเครื่อง; ระบบสั่งงานจากเว็บยังไม่สร้าง | [Content Studio](docs/consult/CONTENT_STUDIO.md) |

## เปิดเว็บลูกค้าในเครื่อง

ใช้ Node.js 24 LTS และ npm; รันคำสั่งจาก root ของ clone:

```sh
cd web/tarot
npm ci
npm run dev
```

เปิด http://127.0.0.1:3010/ · หน้าแรกไม่ต้องมี API key. `npm run build` สร้าง `out/` แบบ static export. วิธีเปิดอีกสองระบบและฐานทดสอบอยู่ใน [LOCAL_SETUP.md](docs/consult/LOCAL_SETUP.md).

## เอกสารสำหรับตรวจแบบ

- [CURRENT_STATE.md](docs/consult/CURRENT_STATE.md) — ทำถึงไหน/อะไรยังไม่มี/หลักฐานล่าสุด
- [ARCHITECTURE.md](docs/consult/ARCHITECTURE.md) — ระบบปัจจุบันและโครงสร้างเป้าหมาย
- [DATA_AND_PAYMENTS.md](docs/consult/DATA_AND_PAYMENTS.md) — ตารางจริง, schema ที่เสนอ, transaction และเครดิต
- [ROADMAP.md](docs/consult/ROADMAP.md) — ลำดับงานและเกณฑ์ผ่านก่อนขึ้นขั้นถัดไป
- [CONTENT_STUDIO.md](docs/consult/CONTENT_STUDIO.md) — Dashboard, งานสร้างคลิป, queue/worker และต้นทุน
- [CONTRIBUTING.md](CONTRIBUTING.md) — วิธีเสนอการแก้และขอบเขตข้อมูลใน public repo

Repository นี้เป็น public. มีซอร์ส/โจทย์ตัวอย่าง/คำอ่านรายวันที่เลือกเผยแพร่; คำตอบและเสียงผู้ทดลอง, holdout answers, ฐานข้อมูลจริง, credentials และโมเดล/สื่อที่แจกต่อไม่ได้เก็บนอก Git. เอกสารเก่าใน wiki/backend มีประวัติหลายรอบ ให้ยึดสถานะใน `docs/consult` เป็นจุดเริ่ม แล้วเปิดหลักฐานที่ลิงก์ไว้.

ผลตรวจชุดส่ง consult: [VALIDATION.md](docs/consult/VALIDATION.md).
