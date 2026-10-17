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

## [2026-10-16] implement / verify | Gemini runner 1.3 — ชื่ออังกฤษบนภาพไพ่

ตาม [[gemini-card-title-source-2026-10-16]] เพิ่ม title-v1 ให้พรอมต์ 78 ใบและ runner, โหมดเพิ่มชื่อภาพเดิม, นำเข้าภาพจับคู่ card id, อนุมัติ ref ตัวอักษรและแนบพร้อม art style เดิม. คิว/ไฟล์ผลมีชื่อแยกจากเดิม; รักษา legacy recovery. ตรวจ offline fixtures, สัญญาพรอมต์ 78 ใบ และ actual MV3 downloads ในโปรไฟล์ทดสอบ; รายงาน tests/artifacts. ไม่เจนในบัญชีเจ้าของและไม่มีภาพ approved reference ใหม่จริง. อัปเดต [[gemini-web-card-runner]], HANDOFF, CLAUDE_HANDOFF, README และ index.

- ผลตรวจรอบส่งมอบ: DOM 25 กรณี + background 9 กรณี + สเปกพรอมต์ครบ 78 ใบผ่าน; actual MV3 ดาวน์โหลดเดิม/รุ่นชื่อแยกกันและ bytes ตรง fixture. Full wiki lint ผ่าน 116 หน้า. ตรวจสำเนา runtime/vault และ ZIP ผ่าน; ไม่ได้กดเจนภาพจริง

## [2026-10-16] implement / verify | หน้า /reading/ — ท่าสับและกางไพ่ลื่นขึ้น (GSAP เดิม)

เจ้าของเลือกทางปรับ GSAP เดิมหลังเทียบกับ Ref2 (3D realtime), Blender และ Gemini video. สับไพ่ 24 ใบด้วย pose ต่อเนื่องบน gsap.ticker, หลังไพ่ WebP จาก SVG เดิม, ตัดเงาเบลอรายใบ, ฐานสำรับมีความหนา; หยุดแล้วรวมจาก pose ปัจจุบัน; ไพ่บินจากกองลงกลางพัดแล้วคลี่ออก; เมาส์ยกไพ่เป็นคลื่น. แก้บั๊กสำรับจางตอนรวมกอง. ชุดทดสอบเดิมผ่านครบ (7/12/11). ไม่เจนภาพ ไม่ใช้เครดิต ไม่ deploy. รายละเอียด web/tarot/READING.md และ VERIFY.md.

## [2026-10-16] implement / verify | หน้า /reading/ — สำรับ 3D three.js แบบ Ref2

เจ้าของขอให้ใกล้ Ref2 และแก้ไพ่ทะลุกันในรุ่น GSAP. เพิ่มสำรับ WebGL (three@0.186.1, โหลด lazy) ช่วงสับ→รวม→กาง: ไพ่ 78 ใบขนานกันคนละความลึก เลื่อน/หมุนในระนาบตัวเองเท่านั้น จึงไม่ทะลุกัน; ชั้นบนแตกเป็นขั้นบันได มีห่อไพ่ดึงออกแล้วเสียบกลับ ทั้งกองหมุนส่าย; หยุดแล้วรวมจาก pose ปัจจุบัน; กางลงตำแหน่งพัด DOM แบบตรงพิกเซลแล้ว fade ส่งต่อ. ส่วนเลือกไพ่ยังเป็น DOM เดิม. ไม่มี WebGL/reduced motion ใช้สำรับ DOM. ชุดทดสอบเดิมผ่าน 7/12/11 และตรวจ fallback ไม่มี WebGL. ยังไม่ทดสอบบนโทรศัพท์จริง/Safari. ไม่เจนภาพ ไม่ใช้เครดิต ไม่ deploy. รายละเอียด web/tarot/READING.md และ VERIFY.md.

## [2026-10-16] implement / verify | หน้า /reading/ — ท่าสับแบบ Moonlight (ไพ่ 30 ใบ เว้นระยะ หันข้าง)

ตามคำขอเจ้าของ วิเคราะห์ท่าสับของ app.moonlight.world จาก JS สาธารณะ (Framer Motion + CSS 3D: กองหมุนรอบแกนตั้ง 4 วินาที, ไพ่วนเป็นวงแนวตั้งรอบกอง 3 วินาที หน่วงใบละ 0.1 วินาที) ห้องตัวอย่างต้องสมัครบัญชีจึงไม่ได้เข้า. เขียนใหม่ใน three.js เอง: ไพ่ 30 ใบวนเป็นวงที่เว้นระยะชัด กองหมุนให้เห็นด้านข้าง ไพ่มีความหนาเห็นเป็นเส้น ไพ่ทุกใบหันทางเดียวกันจึงไม่ทะลุ; ตอนกางเติมเป็นพัด 78 ใบ. ชุดทดสอบเดิมผ่าน 7/12/11 และ fallback ไม่มี WebGL ผ่าน. ไม่เจนภาพ ไม่ใช้เครดิต ไม่ deploy. รายละเอียด web/tarot/READING.md และ VERIFY.md.

## [2026-10-17] implement / verify | หน้า /reading/ — ลากไพ่ลงช่องและแตะเปิดเอง

ตามคำขอเจ้าของ ขั้นเลือกไพ่ลากไพ่จากพัดไปวางในช่องอดีต/ปัจจุบัน/อนาคตที่ต้องการได้ (มือถือดึงขึ้นเพื่อหยิบ ปัดแนวนอนยังเลื่อนพัด) และแตะไพ่ในช่องเพื่อพลิกเปิดเองทีละใบ; ยังเลือกด้วยแตะ+ปุ่มและคีย์บอร์ดได้. state เปลี่ยนเป็นรายช่อง: คืนไพ่แล้วช่องว่างไว้ ไม่เลื่อนใบอื่น (ต่างจากเดิม). แก้บั๊ก hover ค้างบนจอสัมผัสและตำแหน่งไพ่ที่บินเข้าช่อง และเลื่อนหน้าให้เห็นทั้งช่องกับพัดบนมือถือ. ชุดทดสอบผ่าน 8/12/11 รวมลากด้วย touch จริงผ่าน CDP. ไม่เจนภาพ ไม่ใช้เครดิต ไม่ deploy. รายละเอียด web/tarot/READING.md และ VERIFY.md.

## [2026-10-17] implement / verify | Gemini runner 1.4 — Pro และซ่อมตำหนิภาพเดิม

ตาม [[gemini-pro-card-repair-source-2026-10-17]] ตรวจภาพตัวอย่าง Emperor/Chariot ในเครื่อง เพิ่ม Pro picker guard และโหมดซ่อมกรอบ/คิ้ว/คำอธิบาย รักษารูปและชื่อเดิม คิว/โฟลเดอร์ repair แยก, สั่งทำซ้ำหลัง downloaded ได้พร้อม history. เพิ่มข้อกำหนดกรอบ/คิ้วในพรอมต์ใหม่ทั้ง78ใบ; เตรียม repair prompts สองใบ. อัปเดต [[gemini-web-card-runner]], index, handoffs และคู่มือ. ไม่มีการเรียกเจนหรือแก้ภาพต้นฉบับจริง; ไม่แก้งานเว็บสามมิติที่กำลังทำแยกอยู่

- ตรวจรับ: DOM/flow 35 กรณี, background 10 กรณี, สเปกพรอมต์78ใบ และ MV3 downloads จริงบนfixtureผ่าน; wiki lint117หน้าผ่าน. การเลือกProยังตรวจเฉพาะDOMจำลอง และยังไม่มีภาพซ่อมจริงจากGeminiในงานนี้
