# แม่หมอกระต่าย — Local Social Center

> Source snapshotสำหรับconsultอยู่ในโฟลเดอร์นี้. วิธีเปิดจากcloneและตั้งdata directoryใหม่ดู [LOCAL_SETUP](../../docs/consult/LOCAL_SETUP.md). คำสั่ง/pathsเดิมด้านล่างเป็นสภาพruntimeบนMacเจ้าของ; ไม่ได้เป็นcloudadminที่deployแล้ว.

Next.js / React / TypeScript เป็นหน้าเว็บบน Mac และ FastAPI / SQLite เป็น API ภายใน โดยอ่าน Meta Graph API ผ่าน Facebook Login
กราฟหน้าเว็บใช้ SVG และตารางตรวจข้อมูล; PostgreSQL ยังไม่ได้ย้ายในรอบนี้
ฐานข้อมูลและ raw snapshots อยู่ `data/` บนเครื่อง; token อยู่ macOS Keychain service `maemorkratai.meta`
ไม่ใช้เครดิต Higgsfield ไม่มีระบบโพสต์ ตอบคอมเมนต์ หรืออ่านข้อความส่วนตัว

## เปิดใช้งาน

```sh
cd ~/AIVideoLocal/maemorkratai
.venv/bin/python scripts/open_center.py
```

เปิด http://127.0.0.1:3000 หรือใช้ `MaeMorKratai/tools/open-center.command`
Python virtualenv ติดตั้งแล้ว; หากย้ายเครื่องให้ `python3 -m venv .venv` และ `.venv/bin/pip install -r requirements.lock.txt`

## เชื่อมบัญชีจริง

1. เจ้าของเปิด https://developers.facebook.com/apps/ สร้าง App เฉพาะโครงการ และตั้ง use case/Facebook Login ตาม Meta Dashboard
2. เพิ่มบัญชีที่มีสิทธิ์เพจเป็น App role สำหรับรอบทดลอง; ตรวจ Page tasks ที่มี ANALYZE/MANAGE
3. ตรวจว่า IG เป็น Business/Creator เชื่อมกับเพจนี้ เจ้าของเป็นผู้เปลี่ยนประเภท/เชื่อมบัญชีใน Meta หากจำเป็น
4. เปิด Graph API Explorer https://developers.facebook.com/tools/explorer/ เลือก App และ **version ที่ Meta แสดงจริง** สร้าง User token
5. สิทธิ์สำหรับเริ่มตรวจ: `pages_show_list`, `pages_read_engagement`, `read_insights`, `instagram_basic`, `instagram_manage_insights`
   คอมเมนต์ตรวจ `instagram_manage_comments` / `pages_read_user_content` ตาม endpoint; Meta อาจมีเงื่อนไขเพิ่มเติมตามบัญชี/บทบาท/เวอร์ชัน
6. ในหน้าเชื่อมบัญชี กรอก version และ token; token ไม่ส่งผ่านแชต/URL/ไฟล์ config ระบบจะทดสอบ `/me/permissions` และ `/me/accounts` ก่อนเก็บใน Keychain
7. เลือกเพจ ระบบตรวจ Page tasks และชื่อ IG ต้องตรง `maemorkratai` แล้วเก็บ Page token
8. กดตรวจการเชื่อมสดก่อน ระบบทดสอบตัวตน สื่อ คอมเมนต์ และ Insights แยกกัน แล้วกดซิงก์ ตรวจ coverage เพื่อยืนยันโพสต์/คอมเมนต์/Insights จริง การพบเพจไม่ได้รับรองว่ามีสิทธิ์ทุก metric

API version ไม่มีค่าเดาเริ่มต้น รายการ metric เป็น **candidate probes** แก้ได้ในหน้าตั้งค่า
ชื่อที่ Meta ยกเลิกหรือ media ไม่รองรับจะถูกแจ้ง `unsupported` ไม่มีการแทนด้วยศูนย์
โค้ดไม่ใช้ publishing/messaging APIs แม้บาง permission สำหรับอ่านคอมเมนต์จะมีความสามารถเขียนด้วย
หากจำเป็นต้อง App Review / Advanced Access / Business Verification ทำตาม Dashboard ของแอปนั้น ไม่สัญญาว่าข้ามได้

## เก็บข้อมูลและข้อจำกัด

- initial backfill เดิน pagination ของ posts/media, Facebook video_reels, comments และ replies ที่ API ให้เข้าถึง
- เก็บ cursor ใน SQLite หลังนำเข้าหน้าข้อมูลแล้ว จำนวนคำขอต่อแพลตฟอร์มต่อรอบจำกัด 500; ถ้าหยุดกดซิงก์ใหม่เพื่อเก็บต่อ
- API rate limit retry สูงสุด 3 ครั้งต่อ request; token หมดอายุให้กลับมาเชื่อมใหม่ เก็บข้อมูลที่ดึงแล้วไว้
- หลัง initial backfill อัปเดตโพสต์/คอมเมนต์ 90 วันล่าสุดและ account Insights 90 วัน; ไม่อ้างว่าเป็นประวัติทั้งหมดนอก API scope
- ค่า metric เก็บ native name, unit, period, start/end, source ID, observed time แยก lifetime/day/total_over_range/snapshot
- ยอด 30 วันเปรียบเทียบก่อนหน้าเมื่อมี daily buckets ครบหรือยอดรวมตรงช่วงพอดี; ขอบเขตวันอ้าง Asia/Bangkok
  daily bucket ที่ต้นทางใช้ขอบเขตวันต่างกันจะไม่ถูกบวกเข้ายอดเต็มช่วงโดยเงียบๆ ให้ดู raw/coverage หรือนำเข้าไฟล์ที่ขอบเขตตรงกัน
- ยอดผู้ติดตามล่าสุดและเส้นแนวโน้มใช้ snapshot; ไม่สร้างประวัติผู้ติดตามที่ไม่มี ไม่รวม reach เป็นคนไม่ซ้ำ
- raw snapshots เพิ่มไฟล์ UUID ใหม่ ไม่แก้ไฟล์เก่า token ถูกตัดออกจาก response/URL ที่อาจปรากฏใน paging
- คอมเมนต์และ replies อยู่ในเครื่องเท่านั้น รายงานส่งเฉพาะจำนวนและธีม ไม่ใส่รายบุคคล

## นำเข้า CSV

ใช้ CSV จริงจาก Meta Business Suite; UTF-8/UTF-16/ภาษาไทย cp874 และ delimiter comma/semicolon/tab
ระบบแสดงคอลัมน์ให้จับคู่ ไม่เดาคอลัมน์ที่หาไม่พบเป็นตัวเลขศูนย์
เลือก `โพสต์/Reels`, `ภาพรวมรายวัน` หรือ `คอมเมนต์`; ใช้ Account ID เดิมให้ตรงกับ API
วันที่แนะนำ ISO `YYYY-MM-DD`; วันที่ export แบบ slash ที่ตีความได้สองแบบจะถูกปฏิเสธ ให้แปลงเป็น ISO ก่อนนำเข้า
ระบุ timezone ของ export และช่วงวัดจริง: lifetime หรือช่วง start-inclusive/end-exclusive
ข้อมูลรายวันใช้วันที่ของแต่ละแถว; followers เป็น snapshot ไม่ใช่ยอดผู้ติดตามใหม่
watch_time ใน CSV ใช้หน่วยวินาที; API `ig_reels_avg_watch_time` ใช้มิลลิวินาทีตาม native metric
ไฟล์เดิม+mapping+scope เดิมนำเข้าซ้ำไม่เพิ่ม records ตรวจทุกแถวก่อนบันทึก ไม่รองรับตัวเลขย่อ 1.2K

## รายงาน / Obsidian

```sh
.venv/bin/python -m maemorkratai.cli report
.venv/bin/python -m maemorkratai.cli sync
```

vault อยู่ `/Users/sawettachatsuthum/Desktop/AI_Video/MaeMorKratai`
รายงานแต่ละรอบเป็นหน้าใหม่ มี raw JSON ของหลักฐานสรุป source page และรายการ source snapshot ในเครื่อง
ทุกการส่งออกรายงานอัปเดต index และเพิ่ม log; ไม่แตะ .obsidian ไม่เผยแพร่
สรุปหัวข้อ/ธีมใช้ keyword rules ตรวจโดยเจ้าของก่อนใช้เป็นข้อสรุป แผนทดลองติดป้ายสมมติฐาน

## งานรายวันและการทดสอบ

LaunchAgent `ai.maemorkratai.daily-sync` ตั้ง 08:00 ตามเวลาระบบ Mac พร้อม catch-up เมื่อเริ่มงานหลัง 08:00 Bangkok
เครื่องนี้ต้องตั้ง timezone Asia/Bangkok; หากเปลี่ยน timezone ให้เปลี่ยน scheduler ด้วย
ถ้ายังไม่เลือกเพจจะข้ามงานโดยไม่ติดต่อ Meta; logs ไม่บันทึก token

```sh
.venv/bin/pytest -q
python3 /Users/sawettachatsuthum/Desktop/AI_Video/MaeMorKratai/tools/wiki-lint.py
launchctl print gui/$(id -u)/ai.maemorkratai.daily-sync
```

หยุดงานรายวัน: `launchctl bootout gui/$(id -u)/ai.maemorkratai.daily-sync`
ทดสอบใช้ temporary database + fake transport แยกจากข้อมูลจริง ไม่แสดง fixtures ใน dashboard ของช่อง
การตรวจ source ตัวอย่าง 10 โพสต์กับบัญชีจริงยังต้องทำหลังได้รับ token/CSV จากเจ้าของ

## แหล่งอ้างอิงเทคนิค

- Meta Instagram API: https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api
- Meta SDK metric names: https://github.com/facebook/facebook-python-business-sdk/blob/main/facebook_business/adobjects/instagraminsightsresult.py
- Meta Page API: https://developers.facebook.com/docs/pages-api/
- macOS LaunchAgent: `man launchd.plist`

## ภาพตัวละครและคลิปอ้างอิง

เมนูตัวละครที่ http://127.0.0.1:3000/#brand เปิดภาพโปรไฟล์ 3 แบบ คลิปอ้างอิง H.264 และ contact sheet จากไฟล์ที่เจ้าของให้
IMG_5392.JPG เป็น identity หลัก; ภาพ Pride เป็น variant เฉพาะโอกาส มี brief/prompt ทดลอง 15 วินาทีแบบไม่พูด แต่ยังไม่ได้เจนหรือใช้เครดิต
หลังเชื่อมและซิงก์ ส่วนโพสต์จริงแสดงตัวอย่างล่าสุดจาก API ของบัญชีที่เลือกพร้อม snapshot; ต้องเปิดดูภาพ/คลิปจริงก่อนสรุป mood/tone ของช่อง
URL สื่อเก็บจาก Meta อาจหมดอายุ; ไม่มีการดาวน์โหลดคลิปทั้งหมดหรือวิเคราะห์เสียงทุกโพสต์อัตโนมัติ

โค้ด Next.js อยู่ web/; Node 24 และ npm ติดตั้งแล้ว Build ด้วย NEXT_TELEMETRY_DISABLED=1 npm run build -- --webpack ภายใน web/
API อ่านข้อมูลยังเปิด 127.0.0.1:8787; Next.js proxy server-side ไม่ใส่ Meta token ใน browser storage/query
คู่มือทีละขั้นอยู่ใน vault: wiki/analyses/social-api-connection-guide.md
