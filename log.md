# บันทึกโครงการ

## [2026-10-14T17:25:10+07:00] schema | เริ่ม vault

สร้างคลังแยกตาม [[maemorkratai-project-brief]] ยังไม่เชื่อมบัญชีหรือใช้เครดิต

## [2026-10-14T19:51:44+07:00] query | ตรวจและส่งมอบระบบ local

เพิ่ม [[implementation-validation]] และ [[implementation-validation-source-195143]]; ติดตั้ง LaunchAgent; สำรองโค้ด; บัญชีจริงยังรอเจ้าของเชื่อม; ไม่ใช้เครดิต

## [2026-10-14T19:51:44+07:00] query | รายงาน Social Audit

เพิ่ม [[social-audit-2026-10-14-195144-0700-b0dd39]] จาก [[social-audit-2026-10-14-195144-0700-b0dd39-source]]; ไม่มีการเจนหรือเผยแพร่

## [2026-10-14T21:19:07+07:00] ingest / implement | Next.js + Meta setup + silent mascot brief

เปลี่ยนหน้าเว็บหลักเป็นNext.js เพิ่มverify/account-media evidence เก็บเอกสารMetaและreferenceจากเจ้าของ มีคู่มือ [[social-api-connection-guide]], [[character-and-silent-animation-brief]], [[silent-animation-prompts]], [[nextjs-implementation-validation]]; ownerยังไม่มีApp/ข้อมูลจริงยังว่าง; SQLiteเดิมรักษาไว้; ไม่ใช้เครดิต

## [2026-10-14T21:30:07+07:00] query | รายงาน Social Audit

เพิ่ม [[social-audit-2026-10-14-213007-0700-61bb07]] จาก [[social-audit-2026-10-14-213007-0700-61bb07-source]]; ไม่มีการเจนหรือเผยแพร่

## [2026-10-14T21:30:08+07:00] query | รายงาน Social Audit

เพิ่ม [[social-audit-2026-10-14-213008-0700-794f13]] จาก [[social-audit-2026-10-14-213008-0700-794f13-source]]; ไม่มีการเจนหรือเผยแพร่

## [2026-10-15] implement / verify | ฉากจบภาพวาด + Halloween 2026

ส่งมอบ [[illustrated-endcard]] และ [[halloween-2026-endcard]]; เก็บเทมเพลตในanimations/และMP4ในFinalResult/; ตรวจStudio/MP4/iframe/scrubผ่าน อัปเดต[[brand]]ให้แยกร่าง3Dplushเดิมจากคำขอคงภาพวาดล่าสุด; แหล่งหลักฐาน [[illustrated-animation-delivery-source-2026-10-15]]; ใช้เครดิต0 ไม่เปลี่ยนระบบSocialAPI

## [2026-10-15] revise / verify | Halloween v2 สับไพ่และโชว์ไพ่

เจ้าของชอบภาพรวมv1 ขอแก้เฉพาะท่ามือ ใช้มือจากภาพเดิมสับสามรอบ หยิบ/พลิก/ถือโชว์ ส่งออกMaeMorKratai_Halloween_2026_v2.mp4; อัปเดต[[halloween-2026-endcard]]ตาม[[halloween-v2-shuffle-source-2026-10-15]]; ตรวจMP4/iframeผ่าน เก็บv1ไว้เทียบ0เครดิต

## [2026-10-15] ingest | ความหมายไพ่78ใบและสุ่ม5ใบทดลอง

อ่านแชทที่เจ้าของให้ เก็บrawใหม่และสร้าง78หน้าไพ่ตาม[[tarot-love-chat-source-2026-10-15]]; มี468ช่องความหมาย6สถานะ พร้อมที่มาระดับmessage/บรรทัด สุ่ม5แบบไม่ซ้ำบันทึกselection; ยังรอทบทวนเนื้อหาบริการจริง; ดู[[tarot-knowledge-base]]

## [2026-10-15] implement / verify | เว็บไพ่5ใบและHalloween v3

ส่งมอบ[[tarot-web-prototype]]พร้อมstaticHostingerZIPและ[[halloween-2026-endcard]]v3กระพริบตา;5ภาพHyperFrames/GSAP,ตรวจ5draws/30readingsและmobileผ่าน. หลักฐาน[[tarot-web-delivery-source-2026-10-15]];78หน้าไพ่/468ช่องคำอ่านในคลัง.0เครดิต ยังไม่deploy.

## [2026-10-15] implement / verify | ภาพไพ่ใหม่และแสงเปิดไพ่

อัปเดต[[tarot-web-prototype]]ใช้JPEG5ใบจากเจ้าของ พร้อมGSAPแสง/flip/return/toggle,คำอ่านเต็ม6สถานะและreducedmotion;ตรวจ5ไพ่30คำอ่าน/desktop/mobileผ่านตาม[[generated-deck-reveal-source-2026-10-15]].0เครดิต ไม่deploy;เก็บภาพSVGและชุดwebv1ไว้เทียบ.

## [2026-10-15] create / verify | พรอมต์Geminiภาพไพ่ครบ78ใบ

สร้างพรอมต์รวมและTXTพร้อมใช้78ไฟล์ พร้อมmanifestและZIP ตาม[[tarot-gemini-prompts-source-2026-10-15]];อัปเดต[[tarot-knowledge-base]]. ตรวจ78id/หมวด22+14×4/คำสั่งคุมสไตล์ครบ ไม่เจนไม่ใช้เครดิต ไม่เปลี่ยนสำรับเว็บ.

## [2026-10-16] implement / verify | Gemini web runner ไม่ใช้API

ส่งมอบ[[gemini-web-card-runner]]พร้อมZIPและตัวเปิดติดตั้ง ใช้78พรอมต์/แนบภาพเดิมทุกครั้ง ค่าเริ่มต้นข้าม5ภาพ/ทำ1ใบ;ตรวจ8DOMcases+5backgroundcasesผ่านตาม[[gemini-web-runner-source-2026-10-16]].ยังไม่ติดตั้งในChromeเจ้าของหรือเจนจริง;0APIcalls/0ภาพเจน.

## [2026-10-16] fix / verify | Gemini runner ใบค้างTheMagician

ตาม[[gemini-web-runner-recovery-source-2026-10-16]]อัปเดต[[gemini-web-card-runner]]1.0.1:แสดงขั้นค้าง/สาเหตุแรกและวิธีUNSENT/SAVED.9regressionผ่าน;ยังไม่ยืนยันสาเหตุที่รอบแรกค้างหรือทดสอบเจนจริง.0APIcalls/0ภาพเจน.

## [2026-10-16] fix / verify | Gemini runner1.1.0 ตรวจช่องพิมพ์

ตามภาพเจ้าของและ[[gemini-web-runner-dom-source-2026-10-16]]แก้[[gemini-web-card-runner]]ให้เลือกช่องAskGeminiเอง/ค้นDOMหลายแบบ/แนบpasteหรือเมนู+/แสดงrecoveryerror;13fixturecasesผ่าน.ยังไม่เจนบัญชีจริง0APIcalls.

## [2026-10-16] fix / verify | Gemini runner1.2.0 ดาวน์โหลดblob

จากprogressเจ้าของตาม[[gemini-web-runner-blob-source-2026-10-16]]พบblobถูกปฏิเสธก่อนdownloadId;แก้[[gemini-web-card-runner]]ให้อ่านbytes/ชนิดไฟล์จริง,เก็บgeneratedเดิมไม่ส่งพรอมต์ซ้ำ,เปิดไฟล์ตำแหน่งจริง.ผ่าน16DOMfixturecases+8backgroundcasesและactualMV3downloadบนfixture.0paidAPIcalls/0genบัญชีเจ้าของ.

## [2026-10-16] implement / verify | ห้องไพ่สามใบจากสำรับ78

ทำหน้า/reading/ตามแผนเจ้าของ:หมวด/สถานการณ์→สับจนหยุด→เลือก3→อดีต/ปัจจุบัน/อนาคต→ปลดล็อกdemo. สำรองweb/tarotและอัปเดตZIPโดยเก็บรุ่นก่อน. Build/typecheck/domain7/UI12/regression11ผ่าน ตาม[[tarot-three-card-source-2026-10-16]];อัปเดต[[tarot-web-prototype]].5ภาพจริง73กรอบสำรอง;คำอ่านรอทบทวน;ไม่มีAI API/เครดิต/เงินจริง/deploy.

- ตรวจYAML/raw references/wikilinks/indexเฉพาะหน้าที่เปลี่ยนผ่าน;full-vault lintหยุดหลังอ่านไฟล์conceptเก่าบนiCloudช้าต่อเนื่องเกิน100วินาที ไม่ถือว่าตรวจทั้งvaultผ่าน. ไม่กระทบผลbuild/domain/UI/regressionเว็บที่ผ่านแล้ว.

## [2026-10-16] setup / handoff | เชื่อมGitHubและเตรียมส่งต่อClaude

ตามคำสั่งเจ้าของตั้งorigin=https://github.com/riwjung/MaeMorKratai.gitบนmain;สร้าง.gitignoreกันsecrets/raw/ฐานข้อมูล/ZIP/วิดีโอ/ฟอนต์ระบบ;Gitmetadataอยู่นอกiCloud. เพิ่ม[[GIT]]และ[[CLAUDE_HANDOFF]];CLAUDE.md/READMEชี้เอกสารรับงานต่อ;สถานะการpushตรวจจากgit logกับorigin/main.
