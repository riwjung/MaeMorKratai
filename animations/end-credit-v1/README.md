# MaeMorKratai — ฉากจบ 2D

ไฟล์สำเร็จ: renders/MaeMorKratai_end_credit_v1.mp4 — 10วินาที,1080×1920,30fps,H.264/yuv420p ไม่มีเสียงสำหรับนำไปต่อท้ายคลิป
ต้นฉบับ: IMG_5392.JPG คัดลอกแบบไม่แก้ไฟล์มาเป็น assets/character.jpg; หน้า/หู/อุ้งมือใช้ภาพเดิมผ่าน SVG clipping และ mask; ฉาก ห้อง โต๊ะ ไพ่ และส่วนเชื่อมลำตัวเป็น SVG สีเรียบตามภาพเดิม
ไม่มีการแปลงเป็น3D ไม่มี AI generation/upload และใช้เครดิตHiggsfield0

## แก้ไขและดูตัวอย่าง

- index.html เป็น compositionจริง HyperFrames+GSAP
- build_scene.py สร้าง index.html; ถ้าจะแก้ถาวรให้แก้scriptแล้วรันใหม่
- DESIGN.md / STORYBOARD.md เก็บสี สไตล์ และเวลา
- preview.html มีทั้งMP4และiframe timeline; preview_server.py ให้HTTP Rangeสำหรับscrubbing
- เปิดpreview: `~/AIVideoLocal/maemorkratai/.venv/bin/python preview_server.py` แล้วเปิด http://127.0.0.1:3003
- Studio: http://localhost:3002/#project/endcard (เมื่อpreviewทำงาน)

## เรนเดอร์ใหม่

ใช้ HyperFrames ที่ติดตั้งแล้ว:

```sh
~/AIVideoLocal/hf/node_modules/.bin/hyperframes lint .
~/AIVideoLocal/hf/node_modules/.bin/hyperframes render . --output renders/MaeMorKratai_end_credit_v2.mp4 --fps 30 --quality high --workers 2 --strict --no-best-effort --no-browser-gpu
```

ห้ามส่ง snapshot describe ไปAIโดยไม่อนุมัติ ใช้ `--describe false` ถ้าเรียกคำสั่งsnapshot; การเล่นและเรนเดอร์compositionนี้ใช้assetsในเครื่องทั้งหมด
fontใช้Arial Rounded BoldจากระบบMacของเจ้าของสำหรับการเรนเดอร์บนเครื่อง โฟลเดอร์นี้เป็นเทมเพลตส่วนตัว ไม่ใช่แพ็กเกจสำหรับเผยแพร่font
