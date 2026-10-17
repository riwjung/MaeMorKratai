# ส่งต่องานให้ Claude — แม่หมอกระต่าย

อัปเดต: 2026-10-16 (Asia/Bangkok)

## เริ่มอ่านที่นี่

โปรเจกต์นี้เป็น Obsidian vault; Claude Code ที่เปิดโฟลเดอร์นี้สามารถอ่าน Markdown โดยตรงได้ ไม่ต้องเปิดแอป Obsidian และไม่จำเป็นต้องนำเข้าฐานข้อมูลใหม่

1. อ่าน `AGENTS.md` และ `CLAUDE.md` — กติกาของโปรเจกต์
2. อ่านไฟล์นี้ — ภาพรวมงานที่เพิ่งส่งมอบ
3. อ่าน `HANDOFF.md`, `index.md` และท้าย `log.md` — สถานะ/ประวัติ/สารบัญละเอียด
4. งานเว็บ: `web/tarot/READING.md` และ `web/tarot/VERIFY.md`
5. งานเจนภาพ: `tools/gemini-web-runner/README_TH.md` และ `animations/tarot-pilot/prompts-78/README_TH.md`

นี่คือโปรเจกต์แม่หมอกระต่าย แยกจาก AI-Video-Project; อย่ายืมสไตล์ Zack D. Films มาใช้โดยอัตโนมัติ

## ที่ตั้งและวิธีทำงาน

| ส่วน | ตำแหน่ง |
|---|---|
| Vault / checkout | `/Users/sawettachatsuthum/Desktop/AI_Video/MaeMorKratai` |
| Runtime งานหนัก | `/Users/sawettachatsuthum/AIVideoLocal/maemorkratai` |
| เว็บไพ่ที่ใช้รันจริง | `~/AIVideoLocal/maemorkratai/tarot-web` |
| ซอร์สเว็บสำรองใน Git | `web/tarot/` |
| Social Center เดิม | Next.js port3000; FastAPI8787; SQLite |
| Git remote | `https://github.com/riwjung/MaeMorKratai.git` |
| Branch หลัก | `main` |

ทำ build/test/render ใน runtime นอก iCloud แล้วสำรองไฟล์ที่แก้กลับ vault ก่อน commit. ตรวจ `git status` ก่อนทุกครั้ง เพื่อรักษาการแก้ของเจ้าของหรือเอเจนต์อื่น. Git metadata ของ checkout บนเครื่องนี้แยกอยู่นอก iCloud; อ่าน `GIT.md` ก่อนย้ายเครื่องหรือย้าย checkout

## สิ่งที่ทำเสร็จแล้ว: เว็บไพ่

หน้าเดิม `/` เปิดไพ่หนึ่งใบจากสำรับภาพจริง5ใบ มีฉากแม่หมอกระต่าย,แสงเปิดไพ่,ปิด/เปิดใบเดิมซ้ำ และความหมายแยก6สถานะความรัก

หน้าใหม่ `/reading/` เชื่อมจากลูกศร **เปิดไพ่ 3 ใบ →**:

1. เลือกความรัก/การงาน/การเงิน/ภาพรวมชีวิต และคำถามที่พิมพ์หรือเลือกจากตัวอย่าง
2. เลือกสถานการณ์;ความรักใช้คนโสด/แอบชอบ/คุยกัน/ซับซ้อน/มีแฟน/เลิกกัน
3. สำรับสับวนด้วยGSAPจนผู้ใช้แตะหยุด;รวมจากposeปัจจุบันแล้วกางสำรับ
4. เลือก3ใบจาก78รหัสไม่ซ้ำ: ลากไพ่จากพัดไปวางในช่องอดีต/ปัจจุบัน/อนาคตที่ต้องการ หรือแตะแล้วกดเลือก (ลงช่องว่างแรก); คืนไพ่ได้ก่อนเปิดและช่องว่างไว้ไม่เลื่อน
5. แตะไพ่ในช่องเพื่อเปิดเองทีละใบ ลำดับใดก็ได้ หรือกดเปิดใบที่เหลือ; เปิดครบแล้วปลดล็อกคำอ่านแบบสาธิตฟรี

ใช้ม่วง/ครีม/พีชและมาสคอต/หลังไพ่เดิม รองรับkeyboard,reducedmotion,ภาพที่ยังไม่พร้อมและGSAPโหลดไม่สำเร็จ

### ไฟล์สำคัญ

- `app/reading/page.tsx` — หมวด/สถานการณ์/flow/ผลอ่าน
- `app/reading/Table.tsx` — สำรับสับ,พัด/กริด,เลือก/คืน/เปิดไพ่
- `app/reading/reading.css` — UIใหม่ที่แยกสไตล์จากหน้าเดิม
- `lib/reading.ts` — types,state reducer,WebCrypto Fisher–Yates,ตัวสร้างคำอ่านdemo
- `lib/reading-cards.json` — 78รหัสและ468ความหมาย พร้อมแหล่งข้อมูลและURLภาพที่มีจริง
- `lib/reading-motion.ts` — ตัวโหลดGSAPจากlocal asset
- `app/reading/DeckScene.tsx` — สำรับ WebGL (three.js) ช่วงสับ→รวม→กาง ส่งต่อให้พัด DOM; ไม่มี WebGL/reduced motion ใช้สำรับ DOM ใน `Table.tsx`

พาธข้างต้นสัมพันธ์กับโฟลเดอร์เว็บ ไม่ใช่รากvault

### วิธีเปิดเว็บ

เครื่องเจ้าของ:

```sh
cd ~/AIVideoLocal/maemorkratai/tarot-web
npm run build
python3 -m http.server 3010 --bind 127.0.0.1 --directory out
```

เปิด `http://127.0.0.1:3010/reading/` หากportถูกใช้อยู่ให้ตรวจprocessเดิมก่อน อย่าฆ่าprocessอื่นโดยไม่ตรวจสอบ. การพัฒนาใช้ `npm run dev` แทนstatic serverบนportเดียวกัน

บนเครื่องใหม่: เข้า `web/tarot/`, ใช้Nodeตามengines, `npm ci`, แล้วใช้คำสั่งbuild/devเดิม. ซอร์สไม่มีsecretsหรือฐานข้อมูลส่วนตัว

### ผลทดสอบรอบล่าสุด

- Production build และ TypeScript ผ่าน
- `node scripts/check_reading.cjs` ผ่าน7กลุ่ม:ข้อมูล/สุ่ม/state guard/ความหมายทุกสถานะ/summaryเปลี่ยนตามบริบทและใบ2/3
- `../.venv/bin/python scripts/check_reading_ui.py` ผ่าน12กลุ่มบนChromium รวมสับจริงเกิน60วินาที,หยุดโดยไม่resetpose,เลือก/คืน/เปิด/ปลดล็อก,มือถือ360/390/430px,keyboard,resize,reducedmotion,fallback
- หน้าเดิม `scripts/check_reveal.py` ผ่าน11กลุ่ม
- หลักฐาน: `artifacts/reading/`, `artifacts/reveal-three-card-regression/` และ `VERIFY.md`
- ยังไม่ทดสอบSafariบนอุปกรณ์จริงหรือHostinger และยังไม่ได้deploy

## ข้อจำกัดที่ต้องรักษาให้ตรงจริง

- มีภาพไพ่ติดตั้งบนเว็บ5ใบ;อีก73ใบแสดงกรอบสำรองพร้อมชื่อ ห้ามเอาภาพใบอื่นมาแทน
- มี468ช่องความหมายจากแชทที่เจ้าของให้ แต่ยังรอเจ้าของทบทวนก่อนบริการจริง
- บทสรุปสามใบเป็นdemoที่เรียงความหมายตามตำแหน่ง ยังไม่มีวิธีอ่านไพ่ประกอบจากเจ้าของที่ผ่านรับรอง
- หมวดงาน/เงิน/ชีวิตรอความรู้ แสดงข้อความสาธิต ไม่แต่งคำทำนายเป็นความรู้ของแฟนเจ้าของ
- คำถามอิสระใช้แสดงบริบท ยังไม่ตีความด้วยAI
- ไม่มีbackendดูดวง,บัญชี,ประวัติถาวร,AI API หรือการชำระเงินจริง;refreshเริ่มรอบใหม่
- ปุ่มปลดล็อกเป็นdemoเท่านั้น;เก็บเงินจริงภายหลังต้องตรวจสิทธิ์บนserverก่อนส่งคำอ่าน ห้ามใช้CSSซ่อนข้อมูลที่ขายจริงแล้วถือว่าปลอดภัย

## งานต่อที่ยังไม่ได้สั่งให้ลงมือ

1. รับfeedbackเจ้าของต่อUI/จังหวะสับ/การเลือกไพ่ แล้วปรับเฉพาะจุดที่ขอ
2. นำภาพอีก73ใบที่เจ้าของยืนยันแล้วเข้าระบบตามcard IDเดิม
3. เจ้าของทบทวนความหมายและเพิ่มวิธีอ่านสามใบ/กรณีตัวอย่าง ก่อนทำระบบสังเคราะห์จริง
4. Second Brain:ความหมายรายใบ→กฎประกอบ→เคสที่ลบข้อมูลระบุตัวบุคคล→สำนวนเจ้าของ;ทุกชุดมีsource/review status/version
5. ระบบชำระเงินและเผยแพร่เป็นระยะถัดไป ยังไม่เลือกราคา/providerและยังไม่มีการอนุมัติdeploy

## สายงานอื่นที่ต้องรู้

- Gemini web runnerรุ่น1.3.0อยู่ `tools/gemini-web-runner/`;runtimeแยกในโฟลเดอร์เดียวกันนอกiCloud ใช้Chrome extensionแทนpaidAPI แก้blob downloadแล้ว;ห้ามส่งpromptซ้ำให้ใบที่generatedแต่ดาวน์โหลดค้าง อ่านREADMEและwikiก่อนrecover
- ชุดพรอมต์78ใบอยู่ `animations/tarot-pilot/prompts-78/` พรอมต์ครบไม่เท่ากับภาพครบ
- Halloween animationล่าสุดv3มีสับ/ถือไพ่/กระพริบตาอยู่ `animations/halloween-2026/` และruntime;ไม่เจนทับart styleโดยอัตโนมัติ
- Social Center ยังไม่มีข้อมูลบัญชี/โพสต์/metricจริงที่เชื่อมแล้ว ตามHANDOFFเดิม;อย่าอ้างตัวเลขจริงหรือยิงsyncโดยเดาtoken

## Git และข้อมูลส่วนตัว

Repositoryเป็นpublic. `.gitignore`กัน`.env*`,rawส่วนตัว,ฐานข้อมูล,cache/build,ZIP,คลิปและฟอนต์ระบบ. ไฟล์เหล่านี้ยังอยู่ในเครื่อง;บางลิงก์rawในwikiจึงเปิดไม่ได้จากpublic clone. อย่าแก้ให้ไฟล์ส่วนตัวถูกtrackเพื่อเพียงแก้ลิงก์เสีย

คุยภาษาไทย;rawเพิ่มได้อย่างเดียว;ห้ามส่งข้อมูลส่วนบุคคลออกบริการภายนอก;tokenใช้Keychain;ไม่แตะ`.obsidian/`;เปลี่ยนwikiต้องอัปเดตindexและappendlog. เครดิตHiggsfieldต้องตรวจราคาจริงและได้รับอนุมัติก่อนใช้ ห้ามโพสต์/ส่งข้อความ/เผยแพร่โดยไม่มีคำสั่ง

## ข้อความเริ่มงานสำหรับ Claude Code

> อ่าน AGENTS.md, CLAUDE.md และ CLAUDE_HANDOFF.md ในโฟลเดอร์ MaeMorKratai ก่อน แล้วตรวจ HANDOFF.md กับ git status. โปรเจกต์เว็บรันจาก ~/AIVideoLocal/maemorkratai/tarot-web และสำรองใน web/tarot. คุยภาษาไทย รอคำสั่งงานถัดไป ไม่เจนภาพ ไม่ใช้เครดิต และไม่deployเอง.

## อัปเดตชื่อภาพไพ่ — 2026-10-16

เจ้าของยืนยันชื่ออังกฤษเดิม: runner 1.3 และพรอมต์ 78 ใบรองรับ title-v1, เพิ่มชื่อภาพเดิม และ ref ภาพตัวอักษรที่เจ้าของอนุมัติ คู่มือ runner ด้านบนเป็นจุดเริ่มต้น คิวเก่าและไฟล์ไม่มีชื่อยังคงอยู่ ไม่มีการเจนจริงหรืออนุมัติภาพแทนเจ้าของ; ภาพ/ref ที่นำเข้าอยู่ในหน่วยความจำแท็บ ต้องเลือกใหม่หลัง refresh

## Gemini runner 1.4.0 — 2026-10-17

ดู [[gemini-pro-card-repair-source-2026-10-17]]: Pro model picker เป็นค่าเริ่มต้น/ตรวจซ้ำก่อนส่ง; โหมดซ่อมภาพเดิมเลือกกรอบหรือคิ้ว โดยรักษาภาพและชื่อ คิว repair-v1 แยกจากเดิม; attempt history และไฟล์เก่าคงอยู่ ผล cards-repaired/v1 ต้อง owner review ไม่มี auto visual QA. Emperor เริ่มซ่อมกรอบ; Chariot เริ่มเติมคิ้ว. พรอมต์สองใบพร้อมใช้ใน tools/gemini-web-runner/repair-prompts. Google แยก Pro chat กับ Nano Banana Pro (Redo with Pro); ตัวช่วยยังไม่กด Redo เพิ่มเอง. อัปเดตคู่มือ/ZIP/สำรอง runtime แล้ว อ่านผลทดสอบ tests/artifacts; ไม่มีการเจนภาพจริงหรือเปลี่ยน JPG ใน Downloads ในงานนี้
