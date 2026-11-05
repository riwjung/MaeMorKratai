# สถานะเว็บแม่หมอกระต่าย

> **สีปุ่มล่าสุด — 2026-11-05:** ตามที่เจ้าของขอ เปลี่ยนปุ่มตั้งจิตเปิดไพ่กลับเป็นสีเดิม #efb07e (เหลืองทองอมส้ม), ตัวอักษร #321c31 และ hover #ffd0a1; คงทรงแคปซูล/ขนาดพอดีข้อความ. Deploy `dpl_HGeZhAmQdZw2riVWFSBEpryDf73Z` READY ที่ https://mae-mor-kratai.vercel.app/; ตรวจสี/ทรง/ขนาดบน WebKit มือถือแล้ว.

> **ปุ่มเปิดไพ่แบบภาพอ้างอิง — 2026-11-05:** ปุ่มตั้งจิตเปิดไพ่เป็นทรงแคปซูลสีม่วง ขนาดตามข้อความประมาณ 136×46 px บนมือถือ มีดาวซ้ายและจัดกึ่งกลางใต้ฉาก. Build/TypeScript และตรวจภาพบน WebKit มือถือ/Chromium เดสก์ท็อปผ่าน. Production deploy `dpl_AaAUCu6sSX2njmEAs7j4cVL7QTD2` READY และตรวจ WebKit390px บน https://mae-mor-kratai.vercel.app/ ผ่าน (136×46px).

Production UX deployment `dpl_EAr3kQnwugr6CS6NvLmcGB3VbonR` READY. [ผลตรวจบนเว็บจริง](UX_CHECK_20261105.json) ผ่านทั้ง Chromium และ WebKit มือถือ; ปุ่มหลักอยู่ใต้ฉากก่อนตัวเลือกสถานะรัก, กรอบตรงขนาดภาพ, ไม่มีเส้นขอบเสริมหรือด้านหลังซ้อนเมื่อเปิดจบ, ดูใบเดิมไม่สุ่มใหม่.

> **ปุ่มเปิดไพ่และกรอบภาพ — 2026-11-05:** ย้ายปุ่มตั้งจิตเปิดไพ่มาเป็นปุ่มหลักใต้ฉากแม่หมอ ก่อนตัวเลือกสถานะรัก; ปุ่มดูไพ่เดิมเป็นปุ่มรอง. เอาเส้นขอบเสริมรอบหน้าไพ่ออก ซ่อนด้านหลังเมื่อพลิกจบ และใช้ขนาด WebP จริงกำหนดกรอบ. ภาพบนเว็บ 73 ใบมีขนาด 600×965; The Magician 600×894. รายงานความต่างของขนาดต้นทางและรายชื่อครบอยู่ใน [CARD_DIMENSIONS.md](CARD_DIMENSIONS.md). Build และ QA ทั้งสำรับในเครื่องผ่าน; ตรวจ WebKit แบบมีแอนิเมชันและ Chromium เพิ่มด้วย scripts/check_daily_ux.py.


> **ดวงรายวันหน้าแรก — 2026-11-05:** เจ้าของแจ้งว่าแฟนตรวจความหมายจาก [Tarot of the day](https://chatgpt.com/share/6ad48c4f-7994-83ec-a782-621e623e23c6) แล้ว จึงเปลี่ยนหน้า `/` ให้ใช้ข้อความตรงจาก `knowledge/daily/cards.v1.json` ครบ 78 ใบ (`web/tarot/lib/daily-cards.json`). แสดงธีม ภาพรวม งาน เงิน รักตาม 6 สถานะ ข้อความแม่หมอ สี และคำยืนยัน; คำอ่านหน้า `/reading/` ไม่เปลี่ยน. ความรักแบบซับซ้อนของ Major Arcana 22 ใบเป็น `null` จากต้นทางและเว็บแจ้งว่าไม่มีคำอ่าน. ภาพ v3 ยังขาด 4 ใบ: Six of Wands, Nine of Wands, Page of Pentacles, King of Pentacles. Build, QA เปิด 78 ใบ, QA มือถือ Chromium/WebKit และกรณีภาพเสียผ่านทั้งในเครื่องและ [Production](DAILY_LAUNCH_CHECK_20261105.json). Deploy production `dpl_EP1kV1bo8t4VNonPAos5NzcEr5Yq` READY/alias `https://mae-mor-kratai.vercel.app`.

บันทึกตั้งแต่หัวข้อถัดไปเป็นสถานะเวอร์ชันเก่าเพื่ออ้างอิงประวัติ.

> **ไพ่ v3-layout + เปิดห้อง 3 ใบ — 2026-10-30 (Claude):** นำเข้า 74/78 ใบจาก `Downloads/MaeMorKratai/cards-restyled/v3-layout` ผ่านโฟลเดอร์คัดแล้ว `~/AIVideoLocal/maemorkratai/tarot-cards/v3-layout-20261030/` (ไม่แก้ Downloads). ตัดไฟล์ผิดที่ตรวจด้วยตา: `ace-of-cups.jpeg`/`king-of-wands.jpeg` เป็นภาพ Strength ไม่มีตัวละคร, `six-of-wands.jpg`/`nine-of-wands.jpeg` เป็นภาพ Five of Wands, `five-of-wands.jpg` ใช้ .jpeg ที่ใหม่กว่า. **ยังไม่มีภาพ 4 ใบ:** Six of Wands, Nine of Wands, Page of Pentacles, King of Pentacles (แสดงชื่อแทน). ลบ webp v3 เก่า 14 ไฟล์ที่ไม่ถูกอ้าง (สำรองใน `backups/20261030-before-v3-layout/`). เอา Coming soon ออก: `/reading/` เปิดห้องไพ่ 3 ใบเดิม (`ReadingExperience`, ปลดล็อก demo, ยังไม่มีใบที่ 4) และลิงก์หน้าแรกเป็น "เปิดไพ่ 3 ใบ". Build/TypeScript ผ่าน; `check_launch.py` (อัปเดตจาก Coming soon เป็นห้อง 3 ใบ) ผ่าน 8 กลุ่ม, `check_reading_ui.py` 12/12 (แก้ค่าคาดภาพเก่า), `check_reading_webkit.py` 7/7 บนเครื่อง. Preview `mae-mor-kratai-2w6n75lbs-mae-mor-kratai.vercel.app` (ติด Vercel SSO). **Production ยังไม่ deploy** — ระบบสิทธิ์บล็อก รอเจ้าของสั่งเอง: `cd ~/AIVideoLocal/maemorkratai/deployments/20261030-v3-layout-3card && ../../.venv/bin/python ../../workshop-standalone/scripts/vercel.py run deploy --prod --yes`. Rollback ล่าสุดคือ `dpl_GgXzh1n1LpfyVzM8YQgE2qsLE2yS`. ซอร์สสำรองกลับ vault แล้ว ยังไม่ commit/push.

> **แก้กรอบไพ่ v3 ล่าสุด — 2026-10-26:** กรอบเปิดไพ่/ผลคำอ่าน/รายละเอียดและแกลเลอรีใช้สัดส่วนภาพแต่ละใบจากmanifest แทน1632:2624ตายตัว จึงไม่มีพื้นที่เกินบน–ล่างโดยไม่ครอปรูป. Build/TypeScriptผ่าน; localตรวจ14ภาพ+WebKitมือถือ3สัดส่วนรวม17checks และproductionตรวจHierophant/Strength/Justiceพร้อมresult/detailผ่าน. Deploy `dpl_GgXzh1n1LpfyVzM8YQgE2qsLE2yS` ที่URLเดิม. ภาพและความหมายไม่เปลี่ยน. ซอร์สใหม่ `lib/card-art.ts`; หลักฐานruntime `artifacts/card-fit-20261026/`.

อัปเดต 26 ต.ค. 2026 · เจ้าของให้เปิดไพ่หน้าแรกสำหรับทุกคน ใช้คำตอบตามไพ่ และให้หน้า4ใบเป็น Coming soon ระหว่างพัฒนาระบบเต็ม.

## ความคืบหน้าและวิธีนับ

เปอร์เซ็นต์ด้านล่างเป็น **จำนวน milestone/checklist ที่เสร็จเทียบกับขอบเขตที่ระบุ** ไม่ใช่เวลาทำงานที่ใช้ไป โอกาสสำเร็จ หรือความแม่นยำคำทำนาย. ไม่เฉลี่ยเปอร์เซ็นต์คนละขอบเขตเข้าด้วยกัน.

| ส่วนงาน | ความคืบหน้า | วิธีนับ/ข้อจำกัด |
|---|---|---|
| เก็บคำอ่านแม่หมอ | 100% | Supabase owner ส่งทบทวน60/60เคส; การกรอกครบไม่เท่ากับรับรองความรู้ |
| ภาพสำรับ v3 | 18% | มีภาพตรงรหัส14/78ใบในsnapshotที่นำเข้า อีก64ใบแสดงชื่อแทน ไม่ขวางการเปิดหน้าแรก |
| หน้าแรกสำหรับเปิดตัว | 90% ตามchecklist9/10ข้อ | Production QAผ่านแล้ว ยังเหลือแม่หมอลองอุปกรณ์จริงและอ่านตรวจคำตอบก่อนประชาสัมพันธ์; ดูchecklistด้านล่าง |
| ระบบ4ใบพร้อมAIตามแผนเต็ม | ประมาณ25% ตาม2/8milestones | ทำต้นแบบหน้าเว็บและเก็บข้อมูลครบแล้ว อีก6milestonesยังไม่เสร็จ; ไม่ใช่การรับรองว่าจะใช้เวลาอีก75% |

แปด milestone ของระบบเต็ม: (1)ต้นแบบประสบการณ์ไพ่/แบรนด์ ✓ (2)เก็บ60เคส ✓ (3)สำรอง/ถอดเสียง/จัดฉบับรับรอง (4)knowledge+style+ขอบเขตที่อนุมัติ (5)engineกฎและการถามเพิ่ม (6)LLMและตัวเปรียบเทียบA/B (7)เชื่อม4ใบ/API/คิวowner (8)holdout/production QA. รายละเอียด [แผน reading engine](../../backend/READING_ENGINE_PLAN.md).

## ขอบเขตที่จะเปิดวันที่ 31

- หน้า `/`: เปิดไพ่ฟรีโดยไม่ต้องสมัคร สุ่มหนึ่งใบจาก78ใบ ใช้ความหมายเดิมตามไพ่และสถานะความรัก6แบบ รวม468ข้อความ. ไม่เรียกAIและไม่ใช้คำอ่านห้องทดลองมาตอบโดยอัตโนมัติ.
- หน้า `/reading/`: Coming soon สำหรับไพ่4ใบ มีปุ่มกลับหน้าแรก; เข้าลิงก์ตรงก็ไม่เปิดdemo3ใบ. เก็บโค้ดประสบการณ์เดิมใน `app/reading/ReadingExperience.tsx` เพื่อพัฒนาต่อ ไม่ใช่routeสาธารณะ.
- รูปจาก `Downloads/MaeMorKratai/cards-restyled/v3` ใช้ในแกลเลอรี หน้าต่างเปิดไพ่ ผลคำอ่าน และไพ่ในมือแม่หมอ. ใบที่ไม่มีรูปแสดงชื่อ; รูปโหลดผิดพลาดก็ยังอ่านไพ่ได้. ไม่แสดงรูปเก่าคละกับv3.
- ไฟล์ต้นฉบับผู้ใช้ไม่เปลี่ยน แปลงเป็นWebPกว้างไม่เกิน600pxใน `public/cards/v3/` และใช้ชื่อไฟล์มีhashเพื่อไม่ติดcacheรูปเก่า. Manifestเก็บsourcefilename/hash. Wheel of Fortuneมีjpgและjpeg จึงเลือกjpgที่แก้ไขล่าสุดตามกฎนำเข้า.
- หน้าแรกยังเป็นการอ่านความรักตามสถานะที่เลือก ไม่ใช่แชทถามได้ทุกเรื่อง. คงคำอ่านเดิมและprovenanceที่ยังเป็น `owner-provided-chat-unreviewed`; การเปิดตัวไม่เปลี่ยนเป็นapproved knowledgeของระบบAI.

## Checklist หน้าแรก 10 ข้อ

1. เข้าใช้ได้โดยไม่สมัครสมาชิก
2. สุ่มได้ครบ78ใบและผูกcard IDถูกต้อง
3. คำอ่าน468ช่องตรงข้อมูลเดิม ไม่เรียกAI
4. รูปv3ที่มีขึ้นครบ และใบขาด/รูปเสียแสดงชื่อได้
5. หน้า4ใบและลิงก์ตรงแสดงComing soon
6. ปิด/เปิดไพ่เดิมซ้ำ/คีย์บอร์ดและแอนิเมชันใช้งานได้
7. Chromium/WebKitจำลองมือถือไม่มีล้นแนวนอน
8. Production build/TypeScript และ dependency audit ผ่าน
9. Deployเว็บหลักสำเร็จและทดสอบบนURLจริง
10. แม่หมอลองมือถือจริงและอ่านตรวจเนื้อหาหน้าแรกก่อนประชาสัมพันธ์ — ยังรอผู้ใช้ตรวจ

ข้อ1–8ตรวจในเครื่องด้วย `scripts/check_launch.py` และbuild. ผลข้อ9ต้องยึด `artifacts/launch-20261026/production-check.json` และหัวข้อล่าสุดในVERIFY ไม่ถือว่าผ่านจากการอัปโหลดอย่างเดียว. อุปกรณ์มือถือจำลองไม่ทดแทนiPhone/Androidจริง.

## ประเมินกำหนดวันที่ 31

**หน้าแรกตามขอบเขตนี้พร้อมเปิดก่อนได้** เมื่อข้อ9ผ่าน ใช้26–30ต.ค.ให้แม่หมอลองเครื่องจริง/ตรวจข้อความและทยอยเติมรูป. รูปไม่ครบ78ไม่ใช่ตัวบล็อกตามคำสั่งเจ้าของ. ยังไม่ควรรับปากระบบ4ใบ+AIเต็มรูปแบบวันที่31 เพราะยังเหลืองานความรู้ที่อนุมัติ engine การเปรียบเทียบ และการสอบ. ไม่ย้ายเส้นตายด้วยการปล่อยdemoเป็นระบบจริง.

## เติมรูปที่ทยอยเจน

ทำใน runtime `~/AIVideoLocal/maemorkratai/tarot-web`:

```sh
npm run sync:cards -- /Users/sawettachatsuthum/Downloads/MaeMorKratai/cards-restyled/v3
npm run build
```

ตัวนำเข้าจับชื่อไฟล์กับcard ID รองรับjpg/jpeg/png/webp; เลือกไฟล์ที่แก้ล่าสุดเมื่อมีหลายไฟล์ของไพ่เดียวกัน รายงานไฟล์ชื่อไม่รู้จัก และไม่แก้คำอ่าน. รูปใหม่ในDownloads **ยังไม่ขึ้นเว็บอัตโนมัติ** ต้องsync/build/ตรวจ/deployรอบใหม่และสำรองซอร์สกลับvault. ไม่ใช้ `make_web_cards.py` รุ่นเก่าแทนขั้นนี้.

## สิ่งที่ตรวจและสถานะ deployment

- Local QA:78draws/468meanings, เปิดใบเดิมซ้ำไม่สุ่มใหม่,Coming soon/กลับหน้าแรก,hashภาพครบ14ใบ,Chromium/WebKit390px และแอนิเมชันdesktopผ่าน ไม่มีpageerror/HTTPerrorในรอบปกติ.
- Next.jsเดิม16.4.0พบcritical advisoryจากnpm audit จึงอัปเดต16.4.2พร้อมlockfile; `npm install` auditไม่พบช่องโหว่ และproduction build/TypeScriptผ่าน. ไม่ใช้คำแนะนำจากข้อความbuildให้ข้ามการแก้เป็นหลักฐานความปลอดภัย.
- Production: deploy `dpl_D68DB5duzx4LzaFrofS3MFxAcKBm` สถานะREADYและalias [เว็บหลัก](https://mae-mor-kratai.vercel.app) แล้ว. QAบนURLจริงโดยไม่loginผ่านครบ8กลุ่ม รวม78draws/468meanings,Chromium/WebKitมือถือ,แอนิเมชันจริง และจำลองบล็อกภาพเพื่อทดสอบfallback; ไม่พบpageerror/HTTPerrorในรอบปกติ. [หลักฐาน](LAUNCH_CHECK.json). หน้า[4ใบ](https://mae-mor-kratai.vercel.app/reading/)แสดงComing soon.
- Deployผ่านCLIจากโฟลเดอร์แยก `~/AIVideoLocal/maemorkratai/deployments/20261026-single-card-launch` เข้าprojectเดิม `mae-mor-kratai`/root `web/tarot`; ไม่แก้workshop. ซอร์สสำรองกลับvaultแล้ว ยังไม่commit/push. ก่อนpushmainครั้งถัดไปต้องรวมชุดเปลี่ยนนี้เพื่อไม่ให้Gitauto-deployย้อนหน้าเว็บเป็นdemoเก่า. รุ่นก่อนหน้าสำหรับrollbackคือ `dpl_2ouS7kh7BDreDPHp2eZwoqxSdYtK`.
- เว็บทดลองและข้อมูลSupabaseไม่ได้เปลี่ยน ไม่มีการเรียกโมเดล/ฝึกAI/ใช้เครดิต.
