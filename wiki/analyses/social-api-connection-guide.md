---
type: analysis
title: เชื่อม Facebook และ Instagram ทีละขั้น
aliases: []
tags:
- domain/maemorkratai
created: '2026-10-14'
updated: '2026-10-14'
status: ready-for-owner-setup
sources:
- '[[meta-connection-source-2026-10-14-211907-0700-e3302c]]'
---

# เชื่อม Facebook และ Instagram ทีละขั้น

**สถานะ:** ยังไม่ได้สร้างหรือยืนยัน Meta App ของช่องในเซสชันนี้ ยังไม่มีผลตรวจบัญชีจริง ข้อมูลช่องจะเริ่มปรากฏหลังเจ้าของให้สิทธิ์และซิงก์สำเร็จ

หน้าเว็บใหม่ใช้ Next.js ที่ [http://127.0.0.1:3000/#connect](http://127.0.0.1:3000/#connect) และเรียก API ภายในเครื่องที่พอร์ต 8787 ผ่านเซิร์ฟเวอร์ ฐานข้อมูลรอบนี้ยังเป็น SQLite การย้ายไป PostgreSQL เป็นขั้นถัดไป หน้าเว็บไม่ต้องใช้ App Secret และไม่ต้องส่ง token ผ่านแชต

## 1. เตรียมบัญชีของเจ้าของ

1. เข้าบัญชี Facebook ของคุณหรือแฟนที่จัดการเพจแม่หมอกระต่ายได้ เปิด Page Settings → Page access ตรวจว่าอ่าน Insights ได้
2. เปิด Instagram `@maemorkratai` ตรวจ Account type and tools ว่าเป็น **Business หรือ Creator** หากยังเป็น Personal ให้เปลี่ยนเป็น professional account
3. เปิด Facebook Page → Settings → Linked accounts → Instagram แล้วเชื่อม `@maemorkratai` ให้ตรงบัญชี การผูกบัญชีผ่าน Accounts Center อย่างเดียวไม่ได้ยืนยันการเชื่อมเพจที่ระบบต้องใช้

ระบบนี้ใช้ **Instagram API with Facebook Login** ซึ่งต้องมี professional IG เชื่อมกับ Facebook Page เส้นทาง Instagram Login เป็นอีกวิธีที่มีข้อกำหนดต่างกัน จึงไม่ใช้ token จากวิธีนั้นมาวางในระบบนี้ [เอกสาร Meta](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api)

## 2. สร้าง Meta App และกำหนดผู้ทดสอบ

1. เปิด [Meta App Dashboard](https://developers.facebook.com/apps/) และสร้างแอปของโครงการแม่หมอกระต่าย
2. เลือก use case/product ที่รองรับ **Instagram API with Facebook Login และการอ่านข้อมูล Pages** หากขั้นตอนมีประเภท Business ให้เลือกตามความสามารถนี้ ชื่อเมนูอาจต่างกันตามบัญชี
3. ใน App roles เพิ่มบัญชีเจ้าของที่มีสิทธิ์เพจตามบทบาทที่ Dashboard รองรับ ผู้ถูกเพิ่มต้องยอมรับคำเชิญก่อน
4. เปิดส่วน Permissions and Features หรือการตั้งค่า use case ตรวจสิทธิ์ที่แอปใช้ได้จริง หาก Meta ขอ Advanced Access, App Review หรือ Business Verification ให้ทำตามเงื่อนไขที่ Dashboard แสดง การมี App role ไม่รับประกันว่าจะข้ามข้อกำหนดทุก permission ได้

การทดลองเริ่มจากบัญชีเจ้าของ หากจะให้ผู้ใช้อื่นเชื่อมบัญชีในอนาคต ต้องตรวจข้อกำหนดอีกครั้งก่อนเปิดบริการ

## 3. สร้าง User Access Token

1. เปิด [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. ใน Meta App เลือก **แอปที่เพิ่งสร้างของโครงการนี้** ไม่เลือกแอปตัวอย่างหรือแอปอื่น
3. เลือก API version ที่ App Dashboard รองรับ และจำค่ารูปแบบ `vXX.X` สำหรับกรอกในเว็บ ไม่ใช้ version จากตัวอย่างเก่าโดยอัตโนมัติ
4. เลือก Get User Access Token ระบบต้องการ **User token** ในขั้นค้นหาเพจ ไม่ใช้ App token หรือ Page token แทน
5. เพิ่มรายการสิทธิ์เริ่มต้นเพื่ออ่านช่องและ Insights แล้วตรวจ availability ใน Dashboard ของแอปจริง:

   | สิทธิ์ที่ต้องตรวจ | ใช้ตรวจอะไร |
   | --- | --- |
   | `pages_show_list` | รายการเพจที่เจ้าของให้แอปเข้าถึง |
   | `pages_read_engagement` | ข้อมูลและปฏิสัมพันธ์บนเพจ |
   | `read_insights` | Facebook Insights ตาม endpoint ที่ใช้ |
   | `instagram_basic` | ข้อมูลบัญชี IG และสื่อ |
   | `instagram_manage_insights` | IG Insights |

6. สำหรับคอมเมนต์ ให้ตรวจ `instagram_manage_comments` ของ IG และ `pages_read_user_content` ของ Facebook เพิ่มตาม endpoint และข้อมูลที่ต้องอ่านจริง ไม่เพิ่ม publishing, messaging หรือ ads สำหรับรอบนี้ สิทธิ์ชื่อ manage อาจให้ความสามารถเขียนได้ด้วย แต่ตัวเชื่อมของระบบอ่าน Meta ด้วย GET เท่านั้น
7. กด Generate Access Token เข้าบัญชีเจ้าของ และในหน้าขออนุญาตเลือกเพจแม่หมอกระต่ายกับ IG ที่ถูกต้อง หากมีตัวเลือกให้แก้รายการทรัพยากร อย่าปล่อยเพจนี้ออกจากรายการ

รายการ permission เป็นแนวทางสำหรับตรวจแอปจริง ไม่ใช่หลักฐานว่าบัญชีได้รับทุกสิทธิ์แล้ว เอกสาร Meta Postman ครอบคลุมหลาย workflow รวมถึง publishing จึงไม่ควรคัดลอก permission ทั้งชุดโดยไม่ตรวจความจำเป็น

## 4. ตรวจ token ก่อนนำเข้าระบบ

1. เปิด [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/) ของ Meta
2. ตรวจว่า token valid, App ID ตรงแอปโครงการ, Type เป็น User และ scopes ตรงสิทธิ์ที่อนุญาต
3. ดูวันหมดอายุที่เครื่องมือแสดง หากมี Extend Access Token ให้ใช้และตรวจ token ที่ได้อีกครั้ง ห้ามถือว่า token ใช้ได้ตลอดไป
4. token อาจถูกยกเลิกเมื่อเจ้าของถอนการอนุญาต สิทธิ์เพจเปลี่ยน หรือ Meta ยกเลิกสิทธิ์ ระบบยังไม่มีการต่ออายุ User token อัตโนมัติ เมื่อจำเป็นต้องกลับมาสร้างและเชื่อมใหม่

อย่านำ token หรือ App Secret ใส่ภาพหน้าจอ โพสต์ แชต URL ที่แชร์ หรือไฟล์ใน Obsidian

## 5. เชื่อมในเว็บแม่หมอกระต่าย

1. เปิด [เมนูเชื่อมบัญชี](http://127.0.0.1:3000/#connect)
2. กรอก API version เดียวกับที่เลือกใน Explorer และวาง **User token ในช่องรหัสผ่านบนเครื่องเท่านั้น**
3. กดตรวจบัญชี ระบบอ่าน permissions และค้นหาเพจ เก็บ token ที่ Meta ยอมรับใน macOS Keychain
4. เลือกเพจแม่หมอกระต่าย ตรวจว่า IG ที่แสดงตรง `maemorkratai` ระบบหาค่า Page ID และ IG ID จาก Meta จึงไม่ต้องใช้ลิงก์แชร์ Facebook แทน ID
5. ขั้นเลือกเพจอ่าน Page token และเก็บใน Keychain วิธีค้นหาเพจและบัญชี IG ที่เชื่อมอยู่แสดงใน [ตัวอย่าง `/me/accounts` ของ Meta](https://www.postman.com/meta/instagram/request/lpx8lul/get-access-tokens-of-pages-you-manage)
6. กดตรวจการเชื่อมสด ดูผล Facebook identity, IG identity และสิทธิ์ที่ขาด การบันทึก ID แล้วเป็นเพียงการตั้งค่า ไม่ได้พิสูจน์ว่า token ยังใช้ได้ในขณะนี้
7. กดซิงก์ แล้วดูสถานะของ posts/media, comments และ Insights แยกกัน เก็บได้บางกลุ่มไม่ได้แปลว่าทุกกลุ่มได้รับสิทธิ์แล้ว

## 6. ตรวจว่าข้อมูลใช้วิเคราะห์ได้

- ชื่อเพจและ IG ต้องตรงบัญชีเจ้าของ
- ตรวจเวลาซิงก์ล่าสุด ช่วงเวลาที่เก็บ และจำนวนรายการที่ API คืน
- เปรียบเทียบอย่างน้อย 10 โพสต์ หรือทั้งหมดถ้ามีน้อยกว่า โดยใช้ metric และช่วงเวลาเดียวกับข้อมูลต้นทาง
- ค่าที่ API ไม่รองรับหรือไม่คืนข้อมูลต้องแสดงว่าไม่มีข้อมูล ไม่ใช้ศูนย์แทน และไม่เท่ากับบัญชีหลุด
- หลังซิงก์แล้วจึงวิเคราะห์ mood, tone และรูปแบบจากโพสต์จริงร่วมกับภาพตัวละครและวิดีโออ้างอิง ไม่สรุปสไตล์ทั้งช่องจากชื่อบัญชีเพียงอย่างเดียว

## แก้ปัญหาที่พบบ่อย

| อาการ | ตรวจและแก้ |
| --- | --- |
| รายการเพจว่าง | ตรวจว่า Explorer เลือกแอปถูก บัญชีเป็น App role และยอมรับคำเชิญแล้ว มี `pages_show_list` และเลือกเพจนี้ใน asset consent ลองสร้าง token ใหม่หลังแก้สิทธิ์ |
| พบเพจแต่ไม่พบ IG | ตรวจ IG professional type และ Page Settings → Linked accounts ว่าเชื่อม `@maemorkratai` จริง หากพบชื่อ IG อื่นต้องเลือกหรือเชื่อมเพจให้ถูกก่อน |
| พบ IG แต่ไม่อ่านชื่อ/สื่อ | ตรวจ `instagram_basic` และสถานะการอนุญาตใน App Dashboard แล้วสร้าง User token ใหม่ให้ตรง scopes |
| อ่านโพสต์ได้แต่ Insights ไม่ได้ | ตรวจ `read_insights` / `instagram_manage_insights`, Page tasks และข้อกำหนด permission ของแอป หากเสียเพียงบาง metric ให้ตรวจชื่อ metric/version/ชนิดสื่อและช่วงเวลา |
| อ่านคอมเมนต์ไม่ได้ | ตรวจ scopes สำหรับคอมเมนต์ที่ endpoint ต้องใช้และ Page access ของเจ้าของ การอ่านสื่อได้ไม่ยืนยันว่าอ่านคอมเมนต์ได้ |
| token หมดอายุหรือถูกยกเลิก | ตรวจใน Debugger สร้าง User token ใหม่และเชื่อม/เลือกเพจใหม่ ข้อมูลที่ซิงก์ไว้ยังอยู่ |
| Meta จำกัดคำขอ | ดูสถานะงานแล้วลองซิงก์ใหม่ภายหลัง ระบบเก็บข้อมูลและจุดต่อไว้ ไม่ต้องล้างฐานข้อมูล |
| Meta ขอ App Review หรือยืนยันธุรกิจ | ทำตามรายการที่ App Dashboard ระบุ ระหว่างเตรียมสิทธิ์ใช้ CSV export ของเจ้าของพร้อมตรวจ mapping และช่วงเวลา |

Page tasks มีทั้งชื่อเดิม เช่น `ANALYZE`, `MANAGE` และชื่อของ New Page Experience เช่น `PROFILE_PLUS_ANALYZE`, `PROFILE_PLUS_MANAGE`, `PROFILE_PLUS_FULL_CONTROL` ตาม [Meta SDK ทางการ](https://github.com/facebook/facebook-python-business-sdk/blob/main/facebook_business/adobjects/page.py) ต้องตรวจ capability จริงร่วมด้วย ไม่ใช้ task ชื่อเดียวเป็นหลักฐานว่าอ่าน Insights ได้

**ขอบเขตการตรวจเอกสาร:** อ่าน Meta Postman และ SDK ทางการได้ ส่วนหน้า Developer reference สำหรับ Insights/permissions/token extension ถูกจำกัดการเข้าถึงในการตรวจครั้งนี้ จึงยืนยันความพร้อมด้วย Dashboard และคำขอ API ของแอปจริงก่อนใช้งาน ไม่ระบุอายุ token แบบตายตัวหรือรับประกันการข้าม App Review


แหล่งประกอบการวิเคราะห์: [[meta-connection-source-2026-10-14-211907-0700-e3302c]]
