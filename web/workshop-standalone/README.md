# ห้องทดลองแม่หมอกระต่าย — เว็บอิสระ

> **Consult snapshot 2026-11-05:** ระบบมี owner/reader และ owner review `/review` แล้ว. เริ่มจาก [สถานะปัจจุบัน](../../docs/consult/CURRENT_STATE.md) และ [วิธีเปิดฐานทดสอบ](../../docs/consult/LOCAL_SETUP.md); บันทึกวันที่20–21ต.ค.ที่บอกว่ายังไม่มีownerเป็นประวัติ. จำนวนapprovedล่าสุดต้องตรวจด้วยownerก่อนทำknowledge release.

> **หน้าตรวจออนไลน์ — 2026-10-26:** เพิ่ม `/review` สำหรับ Owner ตรวจ 40 เคสพัฒนาและสำนวน 6 ข้อ แก้ฉบับตรวจ ฟังเสียง บันทึกร่าง/ต้องแก้ต่อ/รับรอง และเปิดประวัติได้ เก็บแยกใน private Storage ไม่แก้ต้นฉบับ ไม่รวม 20 holdout ในหน้าตรวจ และยังไม่เปิด AI ตอบลูกค้า อ่าน [คู่มือตรวจ](docs/owner-review-th.md) และ [รายละเอียดระบบ](REVIEW_IMPLEMENTATION.md) ข้อความ “ยังไม่มีปุ่มรับรอง” ด้านล่างเป็นประวัติก่อนรุ่นนี้

> **คำอ่านครบแล้ว 2026-10-26:** ตรวจ Supabase จริงของ active owner พบ60/60เคสเป็นreview; 57เคสข้อความทั้งสองช่วง/3เคสเสียงทั้งสองช่วง รวม6ไฟล์479วินาทีตามmetadata. ขั้นต่อไปคือสำรอง/ถอดเสียง/จัดฉบับรับรองและstyle guide แล้วเทียบAกฎล้วน/BมีLLMตาม `MaeMorKratai/backend/READING_ENGINE_PLAN.md` ในvault. คงdevelopment40/holdout20. ยังไม่รับรองเนื้อหา ฝึกโมเดล หรือเปิดAIตอบลูกค้า; รอบตรวจนี้ไม่เปลี่ยนข้อมูลต้นฉบับ.

คู่มือสำหรับแม่หมอและผู้ทดลอง: [PDF 2 หน้า สำหรับส่งให้อ่าน](docs/workshop-manual-th.pdf) · [ฉบับ HTML สำหรับเปิดในเบราว์เซอร์](docs/workshop-manual-th.html) — เริ่มจากทำให้จบหนึ่งเคส พร้อมอธิบายปุ่มบันทึก การอัดเสียง และการใช้สมุดของตัวเอง (21 ต.ค. 2026).

> **อัปเดตสิทธิ์ 2026-10-21:** เจ้าของระบุบัญชีแม่หมอให้เป็น owner แล้ว; ฐานจริงมีสมาชิก active **1 owner / 1 reader**. บัญชีแม่หมอใช้รหัสเดิม ตอบ/อัดเสียงในสมุดของตัวเอง ดูคำอ่านสมาชิกอื่น และส่งออกได้. ตรวจบนเว็บ production ผ่าน. ยังไม่มีปุ่มรับรองเป็น approved knowledge หรือหน้าเปรียบเทียบ; ให้แม่หมอทดสอบเก็บคำอ่านให้เสร็จก่อนเตรียมเฟสเหล่านั้น. รายละเอียดสอง reader ในย่อหน้าประวัติด้านล่างถูกแทนที่ด้วยสถานะนี้. ไม่เก็บอีเมลใน repository.

สถานะ 2026-10-21: ใช้อีเมลและรหัสผ่านตามที่เจ้าของเลือก ไม่ต้องตั้ง SMTP สำหรับการเข้าใช้รุ่นแรก. Supabase project `pmyftgrjhujcdwtfotqn` มี 60 เคสใน 4 หมวดและ private bucket; public/secret key ใช้งานได้. ผู้ทดลอง 2 บัญชีเป็น `reader` ดูเฉพาะคำอ่านตัวเอง ไม่มีสมาชิก `owner`. ตั้งรหัสเริ่มต้นแยกกันและตรวจ sign-in จริงแล้ว; รหัสอยู่ใน macOS Keychain ไม่อยู่ใน source/แชท. **Deploy แล้ว:** [เปิดห้องทดลอง](https://maemorkratai-workshop.vercel.app) ในโปรเจกต์ `mae-mor-kratai/maemorkratai-workshop` แยกจากเว็บลูกค้าเดิม. หน้า login เปิดได้โดยไม่ต้องมีบัญชี Vercel. ผลทดสอบล่าสุดและข้อจำกัดอยู่ใน [VALIDATION.md](VALIDATION.md).

Runtime: `~/AIVideoLocal/maemorkratai/workshop-standalone/`
สำเนาซอร์สใน vault: `MaeMorKratai/web/workshop-standalone/`

## สิ่งที่ทำได้

- 60 เคสสมมติ: ความรัก 30, การงาน 10, การเงิน 10, สุขภาพ 10 ให้แม่หมออ่าน 3 ใบ อัดเสียงหรือพิมพ์ เก็บต้นฉบับ แล้วจึงเห็นใบที่ 4 ขยายอนาคต
- เลือกหมวดได้จากปุ่มด้านบนทั้งคอมพิวเตอร์และมือถือ; รายการ/ความคืบหน้า/ก่อนหน้า–ถัดไปอยู่ในหมวดที่เลือก และถามก่อนทิ้งร่างเมื่อเปลี่ยนเคส; รีเฟรชแล้วกลับมาหมวด/เคสเดิมตาม URL
- เก็บร่าง ประวัติการแก้ไข และเสียงแต่ละรอบแยกกัน ป้องกันบันทึกชนกันและการส่งคำขอเดิมซ้ำ
- ต้นฉบับก่อนเปิดใบที่ 4 แก้ทับไม่ได้ คำอ่านที่ส่งแล้วเข้าคิวทบทวน ยังไม่ใช่คำตอบที่อนุมัติให้ลูกค้า
- เข้าด้วยอีเมลและรหัสผ่าน เฉพาะผู้ที่เจ้าของเพิ่มสิทธิ์ Reader เห็นของตัวเอง Owner เปิดดูของผู้ทดลองและส่งออกได้
- เสียงอยู่ใน private Storage อัปโหลดตรงด้วย signed upload token เพื่อไม่ติดเพดาน body ของ Vercel; 16 MB / 10 นาทีต่อครั้ง ฟังคืนผ่านลิงก์ชั่วคราว
- Owner สำรองข้อความพร้อมเสียงด้วยสคริปต์; Reader ถอนความยินยอมได้ คำอ่านหยุดเปิดให้ดูทันที ส่วนการลบไฟล์ต้องให้เจ้าของรันคำสั่ง

ไม่มี AI ตอบแทนแม่หมอ ไม่มี STT/RAG/embedding/การเก็บเงินในรุ่นนี้ ข้อมูลทดลองไม่อิงชื่อหรือเรื่องจริงของลูกดวง ไม่มีการย้ายคำตอบ/เสียงจาก Sites เดิม เพราะยังไม่มีไฟล์ export ต้นทาง

## ชุดเคสและหมวด

| หมวด | เคส | ขอบเขตตัวอย่าง |
|---|---|---|
| ความรัก | 01–30 | ความสัมพันธ์ สถานะ การสื่อสารและการตัดสินใจ |
| การงาน | 31–40 | เปลี่ยนงาน ทีม เลื่อนตำแหน่ง ธุรกิจ และทักษะใหม่ |
| การเงิน | 41–50 | รายรับรายจ่าย เงินออม รายได้เสริม และขอบเขตการช่วยเหลือ |
| สุขภาพ | 51–60 | การพักผ่อน ความเครียด กิจวัตร และการดูแลตัวเอง |

โจทย์เป็นสถานการณ์สมมติและไม่มีเฉลยให้แม่หมอ. หมวดสุขภาพไม่ใช้ไพ่วินิจฉัยโรค เลือกยา หรือเลือกการรักษา; การเงินไม่ตั้งโจทย์ให้รับรองผลตอบแทน. คำอ่านทุกหมวดต้องผ่านการทบทวนก่อนนำไปตอบลูกค้า

เคส 01–30 คงข้อความ ไพ่ ID และ version เดิม เพื่อให้คำอ่านเก่ายังอ้างถึงโจทย์เดิม. เคส 31–60 ใช้ `intake-multicategory-2026-10-v1`; รวม 40 development / 20 holdout โดย family ไม่ข้ามชุด. เปลี่ยนความหมายโจทย์เดิมภายหลังต้องออก ID/version ใหม่ ไม่แก้โจทย์ที่มีคำอ่านแล้วแบบเงียบ ๆ

## Supabase และบัญชีผู้ทดลอง

ฐานจริงพร้อมแล้ว **ไม่ต้องรัน migrations ซ้ำ**. เครื่องใหม่หรือโปรเจกต์ใหม่เท่านั้นจึงรัน `supabase/migrations/001_workshop.sql` แล้ว `002_cases.sql` และ `003_more_categories.sql` ตามลำดับ. ตรวจฐานปัจจุบันได้โดยไม่แสดง key:

```sh
cd ~/AIVideoLocal/maemorkratai/workshop-standalone
../.venv/bin/python scripts/credentials.py status
../.venv/bin/python scripts/credentials.py run node scripts/manage.mjs check
```

- Authentication → Email: เปิด Email provider ไว้. ปิด **Allow new users to sign up** ใน Auth settings; ตอนตรวจล่าสุดยังเปิดอยู่ แต่เว็บ/API/RLS ตรวจ active membership เพิ่มอยู่แล้ว
- Project URL, publishable key และ secret key อยู่ใน macOS Keychain. เปลี่ยนค่าได้ด้วย `../.venv/bin/python scripts/credentials.py configure`; ช่องกรอกไม่แสดงค่า ไม่ใช้ `.env` เก็บ secret. ไม่ใส่ secret key ในตัวแปรชื่อ `NEXT_PUBLIC_`
- เคยมี secret key ถูกแนบในบริบทแชทและไฟล์ตัวอย่าง; ลบจากไฟล์แล้ว แต่ยังไม่มีหลักฐานว่า revoke คีย์เก่า. เปลี่ยนที่ Supabase และอัปเดต Keychain ถ้ายังไม่ได้ทำ
- ไม่มีการส่ง invitation/OTP หรือขออีเมล reset password ในรุ่นนี้. การล็อกอินใช้ [Supabase password auth](https://supabase.com/docs/reference/javascript/auth-signinwithpassword). หากจะเพิ่ม OTP/reset ทางอีเมลภายหลัง ต้องตั้งและทดสอบ [custom SMTP](https://supabase.com/docs/guides/auth/auth-smtp) ก่อน

ลงทะเบียน metadata ของเคสเพิ่มจาก catalog ได้ด้วยคำสั่งต่อไปนี้ (รอบนี้ทำแล้วครบ 60):

```sh
../.venv/bin/python scripts/credentials.py run node scripts/manage.mjs sync-cases
```

คำสั่งเติมเฉพาะ IDs ที่ยังไม่มี ตรวจ version/split ให้ตรง และหยุดถ้าพบข้อมูลเดิมขัดกัน. ไม่แก้คำอ่าน/เสียง; บนฐานเดิมใช้คำสั่งนี้หรือ SQL `003_more_categories.sql` สำหรับเคสใหม่ ไม่ต้องรัน `001`/`002` ซ้ำ

คัดลอกรหัสเริ่มต้นของบัญชีที่เตรียมไว้:

```sh
../.venv/bin/python scripts/passwords.py copy
```

กรอกอีเมลที่ได้รับสิทธิ์ โปรแกรมจะคัดลอกรหัสลง clipboard แล้วนำไปวางในช่องรหัสผ่านของเว็บ. ไม่มีการแสดงรหัสบน Terminal. ส่งให้ผู้ทดลองด้วยช่องทางส่วนตัวที่คุณเลือกเอง; สคริปต์ไม่ส่งข้อความแทนคุณ

ถ้าลืมรหัสหรืออยากตั้งรหัสที่จำได้ ใช้คำสั่งนี้ แล้วกรอกอีเมลและรหัสใหม่อย่างน้อย 12 ตัว (เว้นว่างเพื่อสุ่ม):

```sh
../.venv/bin/python scripts/passwords.py reset
```

เพิ่มสมาชิกใหม่เฉพาะเมื่อเจ้าของสั่ง:

```sh
../.venv/bin/python scripts/credentials.py run node scripts/manage.mjs add-user
../.venv/bin/python scripts/passwords.py provision
```

`add-user` ถามอีเมล ชื่อที่แสดง และ role; ผู้ทดลองใช้ `reader`. `provision` ตั้งรหัสสำหรับสมาชิก active ที่มีอยู่แล้ว ไม่สร้างสมาชิกหรือยกระดับ role. ~~สองบัญชีคงเป็น reader~~ → วันที่ 2026-10-21 เจ้าของระบุบัญชีแม่หมอให้เป็น owner จึงเปลี่ยนเฉพาะ role ของบัญชีนั้น; อีกบัญชีคง reader. การมีเครื่องมือ operator ไม่ได้ทำให้บัญชีเป็น owner ในเว็บเอง. ไม่เก็บรายชื่ออีเมลใน source

## Vercel และการ deploy รอบถัดไป

โปรเจกต์ `maemorkratai-workshop` สร้างและ deploy แล้วในทีม `mae-mor-kratai` (Hobby). เครื่องนี้มี token ใน Keychain และ `.vercel/project.json` แล้ว จึงใช้คำสั่ง deploy ด้านล่างได้. ถ้าเชื่อมใหม่หรือ token หมดอายุ ให้สร้าง token อายุสั้นใน [Vercel ของบัญชีที่คุณควบคุมเอง](https://vercel.com/account/tokens) แล้วเก็บผ่านช่องกรอกที่ซ่อนค่า:

```sh
cd ~/AIVideoLocal/maemorkratai/workshop-standalone
../.venv/bin/python scripts/vercel.py configure
../.venv/bin/python scripts/vercel.py run whoami
../.venv/bin/python scripts/vercel.py run teams ls
```

ตัวช่วยอ่าน token จาก Keychain เข้า environment ของ CLI ไม่เขียน auth token ลง repo หรือ command arguments. ตรวจบัญชี/team ก่อนเลือก scope. หากได้ 404 จาก `/v2/user` แปลว่าขั้นตรวจบัญชีไม่สำเร็จ ยังไม่ใช่ error ของแอป; ตรวจ scope/สิทธิ์บัญชีตามข้อความ helper. เชื่อมเฉพาะโปรเจกต์ที่สร้างแล้วด้วยตัวช่วย REST ซึ่งไม่ดาวน์โหลด token ลง `.env.local`:

```sh
../.venv/bin/python scripts/vercel.py link mae-mor-kratai
../.venv/bin/python scripts/vercel.py env-production
../.venv/bin/python scripts/vercel.py run deploy --prod --scope mae-mor-kratai --yes
```

Deploy ปัจจุบันมาจาก CLI ที่ runtime; ยังไม่ได้ commit/push หรือเชื่อม Git อัตโนมัติสำหรับแอปนี้. ทำใน runtime ซึ่ง root เป็นโฟลเดอร์แอปนี้, framework Next.js, build `npm run build`, output ค่าเริ่มต้น. `env-production` ตรวจชื่อ project ก่อนส่งค่าสามตัวจาก Keychain ไปยัง [Vercel Environment Variables API](https://vercel.com/docs/rest-api/projects/create-one-or-more-environment-variables):

| ชื่อ | ขอบเขต |
|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | Production, encrypted |
| `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` | Production, encrypted |
| `SUPABASE_SECRET_KEY` | Production, sensitive |

Preview หากต้องใช้ ให้แยกฐานทดสอบ ไม่ผูกกับข้อมูลจริงโดยอัตโนมัติ. Public key/URL ถูกฝังตอน build; เปลี่ยนค่าแล้วต้อง deploy ใหม่. ตรวจ production URL ว่าเปิดถึงหน้า login ได้จากมือถือโดยไม่ติด Vercel Deployment Protection. ตั้ง Supabase Auth → Site URL เป็น URL HTTPS ที่ได้สำหรับการตั้งค่าภายหลัง; password flow นี้ไม่ใช้ email callback

ก่อนให้แฟนเริ่มเก็บข้อมูล ตรวจ URL จริง → รหัสผ่าน → อัดเสียง → บันทึก → reload → ฟังคืน → เปิดใบที่ 4 และตรวจ Safari/ไมค์บน iPhone จริง รวมการสลับแอป/ล็อกหน้าจอ

## เปิดและทดสอบในเครื่อง

```sh
npm ci
../.venv/bin/python scripts/credentials.py run npm run dev
```

เปิด `http://127.0.0.1:3012`. URL นี้ใช้จากเครื่องนี้เท่านั้น; มือถืออีกเครื่องใช้ URL HTTPS ของ Vercel. ถ้ายังไม่ตั้ง Supabase หน้า login จะแสดงว่ากำลังเตรียมห้อง ไม่สามารถบันทึกจริง

ชุดตรวจไม่ต้องใช้บัญชี Supabase:

```sh
npm test
node tests/check_cases.mjs
npm run typecheck
npm run build
```

ทดสอบ browser แบบ loopback: ติดตั้ง Playwright ใน Python venv (`pip install playwright` แล้ว `python -m playwright install chromium webkit`) และหยุด dev server เดิมก่อน จากนั้น:

```sh
# Terminal 1: Auth/Storage จำลอง และ SQL/RLS จริงใน PGlite; ข้อมูลอยู่ในหน่วยความจำ
npx tsx tests/provider-fixture.ts
# Terminal 2: เรียงตามลำดับนี้ ฐาน fixture ต้องเริ่มใหม่ก่อนชุดทดสอบแต่ละรอบ
../.venv/bin/python tests/check_browser.py
../.venv/bin/python tests/check_webkit.py
```

Fixture ใช้เฉพาะ loopback และไม่มี auth bypass ใน production app. หยุด fixture ด้วย Ctrl+C เมื่อเสร็จ. ผล fixture ไม่แทนการตรวจ hosted Supabase, Vercel จริง หรือไมค์ iPhone จริง ดู `VALIDATION.md`.

ตรวจ hosted Supabase ด้วย production server ในเครื่อง (สร้างบัญชีสมมติชั่วคราวสองบัญชีและลบข้อมูลของการทดสอบเมื่อจบ ไม่มีการส่งอีเมล):

```sh
# Terminal 1
../.venv/bin/python scripts/credentials.py run npm run build
../.venv/bin/python scripts/credentials.py run npm run start
# Terminal 2
../.venv/bin/python tests/check_hosted.py
```

ตรวจเว็บ production ด้วยบัญชีสมมติชั่วคราวได้เช่นกัน:

```sh
WORKSHOP_TEST_URL=https://maemorkratai-workshop.vercel.app ../.venv/bin/python tests/check_hosted.py
```

ใช้ production server เพื่อไม่ให้ไฟล์รายงานทดสอบกระตุ้น Next dev ให้ compile/reload ระหว่างตรวจ. หากทดสอบขัดข้องระหว่าง cleanup ให้ดู `artifacts/hosted-test-cleanup.json` ซึ่งมีเพียง IDs/อีเมลสมมติและลบเฉพาะข้อมูลของบัญชีเหล่านั้นก่อนรันใหม่. ห้ามนำ artifacts, backups, `.next`, `.env` หรือข้อมูลจริงไปคัดลอกใน vault

## สำรองข้อมูลและถอนความยินยอม

ปุ่มส่งออกในเว็บส่งเฉพาะข้อความ/metadata ของผู้ที่เลือก ไม่ได้รวมเสียง. สำรองครบด้วย:

```sh
../.venv/bin/python scripts/credentials.py run node scripts/manage.mjs backup
```

ได้ `backups/<timestamp>/data.json`, `manifest.json` และ `audio/` พร้อม SHA-256. เก็บนอก iCloud/vault และอย่าส่งให้บริษัท. รันขณะไม่มีผู้ทดลองแก้ข้อมูล; export นี้ไม่ใช่ transactional database snapshot และไม่รวม Auth secrets. **ยังไม่มีการทดสอบ restore ข้ามโปรเจกต์**; ถ้าย้ายต้อง remap Auth user IDs และตรวจไฟล์จาก manifest. คำอ่านและเสียงของผู้ถอนสิทธิ์ถูกตัดออกจาก backup ใหม่

หลังมีคำขอถอนสิทธิ์ Owner จะเห็นแจ้งเตือน. ลบข้อมูลและไฟล์ที่บริการด้วย:

```sh
../.venv/bin/python scripts/credentials.py run node scripts/manage.mjs purge-withdrawals
```

คำสั่งทำเฉพาะคำขอที่ผ่าน 2 ชั่วโมง 30 นาที เพื่อรอ signed upload token อายุ 2 ชั่วโมงหมดก่อน ([เอกสาร Supabase](https://supabase.com/docs/reference/javascript/storage-from-createsigneduploadurl)). ลิงก์ฟังเสียงที่ออกไปก่อนถอนสิทธิ์ยังอยู่ได้ไม่เกิน 15 นาที. คำสั่งเก็บสมาชิกที่ถูกระงับและเวลารับ/ดำเนินการคำขอไว้; ไม่ลบ Auth account. ต้องตรวจสำเนา export/backup เก่าและ retention ของผู้ให้บริการแยกด้วย. ยังไม่มี cron ลบอัตโนมัติ

## โครงสร้างและข้อจำกัด

- `app/workshop.tsx`, `app/recorder.tsx`: หน้ากรอกและ MediaRecorder; ใช้ได้บน secure context
- `app/api/workshop/[[...path]]/route.ts`: ตรวจ session/role/Origin; signed uploads, download และ export แบบแบ่งหน้า
- `supabase/migrations/`: schema, RLS และ RPC บันทึกใน transaction พร้อม revision/request UUID
- `lib/cases.json`: 40 development / 20 holdout แยก family; ไม่มีเฉลย; ใบที่ 4 อยู่ฝั่ง server จน seal
- `public/cards/`: ภาพไพ่ 76 ใบ — 71 ใบแบบมีชื่อไพ่จาก `~/Downloads/MaeMorKratai/cards-titled/v1` (2026-10-20, `.jpg` 637×1024) และ 5 ใบเดิมไม่มีชื่อ (`.jpeg`: The Fool, The Lovers, The Hanged Man, Three of Wands, Queen of Swords). The Devil และ King of Pentacles ยังไม่มีภาพ จึงแสดงชื่อไพ่แทน
- `scripts/`: Keychain, เพิ่มสิทธิ์/รหัสผ่าน, เชื่อม Vercel, สำรองไฟล์, ดำเนินการคำขอลบ

SQL ทำให้ authenticated client เขียนตารางตรงไม่ได้และเปิดอ่านคนละ reader ไม่ได้. Service key เป็นสิทธิ์เจ้าของระบบ จึงต้องอยู่ในบัญชี hosting ที่เชื่อถือได้. ขนาด API ของ Vercel จำกัดไว้; เว็บส่ง binary เสียงตรงเข้า Storage และใช้ redirect ไป signed URL สำหรับฟังคืน ([Vercel limits](https://vercel.com/docs/functions/limitations)).
