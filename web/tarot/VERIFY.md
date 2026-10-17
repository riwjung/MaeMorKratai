# ผลตรวจต้นแบบ SVG รุ่นแรก — 2026-10-15

- Next.js production build, TypeScript และ static export ผ่าน
- Chromium จริง: desktop1440px และ mobile390px ไม่มีล้นแนวนอน, browser error หรือ failed request
- กดดูดวงเล่นสับไพ่/หยิบ/พลิกสำเร็จ; ภาพไพ่ในมือกับชื่อและคำอ่านตรงกัน ตรวจครบ5ใบ
- ตรวจคำอ่าน5ใบ×6สถานะ=30ช่องตรงกับ lib/cards.json ที่สกัดจากแชทต้นทาง
- แกลเลอรี5ใบ: finite GSAP timeline6วินาที600×960; HyperFrames lint ทั้ง5ผ่าน0errors0warnings
- ตรวจ modal keyboard focus cycle / Escape และ reduced motion ผ่าน
- ตรวจภาพ desktop, mobile, modal และ5card previews ด้วยสายตาแล้ว
- คลังต้นทาง78ใบไม่ซ้ำ/6สถานะต่อใบ=468ช่อง; คำอ่านยังรอเจ้าของตรวจเชิงเนื้อหาก่อนบริการจริง

หลักฐาน artifacts/web-check.json, cards-check.json, desktop.png, mobile.png, card-detail.png; QAสุ่มแบบบังคับเฉพาะbrowserทดสอบเพื่อครอบคลุม5ใบ โค้ดจริงใช้WebCryptoสุ่มตามปกติ

ยังไม่ได้ทดสอบบนบัญชีHostingerหรืออุปกรณ์Safariจริง และยังไม่ได้deploy. งานนี้0เครดิต ไม่มีbackend/บัญชีผู้ใช้/ชำระเงิน. ไพ่ภาพครบ5ใบ ส่วนอีก73ใบยังไม่ออกแบบ.


## รอบภาพที่เจ้าของเจน + เอฟเฟคเปิดไพ่ — 2026-10-15

- Build production/TypeScriptผ่านในรุ่นส่งมอบ; หยุดidleฉากขณะมีoverlayเพื่อลดภาระการวาดภาพ
- ภาพJPEG5ใบคงbytesตรงต้นฉบับ1632×2624; manifestระบุชื่อเดิมและSHA256
- ตรวจภาพdesktop1440×1000/mobile390×844ด้วยตาแล้ว: ไพ่ครบไม่ครอป คำอ่านอยู่ใต้ไพ่ และรายละเอียด6สถานะอยู่ด้านล่าง
- ปิดแล้วพลิกกลับ,เปิดซ้ำโดยไม่สุ่ม,กดไพ่ในมือ/ไพ่ด้านล่าง,focus trap,Escape/backdrop,shortmobile/reducedmotion: ผลอัตโนมัติรอบล่าสุดอยู่ artifacts/reveal/reveal-check.json (อ้างpassedในไฟล์)
- สคริปต์ปัจจุบัน: scripts/check_reveal.py; รูปและQAเก่าในartifactsรากเป็นรุ่นก่อนหน้า
- ไม่มีการเจนภาพเพิ่มเติมหรือใช้เครดิต ไม่deploy. ภาพ1.jpeg/2.jpegเป็นฉากแบรนด์ ไม่รวมเป็นไพ่สุ่ม

ผลรอบล่าสุด: reveal-check.jsonผ่าน11กลุ่มตรวจ,0browsererrors/404s/externalrequests;ตรวจ5ไพ่30คำอ่าน. rapid-check.jsonผ่านการปิดก่อนเปิดเสร็จและเปลี่ยนreducedmotionขณะปิดโดยยังเลื่อนไปคำอ่านถูกต้อง. ดูภาพที่artifacts/reveal/.


## หน้าไพ่สามใบ — 2026-10-16

- Production build และ npm run typecheck ผ่าน; static route `/reading/` พร้อมหน้าเดิม `/`.
- Domain suite `node scripts/check_reading.cjs` ผ่าน7กลุ่ม:78รหัส/468ความหมาย/ภาพจริง5ใบ,500รอบสุ่มไม่ซ้ำหรือหาย,rejection sampling,state guard/rapid duplicate/ไม่เกิน3ใบ,คืนไพ่/แก้คำถาม/กันcallbackค้าง,ตรวจทุกความหมายรัก6สถานะตามตำแหน่ง,เปลี่ยนใบ2/3หรือสถานะแล้วsummaryเปลี่ยน.
- Chromium UI ผ่าน12กลุ่ม: ลูกศรจากหน้าเดิม,สับจริงเกิน60วินาที,หยุดโดยคงposeแล้วรวม/กาง,78ใบและกริดร่วม,เลือก/คืน/เรียง/เปิด/ปลดล็อกตรงชุดเดิม,รีเฟรชล้างคำถาม,มือถือ360/390/430พร้อมtouch/reducedmotion,keyboard/resize,เปลี่ยนreducedmotionขณะสับ,GSAPโหลดไม่ได้ยังเลือกได้.
- ไม่พบpageerror,HTTPerrorหรือexternalrequestในUI suite. ใช้browser contextทดสอบแยก;การจำลองลากทดสอบguardผ่านpointer events ไม่ใช่การวัดสัมผัสบนโทรศัพท์จริง.
- Regressionหน้าไพ่เดิมผ่าน11กลุ่มตาม artifacts/reveal-three-card-regression/reveal-check.json.
- ตรวจภาพUIด้วยตาหลังแก้ช่องไพ่ว่างและปรับขนาดโต๊ะ/ปุ่มมือถือแล้ว. หลักฐานล่าสุด artifacts/reading/ui-check.json,domain-check.txt และภาพ12ไฟล์.
- ภาพพร้อม5ใบ อีก73ใช้กรอบพร้อมชื่อ. คำอ่านรักจากแชทเดิมยังรอเจ้าของทบทวน;บทสรุปเชื่อมเวลาเป็นdemo หมวดอื่นรอข้อมูล. ไม่มีAI API,การเก็บเงินจริงหรือdeploy.
- ยังไม่ตรวจSafariบนอุปกรณ์จริงหรือHostinger;ไม่มีการวัดFPSบนโทรศัพท์จริง.

## ปรับท่าสับ/กางไพ่ให้ลื่น — 2026-10-16

- เปลี่ยนเฉพาะ motion ใน `app/reading/Table.tsx`, `reading.css`, `lib/reading-motion.ts` และเพิ่ม `public/cards/card-back.webp` (raster จาก card-back.svg เดิม 360×576) ไม่เปลี่ยน art style, state หรือข้อมูลไพ่.
- แก้บั๊กเดิม: `.ritual button:disabled` ทำให้สำรับจางลงระหว่างรวมกอง; และ `position:fixed` ของไพ่ที่บินถูกยึดกับ section ที่มี transform จาก entrance animation จึงใช้ portal.
- typecheck/production build ผ่าน; `check_reading.cjs` ผ่าน7กลุ่ม; `check_reading_ui.py` ผ่าน12กลุ่ม (รวม ticker.sleep หยุดแล้ว pose ไม่ reset); `check_reveal.py` ผ่าน11กลุ่ม.
- ตรวจด้วยตาจากวิดีโอ Playwright 1440 และ 390px (headless ไม่มี GPU, 25fps) ยังไม่ได้วัด FPS บนโทรศัพท์จริงหรือ Safari.

## สำรับ 3D (three.js) ช่วงสับ/รวม/กาง — 2026-10-16

- ตามคำขอเจ้าของให้ใกล้ Ref2 และแก้ไพ่ทะลุกัน: เพิ่ม `app/reading/DeckScene.tsx`, `app/reading/fan.ts`; แก้ `page.tsx`, `Table.tsx`, `reading.css`; dependency `three@0.186.1`, dev `@types/three@0.186.0` (exact). ส่วนเลือกไพ่/คีย์บอร์ด/กริดยังเป็น DOM เดิม.
- three แยก 2 chunk ราว 188KB gzip (368+380KB raw) โหลดเมื่อถึงขั้นคำถาม/สับเท่านั้น ไม่โหลดกับหน้าแรกหรือหน้า /reading/ ตอนเปิด (ตรวจ network ใน Chromium).
- `check_reading_ui.py` ปรับเฉพาะตัวอ่าน pose: อ่าน `data-pose` จากสำรับ WebGL หรือ transform ของสำรับ DOM; เงื่อนไขเดิมคงไว้ (pose เปลี่ยนใน 1.1 วินาที, สับเกิน 60 วินาที, ticker.sleep แล้วกดหยุด pose ไม่ reset).
- ผล: typecheck/build ผ่าน; `check_reading.cjs` 7/7; `check_reading_ui.py` 12/12; `check_reveal.py` 11/11. ตรวจเพิ่ม: WebGL ทำงานจริง (canvas 1 อันระหว่างสับ, 0 หลังกาง), เล่นซ้ำในหน้าเดิมไม่ค้าง canvas, Chromium `--disable-webgl --disable-3d-apis` ตกไปสำรับ DOM 24 ใบและเลือกไพ่ได้ ไม่มี pageerror.
- จุดส่งต่อ 3D→DOM: ตำแหน่งตรงกันราว 1px; หลัง fade ความต่างเฟรมต่อเฟรมสูงสุด ~1.9 (ก่อนแก้ 14.2 จาก opacity ของปุ่ม disabled).
- ข้อจำกัด: วิดีโอ/ตรวจทั้งหมดเป็น headless Chromium (SwiftShader, 25fps) ยังไม่วัด FPS บนโทรศัพท์จริง, Safari/iOS หรือ Hostinger. บนจอ 390×844 พัดอยู่ใต้แถบเลือกที่ sticky จึงเห็นการคลี่ไพ่เพียงแถบบน (layout เดิม).

## ท่าสับแบบ Moonlight (ไพ่น้อยลง เว้นระยะ หันข้าง) — 2026-10-16

- เจ้าของขอให้ลดจำนวนไพ่ เว้นระยะ และใช้ท่าแบบ app.moonlight.world. ห้องตัวอย่างต้องสมัครบัญชีจึงไม่ได้เข้า; วิเคราะห์จากไฟล์ JS สาธารณะที่หน้าโหลดมา (component สับไพ่ใน bundle หลัก) แล้วเขียนใหม่เอง ไม่คัดลอกโค้ด.
- แก้ `DeckScene.tsx` ทั้งท่าสับ/รวม/กาง และ stage สับสูงขึ้น (desktop 440px, มือถือ 370px) ใน `reading.css`.
- ผล: typecheck/build ผ่าน; `check_reading.cjs` 7/7; `check_reading_ui.py` 12/12; `check_reveal.py` 11/11; WebGL ทำงานจริง, canvas คืนหน่วยความจำหลังกาง, เล่นซ้ำในหน้าเดิมได้, ปิด WebGL แล้วตกไปสำรับ DOM ไม่มี pageerror.
- ตรวจด้วยตาเทียบเฟรม Ref2 (มุมหันข้างเห็นวงไพ่, มุมหน้าเป็นขั้นบันได) ที่ 1440×1000 และ 390×844; ยังไม่วัด FPS บนโทรศัพท์จริง/Safari.

## ลากไพ่ลงช่องและแตะเปิดเอง — 2026-10-17

- ตามคำขอเจ้าของ: ลากไพ่จากพัดไปวางในช่องที่เลือก และแตะไพ่ในช่องเพื่อเปิดเอง. แก้ `lib/reading.ts` (slots/opened, `PICK` แบบระบุช่อง, `OPEN`), `Table.tsx`, `page.tsx`, `reading.css`; ปรับชุดทดสอบตามพฤติกรรมใหม่ (คืนไพ่แล้วช่องว่างไว้ ไม่เลื่อน).
- แก้บั๊กเดิม 2 จุดที่เจอระหว่างทำ: `:hover` ค้างบนจอสัมผัสทำให้ไพ่ใบที่แตะล่าสุดยกค้างและบังใบข้าง ๆ (จำกัด hover ไว้ที่ `@media(hover:hover)`); ไพ่ที่บินเข้าช่อง (`.ritual-flight`) ใช้ position:fixed ใต้ section ที่มี transform จึงเพี้ยนตำแหน่ง (ย้ายไป portal ที่ body). เพิ่มการเลื่อนหน้าตอนกางไพ่ให้เห็นทั้งช่องและพัดเหนือแถบเลือกบนมือถือ (เดิมที่ 390×844 พัดโผล่ราว 68 จาก 205px).
- ผล: typecheck/build ผ่าน; `check_reading.cjs` 8/8 (เพิ่มกลุ่มเปิดเองลำดับใดก็ได้); `check_reading_ui.py` 12/12 รวมลากด้วยเมาส์ลงช่องที่ระบุ, ปล่อยนอกช่องแล้วไพ่กลับ, คืนไพ่แล้วช่องว่างคงที่, ลากด้วย touch จริงผ่าน CDP ที่ 360/390/430px และแตะเปิดครบสามช่อง; `check_reveal.py` 11/11; ตรวจ WebGL/fallback ผ่าน.
- ตรวจด้วยตาจากวิดีโอ 1440×1000 และ 390×844 (touch ผ่าน CDP); ยังไม่ทดสอบนิ้วจริงบนโทรศัพท์/Safari iOS.

## กระต่ายเคลื่อนไหวและไพ่ลอย CSS 3D — 2026-10-17

- เพิ่ม AnimatedRabbit/portrait bridge และ CardVisual; ไม่แก้ state model, RNG หรือคำอ่าน. หน้าแรกใช้เส้นทางเดิม; regression `artifacts/reveal-motion-regression/reveal-check.json` ผ่าน 11 กลุ่ม.
- `check_reading_motion.py` ผ่าน 10 กลุ่ม: หายใจ/กะพริบตาจริง, การลอย, origin/source guards, portrait ไม่รับ draw, หยุด/เล่น, visibility lifecycle, hitbox ช่องนิ่ง, ขอบหน้า–หลัง, เปิดสลับลำดับ, หยุดกลาง gather/reveal, ID ตรงคำอ่าน, มือถือ 360/390/430 และ failed scene/reduced motion. ไม่พบ pageerror.
- `check_reading_interruptions.py` ผ่าน 6 กลุ่ม: WebGL unavailable ใช้ DOM animated fallback, หยุดกลาง spread, Escape/resize/hidden/pointercancel ยกเลิกลากได้, หยุดระหว่างบินแล้วเล่นจนปลดล็อกด้วย ID เดิม.
- ภาพและคลิปใน `artifacts/reading-motion/`: screenshots เดสก์ท็อป/มือถือ และ desktop-preview.mp4, mobile-preview.mp4 จากการเล่นจริงใน Chromium. คลิปไม่มีเสียง ไม่ใช่วิดีโอที่เจนใหม่.
- ตรวจภาพหู/หมวกอยู่ในกรอบ, ข้อความและปุ่มไม่บังกัน, ไพ่เปิดแล้วหยุดลอย. ช่วง gather/spread ใช้ elapsed time โดยหักเวลาซ่อนแท็บเพื่อไม่ยืดเวลาบน renderer ช้า. พื้นหลัง portrait ไม่คำนวณ turbulence ทั้งห้องใหม่ทุกเฟรม.
- การทดสอบเป็น desktop Chromium และมือถือจำลอง ยังไม่วัด FPS หรือตรวจ Safari/iOS บนอุปกรณ์จริง. ไม่มี deploy หรือบริการ/เครดิตเพิ่ม.

สภาพแวดล้อมหน้าแรก: ตรวจรอบสุดท้ายด้วย `MMKT_BROWSER_CHANNEL=chrome ... scripts/check_reveal.py` ผ่าน 11/11 โดยไม่เปลี่ยน timeout 14 วินาทีของ suite. ตัว Chromium headless shell แบบ software rendering บนเครื่องนี้เล่นฉากเดิมช้าจนเกิน timeout ระหว่าง normal-motion draw; ตรวจพบว่า timeline ยังเดินและเปิดได้ จึงใช้ Chrome ที่ติดตั้งเป็นตัวตรวจเพิ่มเติม ไม่เปลี่ยนความเร็ว/ท่าของหน้าแรก. ชุด /reading/ ใช้ Chromium headless shell ผ่าน 12/12. คลิป preview ใช้ Chrome จาก browser profile ทดสอบแยก.

## ตรวจบน WebKit (engine ของ Safari) แบบ iPhone — 2026-10-17

- ใช้ Playwright WebKit 27.2 จำลอง iPhone 13 (`scripts/check_reading_webkit.py`, ผ่าน 4/4): หน้าแรก, สับ/หยุด/กาง, วางไพ่ 3 ใบ, แตะเปิด, ปลดล็อก demo และหน้าอ่าน ไม่มี pageerror/console error หรือ overflow แนวนอน.
- พบและแก้ 2 จุดที่เห็นได้บน iPhone: หลังไพ่ใน `CardVisual` แสดงกลับด้าน (WebKit ไม่ซ่อน backface ในการ์ดสามมิติซ้อนชั้นนี้) จึงซ่อนด้านที่ไม่ควรเห็นด้วย `visibility` สลับที่ 230ms ซึ่งเป็นจุด 90° ของการพลิก 650ms; เมนูหัวหน้าแรกตัดบรรทัดที่ 390px จึงซ่อนลิงก์ในหน้าเดียวกันบนจอไม่เกิน 480px เหลือ "เปิดไพ่ 3 ใบ →".
- WebKit แบบ headless ส่งเฟรมแอนิเมชันราว 1 เฟรมทุก 2 วินาที (Chromium headless ~5–7 fps) ทั้งที่ renderer เป็น Apple GPU จึงตรวจเส้นทาง WebGL บน WebKit ไม่ได้ (สับได้แต่ช่วงรวมกองค้างตามจำนวนเฟรม) ต้องดูบนโทรศัพท์จริง; สคริปต์จึงใช้ reduced motion.
- ตัวช่วยลากใน `check_reading_ui.py` เล็งใหม่เมื่อไพ่ข้าง ๆ ที่ถูกยกตามเมาส์บังแถบไพ่ (เดิมสุ่มล้ม): ผ่าน 12/12 ติดกัน 4 รอบ; `check_reveal.py` 11/11, `check_reading.cjs` 8/8, `check_reading_interruptions.py` 6/6; `check_reading_motion.py` ยังขึ้นกับจังหวะเวลา (ผ่าน 10/10 บางรอบ).

## ประสิทธิภาพบน iPhone/Safari — 2026-10-17

- อาการ: เจ้าของลองบนโทรศัพท์แล้วเล่นไม่ได้. วัดด้วย Playwright WebKit (iPhone 13): หน้าแรก ~0.5–1.3 fps, สับไพ่ 3D ~1 fps; หน้าเปล่า ~53–60 fps. ถอด iframe มาสคอตแล้วสับ 3D ได้ 60 fps จึงไม่ใช่โมเดล 3D แต่เป็นฉาก SVG ที่มีฟิลเตอร์ 13 ตัว (feTurbulence/blur) กับ GSAP 110 tween ที่ Safari วาดใหม่ทุกเฟรม; หยุดทุกอย่างแล้วกลับ 60 fps.
- แก้: ฉากนิ่งบน Safari/จอสัมผัส; มาสคอตเป็นภาพนิ่งบนอุปกรณ์เหล่านั้น; หน้าแรกฉากย่อด้วย zoom (บนจอ 3x Safari ทิ้งชั้นห้องที่มีฟิลเตอร์ — ห้องหายเหลือแต่กระต่าย ซึ่งมีมาก่อน); หน้าต่างเปิดไพ่หน้าแรกบน Safari ค้างที่หลังไพ่กลับด้านไม่เห็นหน้าไพ่ (มีมาก่อน) แก้ด้วยการสลับด้านตามมุม; ตัวตรวจการมองเห็น (IntersectionObserver) ใน `Motion.tsx`/`DeckScene.tsx` อ่านค่าล่าสุดแทนค่าแรก (เดิมค้างที่ "ไม่อยู่ในจอ" เมื่อสลับเร็ว ทำให้มาสคอตหรือการสับหยุด); หน้าไพ่ WebP.
- หลังแก้ WebKit iPhone: หน้าแรก 60.5 fps, สับ 3D 60.5 fps, flow เต็มแบบมีแอนิเมชันจบถึงหน้าอ่าน. `check_reading_webkit.py` 6/6 (มีเกณฑ์ ≥30 fps, ฉาก zoom, หน้าไพ่ใน reveal); `check_reading.cjs` 8/8; `check_reveal.py` 11/11; `check_reading_ui.py` 12/12; `check_reading_interruptions.py` 6/6; `check_reading_motion.py` 10/10 สองรอบติด (ปรับให้มือถือคาดหวังภาพนิ่ง และตรวจการเคลื่อนไหวแบบสุ่มหลายจุดแทนจุดเดียว).
- ข้อจำกัด: เป็นการจำลองบน Mac; Android จำลองใน headless ใช้ software GL จึงได้ ~30 fps ซึ่งไม่แทนเครื่องจริง; ยังต้องให้เจ้าของลองบนโทรศัพท์จริง.

## หน้าแรกบนมือถือ: วิดีโอสับและชูไพ่ — 2026-10-17

- เจ้าของอยากเห็นกระต่ายสับและชูไพ่บนมือถือ (โหมดนิ่งข้ามฉากไป). วัดบน WebKit iPhone แบบเล่นสดจริง (iframe `?fit=1&motion=live`): 3 fps ระหว่างรอ, 2.5 fps ระหว่างสับ; ถอดฟิลเตอร์ได้ ~60 fps — ต้นทุนอยู่ที่ฟิลเตอร์ของ art จึงอบช่วงสับ+ชูไพ่เป็นวิดีโอแทน (ภาพตรงต้นฉบับ).
- `scripts/build_scene_videos.py`: 190 เฟรม จากการเลื่อนไทม์ไลน์ GSAP ทีละ 1/30 วินาที → H.264 Main 720×1000 30fps 6.33 วินาที 699KB.
- WebKit iPhone: วิดีโอเล่นต่อเนื่อง 0→6.3 วินาที, หน้าต่างผลเปิดหลังวิดีโอจบพร้อมหน้าไพ่, ปิดแล้วกลับเป็นฉาก, ไม่มี error. ชุดทดสอบ: `check_reading_webkit.py` 6/6 (เพิ่มการตรวจว่าวิดีโอเล่นและผลรอจนจบ), `check_reveal.py` 11/11, `check_reading.cjs` 8/8, `check_reading_ui.py` 12/12, `check_reading_interruptions.py` 6/6, `check_reading_motion.py` 10/10.
- `.gitignore` ยกเว้นเฉพาะ `web/tarot/public/scene/draw-shuffle.mp4` ให้ขึ้น repo/Vercel ได้.

## หน้าแรก: กระต่ายขยับตั้งแต่เข้าหน้า และไพ่หันหน้าหลังปิดผล — 2026-10-17

- เจ้าของขอให้กระต่ายหน้าแรกขยับเหมือนเดิมตั้งแต่เข้าหน้า และหลังเปิดไพ่แล้วกด "อ่านความหมายทั้งหมดด้านล่าง" ให้ไพ่หันหน้า ไม่พลิกกลับเป็นหลัง.
- มือถือ/Safari: วิดีโอวน `idle-loop.mp4` (ไทม์ไลน์ระหว่างรอของฉาก 4 วินาที, 120 เฟรม, 720×1000) เล่นทับฉากนิ่งก่อนเปิดไพ่ และหยุด/ซ่อนเมื่อเริ่มเปิดไพ่; เดสก์ท็อป Chrome ยังเป็นฉากสด. `scripts/build_draw_video.py` เปลี่ยนชื่อเป็น `scripts/build_scene_videos.py` (`idle`/`draw`) และตรวจรอยต่อลูปจากภาพก่อนบีบอัด.
- ปิดหน้าต่างผล (ทั้งปุ่มปิดและปุ่มอ่านความหมาย) ไม่หมุนไพ่เป็นหลังแล้ว; ฉาก `mmkt:stow` ตั้งไพ่ในมือเป็นหน้า. ปรับ `check_reveal.py` ให้ตรวจว่าปิดแล้วหน้าไพ่ยังหันออก และไพ่ในมือหันหน้า (เดิมตรวจว่าต้องหันหลัง).
- ส่วนคำอ่านด้านล่าง (ที่ปุ่ม "อ่านความหมายทั้งหมดด้านล่าง" เลื่อนไปหา) เดิมแสดงหลังไพ่กับ "แตะเพื่อเปิดไพ่ใบเดิม" เปลี่ยนเป็นหน้าไพ่ (ไฟล์เดียวกับหน้าต่างผล จึงไม่โหลดซ้ำ) แตะแล้วเปิดใบใหญ่เหมือนเดิม; `check_reveal.py` และ `check_reading_webkit.py` ตรวจว่าไม่มีหลังไพ่เหลือในส่วนนี้.
- `check_reading_webkit.py` ตรวจเพิ่ม: วิดีโอวนเล่นตั้งแต่เปิดหน้า, ซ่อนระหว่างสับ, หลังกดอ่านความหมายไพ่ในมือหันหน้า และกรณีมือถือไม่ยอมเล่นวิดีโอ.
- มือถือไม่ยอมเล่นวิดีโอ (iOS Low Power Mode): วิดีโอสับซ่อนและเปิดผลทับฉากนิ่งทันที (เดิมเฟรมแรกของวิดีโอค้างทับฉากระหว่างเปิดผล).
- รอยต่อลูป: ภาพต้นทาง t=4 วินาทีตรงกับ t=0 (ต่าง 0.000), เฟรมสุดท้าย→แรก 0.015 เทียบการขยับปกติต่อเฟรม 0.14. หลังบีบอัดต่าง 0.74 เป็นเม็ด noise ของ codec ล้วน (ซูม 2 เท่ามองไม่เห็นต่าง, PSNR 41–43 dB ทั้งลูป); CRF 18–20 ลดได้นิดเดียวแต่ไฟล์ 380–500KB จึงคง CRF 24 (218KB).
- `check_rapid_reveal.py` เดิมตรวจว่าปิดแล้วไพ่ในมือหันหลัง ปรับเป็นหันหน้า. `.gitignore` ยกเว้น `web/tarot/public/scene/idle-loop.mp4` เพิ่ม.
- ผล: build ผ่าน; `check_reading.cjs` 8/8; `check_reading_webkit.py` 7/7 (หน้าแรก 61 fps, สับ 3D 60.5 fps); `check_reveal.py` 11/11 (Chrome); `check_rapid_reveal.py` ผ่าน; `check_reading_ui.py` 12/12; `check_reading_interruptions.py` 6/6; `check_reading_motion.py` 10/10. หลังเปลี่ยนรูปไพ่ในส่วนคำอ่าน รันชุดหน้าแรก (WebKit/reveal/rapid) ซ้ำบน build สุดท้ายผ่าน.
