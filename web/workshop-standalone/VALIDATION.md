# ผลตรวจเว็บอิสระ — 2026-10-21

> **Owner review 26 ต.ค. 2026:** เพิ่ม `/review` ตรวจและรับรอง40development/6สำนวน พร้อมprivate revision history. Build/TypeScript/unit5testsผ่าน; Chromiumกับhosted Supabaseผ่านdraft/reload/approval/history/idempotency/concurrent409/CSRF/role+storage isolation/holdout exclusion/dirtyguard/mobile. WebKitproductionผ่านlogin/menu/40เคส/6สำนวน/audio metadata/mobile layout ไม่มีpageerror. Chromiumproductionทดสอบwrite/read/securityชุดเดียวกันผ่านและcleanupแล้ว. ใช้บัญชีสมมติสำหรับwrite tests; บัญชีแม่หมอจริงอ่านอย่างเดียว ยังไม่รับรองเนื้อหา. ดู `REVIEW_IMPLEMENTATION.md` และหลักฐานรวมในvault `backend/evidence/online-owner-review-2026-10-26.json`.

## เปลี่ยนสิทธิ์บัญชีแม่หมอเป็น owner — 2026-10-21

- เจ้าของระบุบัญชีที่มีอยู่จริงและ active. เปลี่ยนเฉพาะ membership role จาก reader เป็น owner; อ่านกลับยืนยัน 1 owner / 1 reader และข้อมูลสมาชิกอื่นไม่เปลี่ยน. ไม่เปลี่ยนรหัสผ่าน/คำอ่าน/เสียง และไม่ส่งอีเมล.
- ตรวจด้วย Chromium บน `https://maemorkratai-workshop.vercel.app`: เข้าด้วยรหัสเดิมจาก Keychain, API `/members` ตอบ 200, เห็นตัวเลือกผู้บันทึกและปุ่มส่งออก, สมุดตัวเองในเคสยังไม่เริ่มพิมพ์/อัดเสียงได้, เปิดสมุดสมาชิกอีกบัญชีเพื่อทบทวนได้และเป็น read-only.
- ไม่กดบันทึก/อัดเสียง/ส่งออก ไม่แก้คำอ่านจริง ไม่บันทึก screenshots หรือ session/credentials. ปิดเฉพาะ browser ตรวจ ไม่สั่ง global logout บัญชีแม่หมอ.
- หลักฐานใน runtime `artifacts/owner-access-check-20261021.json`: `passed=true`, `responsesWritten=0`, `audioUploaded=0`, `emailsSent=0`; ไม่มีอีเมล/user ID ในรายงาน. เป็นการตรวจสิทธิ์หลังเปลี่ยน role ไม่ใช่การรันชุด regression ทั้งหมดใหม่.
- ยังไม่มี approved-knowledge action/API/schema หรือหน้าเปรียบเทียบในรุ่นนี้. การดูทบทวนโดย owner ไม่เปลี่ยนสถานะ `review` เป็น approved อัตโนมัติ. ไม่มีการแก้โค้ดแอปหรือ deploy ในรอบนี้.

ตรวจจาก runtime `~/AIVideoLocal/maemorkratai/workshop-standalone`. รุ่นปัจจุบันเข้าใช้ด้วยอีเมลและรหัสผ่านตามคำสั่งเจ้าของ ไม่ต้องส่ง OTP. ข้อมูลคำอ่านและเสียงในชุดทดสอบเป็นข้อมูลสมมติทั้งหมด ไม่ใช่ข้อมูลแฟนหรือลูกดวง

## รุ่น 60 เคส / 4 หมวด — 2026-10-21

เพิ่มเคสการงาน การเงิน และสุขภาพหมวดละ 10 เคสจาก 30 เคสความรักเดิม. หมวดสุขภาพเป็นโจทย์เรื่องการดูแลตัวเอง ไม่ใช้ไพ่วินิจฉัยโรค. เคสเดิม 01–30 คง ID, เนื้อหา และ version; ฐาน Supabase เพิ่มเฉพาะ metadata ของเคส 31–60 ด้วย `sync-cases`, ไม่แก้คำอ่านหรือเสียงเดิม. รวม 40 development / 20 holdout.

- `node tests/check_cases.mjs`, `npm test`, `npm run typecheck` และ production build ผ่าน; ตรวจหมวด/ID/version/ไพ่/การแยก holdout, SQL/RLS และ Origin.
- Production browser smoke บน https://maemorkratai-workshop.vercel.app ผ่าน Chromium/WebKit: เลือก 4 หมวด, ขอบเขตรายการ/ความคืบหน้า, การกันทิ้งร่าง, รีเฟรชกลับเคสเดิม, save ในหมวดการงาน/การเงิน, เคสสุขภาพพร้อมเสียง signed upload/ฟังคืน/ใบที่ 4, สิทธิ์ข้ามบัญชีและ logout. `artifacts/hosted-check.json` ที่ runtime ยืนยัน `passed=true`, `temporaryDataRemoved=true`, `emailsSent=0`.
- ยังไม่ตรวจไมค์และ Safari บน iPhone จริง; การทดสอบเสียงใช้ไมค์จำลองใน Chromium.

ตารางผลด้านล่างเป็นหลักฐานรุ่นเดิม 30 เคส ณ 2026-10-20; ข้อความ `30 เคส` ในตารางนั้นหมายถึงผลตรวจครั้งก่อน ไม่ใช่จำนวนเคสปัจจุบัน.

## ผลตรวจรุ่นรหัสผ่าน

| การตรวจ | ผล |
|---|---|
| `npm test` | ผ่าน 2 กลุ่ม: PostgreSQL RPC/RLS และ Origin/CSRF |
| `node tests/check_cases.mjs` | ผ่าน 30 เคส, 20 development / 10 holdout, family ไม่ทับ, ไพ่ถูกต้อง, ไม่มีคำตอบแม่หมอ |
| TypeScript / production build | ผ่าน รวมการเปลี่ยน login และ Referrer-Policy |
| `scripts/manage.mjs check` กับ Supabase จริง | 30 เคส, private bucket, publishable key และ Email provider ใช้ได้; signup ยังเปิดและเว็บตรวจ membership เพิ่ม |
| `scripts/passwords.py` กับบัญชีผู้ทดลองจริง | ตั้งรหัสแยกให้สองบัญชีและ sign-in จริงผ่าน; ทั้งสองคง role reader/active ไม่มี owner; รหัสเก็บใน Keychain ไม่แสดงในแชท/ไฟล์ |
| Chromium + `tests/check_hosted.py` | ผ่าน wrong-password rejection, anonymous 401, password login, session/membership |
| Chromium + hosted Storage/PostgREST | ผ่าน MediaRecorder จากไมค์จำลอง → signed upload → ตรวจไฟล์จริง → บันทึก → reload → Range 206 และฟังคืน |
| Chromium + hosted reading flow | ผ่านซ่อนใบที่ 4 ก่อน seal, baseline คงเดิม, เปิดใบขยายและส่งทบทวน |
| Chromium + hosted permissions | reader อื่นฟังเสียงไม่ได้ 404, ขออ่านข้ามบัญชี/export ไม่ได้ 403, คำอ่านบัญชีใหม่ยังว่าง, logout แล้ว API 401 |
| WebKit + hosted Supabase | ผ่าน password login, reload ยังมี session, mobile 390 px ไม่ล้นจอ, logout แล้ว API 401 |
| Cleanup | ลบเฉพาะบัญชีสมมติชั่วคราว คำอ่าน และเสียงที่ชุดตรวจสร้างแล้ว; ไม่เหลือ cleanup journal |
| Operator scripts | Python compile และ Node syntax ผ่าน; Vercel CLI 64.7.0 เรียกได้ผ่าน npm cache แยก |

ผล hosted อยู่ใน runtime `artifacts/hosted-check.json`: passed=true, emailsSent=0, temporaryDataRemoved=true. ตรวจสองรอบสำเร็จ: Next production server บน loopback เชื่อม Supabase จริง และรอบล่าสุดใช้ https://maemorkratai-workshop.vercel.app บน Vercel จริง. ทั้งสองรอบตรวจ Chromium และ WebKit ตามตาราง แต่ยังไม่ใช่ไมค์บน iPhone จริง. ไม่มีการส่ง invitation/OTP และไม่ได้เขียนคำอ่านทดสอบให้สองบัญชีจริง

ข้อผิดพลาดที่พบและแก้:

- `Referrer-Policy: no-referrer` ทำ native POST form ส่ง `Origin: null`, ทำให้ logout ถูก CSRF ปฏิเสธ 403. เปลี่ยนเป็น `same-origin` ซึ่งยังไม่ส่ง referrer ไปเว็บอื่น; hosted Chromium และ WebKit ยืนยัน logout แล้ว session ใช้อีกไม่ได้
- Next dev มี compile/reload ระหว่าง browser smoke จึงตรวจชุด hosted ด้วย production build/server เพื่อให้ตรงรูปแบบ deploy
- Vercel token ที่เจ้าของลองครั้งแรกได้ 404 จาก `/v2/user`; helper เดิมบอกสาเหตุกว้างเกินไป. เพิ่มข้อความแยกสถานะ/endpoint โดยไม่แสดง response ที่อาจมีข้อมูลลับ. ไม่ยืนยัน scope ที่ผู้ใช้เลือกจาก HTTP 404 เพียงอย่างเดียว
- npm cache กลางมีไฟล์ที่สิทธิ์ไม่ตรง จึงให้ Vercel helper ใช้ cache แยกใน runtime parent; ไม่แก้ ownership ทั้งเครื่อง

## Vercel production

- Deploy สำเร็จในทีม `mae-mor-kratai` (Hobby), โปรเจกต์ใหม่ `maemorkratai-workshop`, build/typecheck บน Vercel ผ่านและสถานะ READY
- URL: https://maemorkratai-workshop.vercel.app — GET `/login` ได้ HTTP 200 และเป็นหน้าห้องทดลอง ไม่ต้องล็อกอิน Vercel
- [หลักฐาน deployment](https://vercel.com/mae-mor-kratai/maemorkratai-workshop/AwhEqYoYaKGg7vFX3LqrZ8jxAeqo)
- รัน `WORKSHOP_TEST_URL=https://maemorkratai-workshop.vercel.app ../.venv/bin/python tests/check_hosted.py` ผ่านทั้งหมด รวม signed audio จริง, reload/playback, 3+1, isolation และ logout; ลบข้อมูลสมมติของรอบนี้แล้ว
- ตั้ง environment จาก Keychain สำหรับ Production เท่านั้น; secret key เป็น Sensitive. ไม่มีการส่งค่าไปไว้ใน source/แชท. ไม่มีการแก้โปรเจกต์เว็บไพ่เดิม
- CLI link ครั้งแรกสร้างไฟล์ OIDC ชั่วคราวโดยอัตโนมัติ; ลบเฉพาะไฟล์ที่ยืนยันว่ามี OIDC ตัวเดียวแล้ว ไม่สำรองใน vault. เปลี่ยน helper ให้ link ผ่าน REST และห้ามคำสั่ง pull/login ที่เขียน credential ลงไฟล์; ตรวจ link กับโปรเจกต์จริงผ่าน
- เครื่องนี้เชื่อม token ได้หลังเจ้าของตั้งค่าใหม่; ไม่ทราบ scope ของ token ครั้งแรก จึงไม่ยืนยัน root cause ของ HTTP 404
- Deploy จาก CLI runtime; ไม่ได้ commit/push หรือเปิด Git auto-deploy ของแอปนี้. การทดสอบอีเมล/การตั้ง Site URL สำหรับ email callbacks ไม่เกี่ยวกับ password login ในรุ่นนี้

## หลักฐานรุ่นก่อนเปลี่ยน login

Chromium/WebKit ผ่าน provider fixture แบบ loopback และ SQL/RLS จริงใน PGlite: อัดเสียงจำลอง/ฟังคืน, consent, ซ่อนใบที่ 4, seal baseline, immutable review, request retry/idempotency, concurrency 200/409, reader isolation, owner read-only/export, mobile 360/390/430 px, ปฏิเสธไมค์แล้วพิมพ์แทนได้. WebKit ทดสอบ MediaRecorder ด้วย Web Audio จำลองด้วย

fixture เดิมใช้ OTP จำลอง; ปรับ fixture/login helper ให้ใช้ password แล้ว แต่การตรวจ login รุ่นนี้ใช้ hosted suite ข้างต้น. ไม่อ้างว่าได้รัน fixture browser suite ทั้งหมดซ้ำหลังเปลี่ยน login

SQL tests ใช้ migration ชุดเดียวกับฐานจริง: direct writes ถูกห้าม, reader ไม่เห็นของคนอื่น, owner เห็นเฉพาะผู้ทดลอง active, request UUID ผูกกับ payload เดิม, baseline/review แก้ไม่ได้, audio ต้องพร้อมและเป็นของ reader/case/stage เดียวกัน, client finalize audio ไม่ได้ และ withdrawal ระงับการอ่าน/เขียน

## ขอบเขตที่ยังไม่ตรวจ

- Safari และไมค์บน iPhone จริง รวมสลับแอป/ล็อกจอ
- Operator backup/purge/restore กับบริการจริง; ไม่มีการรันลบข้อมูลผู้ทดลองเพื่อทดสอบ
- SMTP delivery ไม่ใช้ในรุ่นนี้; ถ้าจะเพิ่ม OTP/reset email ภายหลังต้องตั้งและทดสอบใหม่
- Secret key ที่เคยเปิดเผยถูกนำออกจากไฟล์ตัวอย่างแล้ว แต่ไม่มีหลักฐานการ revoke คีย์เก่า; ไม่อ้างว่าการลบไฟล์ลบข้อความในแชทได้
- ไม่ได้กู้ข้อมูลจาก Sites เดิม และไม่ใช้บัญชี Sites บริษัท
