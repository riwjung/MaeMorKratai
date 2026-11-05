# The Fool ในออฟฟิศ — Expression Cut v1

วันที่ 4 พฤศจิกายน 2026 · เวอร์ชันต่อจากสีหน้าฟูลที่เจ้าของอนุมัติ

เปิด [review.html](review.html) เพื่อดูคลิปและเลือก 12 ช็อต; วิดีโอ `fool-office-expression-v1.mp4` 61 วินาที 1080×1920 / 30 fps. ภาพ Blender เรนเดอร์ขนาดเดียวกับไฟล์ส่ง.

## งานชุดนี้

- ฟูลและพี่แว่นใช้ GLB Tripo ของเจ้าของจาก `../funmaxxing-claude-v1/assets/3d/`; rig 25 กระดูกต่อตัว พร้อม texture. พร็อพโต๊ะ หอคอย ถ้วยกาแฟ กองงาน และของเล่นกระดาษใช้ GLB ที่มีอยู่.
- ฟูลเพิ่ม Shape Keys curious/worried/happy/blink และคิ้วตาม proof `../funmaxxing-claude-v1/expression-proof-v1/` ที่เจ้าของเลือก. ขยับหัว หู และท่าทางให้เข้าบท; ลดน้ำหนักยิ้มในช็อตยาวเพื่อให้เห็นตา. พี่แว่นยังใช้ใบหน้าต้นทาง.
- เสียง **sai-voicestudio-seedref-v8-final.wav** คงไฟล์เดิมทุก byte (SHA ใน production.json), 53.897708 วินาที 48 kHz mono. ไม่สร้างเสียงหรือใช้เครดิตเพิ่ม.
- จัด 12 ช็อตจาก sources.json ของเสียง final ที่เลือกจริง รวมท่อน 6–7 และไฟล์แก้ v8b; ไม่ใช้ timeline หรือคิวปาก v2/v8 เก่า. พาธของไฟล์เสียงย่อยใน sources.json อ้างอิงจากโฟลเดอร์โปรเจกต์ต้นทางใน production.json; ไฟล์ WAV final ที่ใช้ตัดต่ออยู่ในชุดนี้ครบ.
- แม่หมอผู้เล่ากลางล่างเป็นภาพ 2D ชุด A–F เดิม ขยับตาม Rhubarb ใหม่ 370 คิว และขยับตัวเบา ๆ แบบ EP01. ตัวละครฟูล 3D แสดงอารมณ์ ส่วนผู้เล่าเป็นคนพูด.
- ซับ HyperFrames + GSAP สีขาวขอบเข้ม/เน้นคำเหลือง/เด้งเข้า 24 ช่วง ใช้แบบ EP01 พร้อมพื้นโปร่งใส. เปลี่ยน intermediate จาก ProRes 4444 เป็น VP9 WebM alpha เพราะ ProRes ใช้พื้นที่จนดิสก์เต็ม. เอฟเฟกต์และเลย์เอาต์คงเดิม.
- ดนตรี/SFX สังเคราะห์ในเครื่อง จัดคิวใหม่และหลบใต้เสียงพูด มิกซ์เป้า −16.5 LUFS โดยลดระดับรวมคงที่ ไม่เร่ง/เปลี่ยนโทนเสียงพูด.
- End credit ต้นฉบับของเจ้าของครบ 300 เฟรม เริ่มที่ 50.9667 วินาที; ประโยคชวนติดตามเดิมเริ่ม 50.98 วินาที. แสดง Like · Share · Follow เหนือชื่อ MaeMorKratai หลังจบคำพูด. ไทม์ไลน์ปัดเข้ากริดเฟรมและเติมเฟรมท้ายหนึ่งเฟรม รวม 61 วินาที.

## ซอร์สและการรันซ้ำ

- `blender/build_scenes.py`: ฉาก แสง กล้อง ท่าร่างกายและสีหน้า; `blender/scenes/shot-01.blend` ถึง `shot-12.blend` เปิดแก้ได้รายช็อต
- `assets/fool-expressions-approved.blend`: สำเนาโมเดลฟูลจาก proof; GLB ต้นฉบับใน assets/3d ไม่ถูกแก้
- `timing/shots.json`, `timing/pieces.json`: เวลาใหม่ตามไฟล์เสียง final; `timing/captions.json` และ `transcript.srt`: ซับ; `timing/mouth-cues.json`: ปากแม่หมอ
- `tools/render.py`: เรนเดอร์ช็อตที่ยังไม่มี MP4; ลบ MP4 ของช็อตที่จะแก้ก่อนรันใหม่ เก็บ .blend และ MP4 แล้วล้างเฉพาะ JPEG ที่สร้างใหม่หลัง encode
- `tools/make_overlay.py`: สร้าง overlay/index.html; runtime HyperFrames อยู่ `~/AIVideoLocal/hf/node_modules/.bin/hyperframes`
- คำสั่ง overlay: `hyperframes render overlay --format webm --fps 30 --workers 1 --vp9-cpu-used 6 --crf 28 --output overlay/overlay.webm`; ffmpeg ต้องใช้ `-c:v libvpx-vp9` ก่อน input WebM เพื่ออ่าน alpha
- `tools/make_score.py` รันด้วย Python ของ Blender ที่มี numpy; ตามด้วย `python3 tools/mix.py`
- `python3 tools/compose.py`: ประกอบเต็ม; `--proof` สร้าง 12 วินาทีแรกเมื่อสามช็อตแรกและ overlay พร้อม
- `python3 tools/make_review.py`, `python3 tools/verify.py`: หน้ารีวิวและตรวจขนาด/เฟรม/decode/SHA เสียง/บท/ลิงก์

## ขอบเขตการรีวิว

เป็นไฟล์ตรวจในเครื่อง ยังไม่ได้เผยแพร่. ซับระดับประโยคอิงเวลาท่อนเสียงจริง ส่วนขอบเขตภายในประโยคประมาณตามความยาวคำ. Rhubarb phonetic ประมาณจังหวะภาษาไทย; โปรดฟังและดูปากก่อนล็อกงาน. ขอบตา/ปากฟูลใช้ topology เดิม จึงยังเห็นรายละเอียดบางจุดเมื่อซูมใกล้. การเก็บ topology และทำชุดปากออกเสียงให้ตัวละคร 3D เป็นงานต่อจากสีหน้า proof นี้.

## ไฟล์ส่งรีวิวและผลตรวจ

- [MP4 ใน FinalResult](/Users/sawettachatsuthum/Desktop/AI_Video/FinalResult/MaeMorKratai_TheFool_Office_Expression_v1.mp4)
- `qa/validation.json`: 61.0 วิ, 1830 เฟรม, 1080×1920/30fps, decode ทั้งไฟล์ผ่าน, บทซับครบ, เสียงต้นฉบับ SHA ตรง, ลิงก์หน้ารีวิวครบ
- ลดมุมยกแขนช็อตถามเป็น 42 องศาให้มืออยู่ในเฟรมและลดรอยยืดใต้แขน; ยังใช้ skin weights ของโมเดลต้นทาง
- สำรองซอร์สล่าสุดใน vault: `animations/TheFools_Type/funmaxxing-expression-cut-v1/source-export-20261104-final.zip`; ภายในมีโค้ด เวลา README production และผลตรวจ. ไฟล์ .blend/GLB และสื่ออยู่ runtime นี้
