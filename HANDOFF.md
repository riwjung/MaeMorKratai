# สถานะส่งต่องาน — 2026-10-14

Next.js พร้อมที่ http://127.0.0.1:3000; เปิด tools/open-center.command
งานหนัก: `/Users/sawettachatsuthum/AIVideoLocal/maemorkratai`; FastAPI8787/SQLiteปัจจุบัน PostgreSQLยังไม่ย้าย

**เจ้าของตอบว่ายังไม่มีMetaApp; connected=false; ฐานช่องจริงไม่มีข้อมูลบัญชี/โพสต์/คอมเมนต์/metric**
เจ้าของสร้างApp→professionalIGlinkPage→Usertokenเฉพาะฟอร์มlocal→เลือกPage/IG→ตรวจสด→sync ตาม [[social-api-connection-guide]]

ตรวจตัวละครและคลิปอ้างอิงแล้ว: [[character-and-silent-animation-brief]]; ร่าง15วินาทีแบบไม่พูด [[silent-animation-prompts]]; pilotJSONในwiki/assets
ส่วนโพสต์จริงพร้อมแสดงcaption/mediaURL/sourceหลังsync ต้องตรวจภาพ/เสียงจริงก่อนสรุปmood/toneทั้งช่อง

pytest33ผ่าน/Nextbuildผ่าน/browserตรวจจริงผ่าน ตาม [[nextjs-implementation-validation]]
ใช้เครดิตHiggsfield0; ยังไม่เลือกโมเดล/ตรวจราคา/อัปโหลด/เจน ตรวจget_costและขออนุมัติก่อนgeneration
โค้ดสำรอง tools/social-center-source.zip ไม่รวมdata/settings/secrets/node_modules/.next

## งานแอนิเมชันล่าสุด — 2026-10-15

- [[illustrated-endcard]]: ฉากจบเดิม10s ส่งออกFinalResult/MaeMorKratai_end_credit_v1.mp4
- [[halloween-2026-endcard]]: ห้องปรุงยาHalloween12s ส่งออกFinalResult/MaeMorKratai_Halloween_2026_v1.mp4; preview127.0.0.1:3004,Studio3005
- เจ้าของต้องการคงลายเส้นภาพอ้างอิง งานนี้ใช้ภาพเดิม+SVGในฉาก2.5Dด้วยCSSperspective/GSAP ไม่ใช่โมเดล3Dplushตามร่างเดิม
- ต้นฉบับที่แก้ได้อยู่~/AIVideoLocal/maemorkratai/halloween-2026 และสำรองanimations/halloween-2026
- ตรวจและส่งออกแล้วตามVERIFY.md;0เครดิต ไม่มีอัปโหลด ยังรอความเห็นเจ้าของต่อผลงาน

### Halloween v2 — 2026-10-15

ฉบับปัจจุบัน: FinalResult/MaeMorKratai_Halloween_2026_v2.mp4 และ animations/halloween-2026/renders/MaeMorKratai_Halloween_2026_v2.mp4; มือสับสำรับ3รอบก่อนหยิบ/พลิก/ถือโชว์จนจบ ตาม[[halloween-2026-endcard]]; preview3004ชี้v2;12s/1080×1920/30fps/ไม่มีเสียง/0เครดิต; เก็บv1ไว้สำหรับเทียบ

### ล่าสุด — เว็บไพ่ + Halloween v3, 2026-10-15

- [[halloween-2026-endcard]]: v3กระพริบตา4ครั้ง เก็บสับ/โชว์จากv2; FinalResult/MaeMorKratai_Halloween_2026_v3.mp4; preview3004
- [[tarot-web-prototype]]: Next.jsแยกบน3010; runtime~/AIVideoLocal/maemorkratai/tarot-web; portable source web/tarot; staticZIP web/maemorkratai-hostinger-static.zip ยังไม่deploy
- [[tarot-knowledge-base]]:78ใบ468ช่องจากแชทเจ้าของ;ภาพทดลอง5ใบอยู่animations/tarot-pilot อีก73ใบยังไม่ออกแบบ;คำอ่านรอเจ้าของทบทวน
- QAproductionbuild/5draws/30readings/mobile/modal/reducedmotionผ่าน;0เครดิต. SocialAPI/adminเดิมคงสถานะเดิม

### เว็บล่าสุด — ภาพไพ่ที่เจ้าของเจน + แสงเปิดไพ่

[[tarot-web-prototype]]ใช้JPEG5ใบจากwiki/Images/Cardsแล้ว;overlayกลางจอพร้อมคำอ่าน,ปิดพลิกกลับ,กดใบเดิมซ้ำไม่สุ่ม,รายละเอียด6สถานะด้านล่าง. Preview3010;sourceweb/tarotและruntimeเดิม. QA11กลุ่ม+rapidcloseผ่าน,0เครดิต/ยังไม่deploy. ชุดHostingerZIPล่าสุดถูกอัปเดต;เก็บรุ่นก่อนในweb/*-v1.zip. ไพ่SVGเดิมเก็บไว้แต่เว็บไม่ใช้แสดงแล้ว.

### พรอมต์ครบ78ใบ — 2026-10-15

animations/tarot-pilot/prompts-78มีGEMINI_PROMPTS_78.md,STYLE_LOCK.txt,cards/*.txt78ไฟล์และmanifest;ZIPข้างโฟลเดอร์. ใช้IMG_5392.JPG+ไพ่ที่อนุมัติเป็นreference. ภาพ5ใบเดิมยังใช้ต่อ อีก73เป็นพรอมต์ ยังไม่เจน/ไม่ใช้เครดิต/ไม่แก้เว็บให้สุ่ม78. ดู[[tarot-gemini-prompts-source-2026-10-15]].

### Gemini เว็บอัตโนมัติ — 2026-10-16

เจ้าของเปลี่ยนไปใช้แชทGeminiเว็บเพื่อไม่เสียค่าAPI. ส่งมอบ[[gemini-web-card-runner]]ที่tools/gemini-web-runnerและZIP;runtime~/AIVideoLocal/maemorkratai/gemini-web-runner. ChromeLoadunpackedextensionครั้งเดียวแล้วเริ่ม1ใบ.78พรอมต์/JPGแนบทุกครั้ง/ข้าม5เดิม;fixture8cases+background5casesผ่าน แต่liveGeminiยังไม่ทดสอบ.0APIcalls/0ภาพเจน. รอบเปรียบเทียบGeminiAPI2โมเดลก่อนหน้าถูกหยุดและยังไม่เจน.

### Gemini runner1.0.1 — ใบค้างTheMagician

เจ้าของกดเริ่มแล้วติดduplicateguard;ยังไม่ทราบสาเหตุครั้งแรก. แสดงขั้นค้างและรักษาสาเหตุแรกแล้ว;9fixturetestsผ่าน. แนะนำตรวจแชท→ถ้าไม่เคยส่งและcomposerว่างให้UNSENT→เตรียมใบถัดไป. Reloadextension+refreshGeminiรับรุ่นใหม่. ดู[[gemini-web-runner-recovery-source-2026-10-16]].

### Gemini runner1.1.0 — ช่องพิมพ์0ตามภาพเจ้าของ

ภาพยืนยันeditor selectorไม่เจอ;UNSENTเดิมthrowเพราะeditorยังไม่เจอ. เพิ่มmanualpicker/openShadow/textarea/emptycontenteditable/lazyfileinput/paste/UNSENTerrorhandling. Reloadextension+refreshGemini→เลือกช่องพิมพ์→คลิกAskGemini→ถ้าไม่เคยส่งให้กดปุ่มปลดใบค้าง→เริ่ม1ใบ.13fixturecasesผ่าน ยังไม่ยืนยันlivegeneration. [[gemini-web-runner-dom-source-2026-10-16]]

### Gemini runner1.2.0 — blob downloadแก้แล้ว

progressจริงแสดงMagician/HighPriestess=SAVEDมือ,Empress=generated;URLblobถูกbackgroundเก่าปฏิเสธ ไม่มีdownloadId. แก้blobbytes→dataURI→ChromeDLตามMIME/filenameจริง,บันทึกใบค้าง/เลือกภาพ/เปิดFinder. Reload+refresh→บันทึกภาพใบค้างEmpress→เปิดตำแหน่งไฟล์→ตั้งbatchต่อ;ไม่ใช้UNSENTกับใบที่ได้ภาพแล้ว.16DOM+8backgroundcasesและactualMV3downloadบนfixtureผ่าน.0API/0genใหม่. [[gemini-web-runner-blob-source-2026-10-16]]

### ห้องไพ่สามใบ — 2026-10-16

[[tarot-web-prototype]]เพิ่มhttp://127.0.0.1:3010/reading/ ลูกศรจากหน้าเดิม;หมวด/สถานการณ์→สับวนจนหยุด→พัด/กริด78ใบ→เลือก3คว่ำ→เปิดอดีต/ปัจจุบัน/อนาคต→ปลดล็อกdemoฟรี. Runtimeเดิมtarot-web,สำรองweb/tarot;READING.mdมีtypes/SecondBrainแนวทาง. Build/typecheck/domain7/UI12/regressionเดิม11ผ่าน ตาม[[tarot-three-card-source-2026-10-16]].ภาพจริง5ใบ อีก73กรอบสำรอง;คำอ่าน/summaryยังรอเจ้าของทบทวน.ไม่มีAI API/เครดิต/รับเงินจริง/deploy;ยังไม่ตรวจSafariจริง. ZIPล่าสุดอัปเดตและเก็บชุดก่อนเป็น*-before-three-card-20261016.zip.
