# เตรียมนำขึ้นHostingerภายหลัง

ยังไม่ได้เผยแพร่หรือเชื่อมบัญชีHostinger. ZIP maemorkratai-hostinger-static.zip เป็นไฟล์staticที่buildแล้ว ไม่ใช่โครงการหลังบ้าน.

1. ทบทวนคำอ่านและภาพไพ่5ใบ เลือกโดเมน/แพ็กเกจจริงก่อนpublish
2. ในHostinger dashboard เลือกWebsites→Create website→Custom PHP/HTMLสำหรับไฟล์ที่buildแล้ว การแสดงเมนูขึ้นกับแพ็กเกจ; เลือกโดเมนหรือโดเมนชั่วคราวตามขั้นตอนของHostinger ([คู่มือHostinger](https://www.hostinger.com/support/1583214-how-to-add-a-website-in-hostinger/))
3. อัปโหลด/แตกไฟล์ZIPให้index.htmlและ_next/,scene/,cards/,card-scenes/อยู่ที่รากเว็บของโดเมน ไม่ซ้อนอีกชั้นและไม่อัปโหลดsource/,raw/,ฐานข้อมูลหรือtoken. ทำตามFile Manager/document rootที่แผงบัญชีแสดง.
4. ทดสอบHTTPS:เปิดหน้า,เลือกสถานะ,สับไพ่,ไพ่บนมือกับผลตรงกัน,เปิดmodal,มือถือและโหลดใหม่. เว็บไซต์นี้ใช้เส้นทางจากรากโดเมน; ถ้าจะติดตั้งใต้subfolderต้องแก้basePathและassetURLsก่อนbuildใหม่.
5. เมื่อพร้อมให้ค้นหาได้ ให้ปรับrobotsในapp/layout.tsxจากnoindexและbuildใหม่ พร้อมตั้งmetadata/domainจริง.

Next.js output:'export' สร้างout/ที่ให้static web serverบริการได้ ปฏิสัมพันธ์นี้ทำในbrowserจึงไม่ต้องมีNode runtimeบนhost. หากเพิ่มlogin/ชำระเงิน/ประวัติหรือPostgreSQLภายหลัง จะต้องออกแบบbackendและเลือกบริการที่รองรับแยกจากstatic packageนี้ ([เอกสารNext.js](https://nextjs.org/docs/app/guides/static-exports)).

แพ็กเกจและโดเมนของบัญชียังไม่ได้ตรวจ จึงยังไม่รับรองว่ามีNode.jsหรือฐานข้อมูลตามแผนใดอยู่แล้ว.


## รุ่นเพิ่มหน้าไพ่สามใบ 2026-10-16

ชุด static ล่าสุดมี `reading/index.html` และ chunk ของหน้าใหม่ด้วย ต้องอัปโหลดทั้งชุดให้เส้นทาง `/reading/` ทำงานและทดสอบเข้า URL ตรง/รีเฟรช หน้าแรกยังมีบริการไพ่หนึ่งใบเดิม คำอ่านและปุ่มปลดล็อกหน้าใหม่เป็น demo ไม่ใช่ระบบรับชำระเงินจริง รายละเอียดใน READING.md. ยังไม่เผยแพร่และยังคง noindex.
