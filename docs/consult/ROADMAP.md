# Roadmap ตามเกณฑ์ผ่าน

อัปเดต 5 พ.ย. 2026. ลำดับด้านล่างเป็นข้อเสนอสำหรับ consult; ยังไม่มีประมาณเวลาหรือวันรับปากเปิด paid service. ขนาดงานต้องประเมินหลังตรวจโค้ด/ข้อมูลที่ได้รับสิทธิ์.

| ขั้น | สถานะ | ผลส่งมอบ | ผ่านขั้นเมื่อ |
|---|---|---|---|
| 0. หน้าไพ่/แบรนด์ | ใช้งานแล้ว | รายวัน78ใบ, ภาพ74ใบ, ประสบการณ์3ใบdemo | รักษา build/UI; เติมภาพ4ใบ/ข้อความที่ขาดตามเจ้าของ |
| 1. เก็บคำอ่าน | มีระบบและเก็บตัวอย่างแล้ว | 60เคส/4หมวด, เสียง/ข้อความ, 40development+20holdout | ยืนยันสถานะ owner review ปัจจุบันและฟังตรวจ ASR |
| 2. Knowledge release | **งานถัดไป** | card rules, intent/position rules, ไพ่ร่วมกัน/ใบขยาย, styleและขอบเขตที่รับรอง | มี provenance/รุ่น/owner sign-off แยกจาก original; ไม่เอา holdout answers เข้าระบบค้น |
| 3. Reading engine pilot | ยังไม่สร้าง | Aกฎ/template และ B optionalLLMจากหลักฐานเดียวกัน; คำถามเพิ่ม/ส่งคน | สอบแบบไม่เห็นชื่อวิธี, evidenceตรงไพ่, รายงานความผิดพลาด/เวลา/ต้นทุน |
| 4. เว็บลูกค้า3+1ใบ | ยังไม่เชื่อม | login/history/API, ไพ่และใบขยายล็อกฝั่งserver, ownerรับเคสต่อ | end-to-end/RLS/ข้อมูลรุ่นถูกต้อง/ไม่เปิดใบ4ก่อนเวลา |
| 5. Paid beta | ยังไม่สร้าง | checkout, webhook, credit ledger/reservation, reconciliation | กดซ้ำ/เว็บฮุกซ้ำไม่เก็บซ้ำ; refund/failure recoveryผ่าน; policy/priceตกลง |
| 6. Admin Dashboard | มีเฉพาะworkshop/localSocial | รวมความรู้/คำอ่าน/เคสติดปัญหา/ยอดขาย/เครดิต/การตั้งค่า | roleชัดเจน/audit/export/backup; หน้าแสดงสถานะจากข้อมูลจริง |
| 7. Content Studio pilot | pipelineในเครื่องมีแล้ว | หน้าเลือกซีรีส์/ตอน/template → job → worker → preview | templateหนึ่งแบบทำครบ, ปิดbrowserแล้วงานไม่หาย, retryไม่เสียเครดิตซ้ำ, ownerreviewก่อนเผยแพร่ |
| 8. Content Studio production | ยังไม่สร้าง | provider adapters, library/version, queue/workerหลายงาน, scheduling/publishและanalytics | load/cost/quota/cleanup/restore/revokeผ่าน; providerและสิทธิ์assetพร้อม |

ขั้น 6–7 วางแบบคู่ขนานกับ engine ได้ แต่การทำ dashboard/ปุ่ม generate ไม่ได้ทำให้ knowledge หรือ backend พร้อมโดยอัตโนมัติ. เริ่ม pilot จากกลุ่มเล็กและการวัดผลจริง.

## งานที่แบ่งเป็น PR ถัดไปได้

1. **ADR/contract:** ตรวจ docs นี้, ตกลง domain/Auth/RLS, data ownership, API boundary และ environments
2. **Knowledge release v1:** ตรวจสถานะ review ด้วย owner, สกัด development เป็นกฎที่อธิบายได้, เพิ่ม release approval และ validation; เก็บ holdout privateแยก
3. **Engine A + evaluator:** deterministic lookup/position rules/ขอบเขต พร้อม trace และชุดทดสอบที่ไม่ได้คัดลอกจากคำตอบที่กำลังพัฒนา
4. **B adapter + blind comparison:** ใช้ providerที่เลือกหลังอนุมัติงบ เปรียบเทียบกับ A จาก inputs เดียวกัน; ยังไม่ต้อง fine-tune
5. **Customer API and ledger prototype:** แยกจากข้อมูลจริง ทดสอบ transaction/concurrency ก่อนผูก providerและหน้า checkout
6. **One content job:** ยก pipelineที่มีหนึ่งtemplateมาเป็นคำสั่งรับ config และคืน artifactmanifest; ทำqueue/APIทีละชั้น

## เกณฑ์คุณภาพที่เสนอให้ตกลงกับแม่หมอ

- ไม่มีข้อผิดพลาดร้ายแรงในชุดตรวจที่กำหนด เช่น ชื่อไพ่/ตำแหน่งผิด, ใช้ใบขยายก่อนเปิด, แต่งเหตุการณ์ส่วนตัว, สรุปเกินหลักฐาน
- เป้าหมายเดิมสำหรับ pilot คือ ownerยอมรับอย่างน้อย18/20holdout และสำนวนเฉลี่ย4/5 — เป็นเป้าทดลอง ยังไม่ใช่ผลที่ได้; จำนวนตัวอย่างน้อยต้องรายงานแยกหมวดและจำนวนเคส
- รายงานตอบได้/ถามเพิ่ม/ส่งคน แยกจากคะแนนคำตอบ เพื่อไม่ให้ระบบผ่านด้วยการส่งทุกเคสให้คน
- วัดเวลารอ/costต่อคำถาม/อัตราfail และต้นทุนต่อผู้ใช้หนักก่อนออกแพ็กไม่อั้น
- เรื่องสุขภาพไม่ตีความเป็นการวินิจฉัยโรค; ต้องกำหนด scope คำถามอ่อนไหวและข้อความที่แม่หมอรับรองก่อนปล่อยใช้งานจริง

## หนี้ทางเทคนิคที่ต้องเห็นก่อนประเมินราคา

- Productionเว็บหลักเคย deployจากCLI snapshot; Gitนี้เป็นฐานให้ consult และยังไม่รับรองว่าเปิด Git auto-deployแล้ว
- หน้าแรกเป็นstatic; ถ้าจะใส่ APIในแอปเดียวต้องแก้ deployment modeอย่างตั้งใจ
- ซอร์สคำอ่านรายวันเก็บmetadata reviewเก่าตามsnapshot; READMEบันทึกอนุมัติ5พ.ย. ควรเพิ่มpublication record/versionที่เครื่องอ่านได้ในรอบknowledge release
- ใบขยายมีในworkshop แต่ไม่มีในเว็บลูกค้า; วิธีscopeคำถามและรวมหลายไพ่ยังไม่เป็นproductionengine
- Sourceคลิปมีlocal pathsและต้องใช้GLB/เสียง/เครื่องมือที่ไม่ได้แจกผ่านpublicGit; ต้องทำassetmanifestและworkercontractก่อนย้ายขึ้นcloud
