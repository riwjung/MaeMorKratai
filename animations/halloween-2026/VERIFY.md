# Verification — Halloween v3, 2026-10-15

เพิ่ม blink ที่0.8/3.9/7.5/10.7s ด้วยชั้นเปลือกตาใช้textureจากภาพเดิม. ช่วงปิดประมาณ0.14sก่อนเปิด0.065s. เก็บท่าสับสามรอบ1.1–4.34s, รวบ4.42–5.05s, ยก5.1–6.6s, พลิก6.35–7.05sและถือโชว์ถึง12sจากv2.

HyperFrames lint/runtime/layout/contrast0errors0warnings; check-v3.json. MP4:12s,1080×1920,30fps,360frames,H264,yuv420p,silent. Full decode/blackdetectผ่านไม่มีช่วงดำ. Chromiumเล่นจนended12s, Range206, iframe scrub10.8sและmobile390ผ่านไม่มีbrowser/media errors. ตรวจencoded blink/contact sheet/heroด้วยสายตาแล้ว.

หลักฐานcheck-v3.json,probe.json,playback-check.json,renders/encoded-blink-v3.png. เก็บcheck-v2.jsonกับbuild_scene_v2.pyไว้เทียบ; MP4v1/v2คงอยู่. ภาพcharacter.jpgเดิมไม่เปลี่ยน.0Higgsfieldเครดิต ไม่อัปโหลด.
