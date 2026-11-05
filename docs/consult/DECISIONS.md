# Decisions และคำถามที่ยังเปิดอยู่

## ข้อกำหนดที่เจ้าของยืนยันแล้ว

- รายวันใช้คำอ่านที่แม่หมอเลือกและตรวจแล้ว; มีหมวดงาน/เงิน/รัก ไม่จำกัดแค่ความรัก
- เว็บหลายใบเป็นอดีต–ปัจจุบัน–อนาคต และวางแผนใบที่4ขยายอนาคต. คำตอบต้องอิงไพ่/คำถามและลดการเดาเรื่องส่วนตัว
- เก็บวิธีอ่านและสำนวนของแม่หมอจากเสียง/ข้อความ; แยกoriginal/ฉบับรับรอง. ห้ามเอาdraftหรือholdoutมาเป็นapprovedknowledgeเอง
- มีDashboardของตัวเองดูแลเว็บและงานช่อง. ระยะต่อไปให้สร้างซีรีส์ไพ่จากหน้าเว็บได้
- ค่าใช้เครดิตproviderต้องตรวจราคาและอนุมัติก่อน; การสร้างและการเผยแพร่เป็นคนละการอนุมัติ

## ข้อเสนอที่ยังรอ consult / เจ้าของตัดสินใจ

| ID | เรื่อง | จุดเริ่มที่เสนอ | สถานะ |
|---|---|---|---|
| ADR-01 | appboundary/domain/Auth | เก็บ2แอปที่ออนไลน์แยกก่อน; เพิ่มcustomerAPIและadminตามPRที่ทดสอบได้ | เปิด |
| ADR-02 | engine/LLMprovider | Aกฎก่อน แล้วเทียบB; เลือกproviderจากevidence/cost | เปิด |
| ADR-03 | jobqueue/worker | durablequeueกับworkerหนึ่งตัว; เลือกบริการหลังpilottemplate | เปิด |
| ADR-04 | customerDB/knowledge schema | PostgresRLS+versionedrelease, logicalmodelในDATA_AND_PAYMENTS | เปิด |
| ADR-05 | payment/แพ็กเกจ | creditpackและverifiedwebhook/ledger; ตรวจprovidereligibilityและค่าบริการจริง | เปิด |
| ADR-06 | deploy/CI/rollback | stagingแยก, ทดสอบclonebuild, deployผูกcommit | เปิด |
| ADR-07 | reviewdataล่าสุด | ownerตรวจจำนวนapprovedปัจจุบันก่อนrelease | ต้องตรวจข้อมูลที่ได้รับสิทธิ์ |
| ADR-08 | ความหมายช่องที่ขาด/ภาพ4ใบ | ให้แม่หมอเติม/อนุมัติจากต้นทาง; ไม่สร้างเอง | รอcontent |

เมื่อมีข้อสรุป บันทึกวันที่/ผู้ตัดสินใจ/ตัวเลือก/เหตุผล/ผลกระทบ/หลักฐาน และลิงก์PRหรือissue. ข้อเสนอในrepoไม่ใช่การอนุมัติใช้providerที่เสียเงินหรือย้ายproductionแล้ว.
