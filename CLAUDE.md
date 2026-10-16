# กติกาคลังความรู้ แม่หมอกระต่าย

- ภาษาไทย; slug อังกฤษ kebab-case; wikilink ภายใน [[slug]]
- raw/ เพิ่มได้อย่างเดียว ห้ามแก้ ย้าย หรือลบ; ไม่แตะ .obsidian/
- wiki ทุกหน้ามี YAML: type,title,aliases,tags,created,updated และ status/sources สำหรับหน้าสังเคราะห์
- type: source เพิ่ม source_type,author,published,url,raw_path,ingested
- ทุกข้อเท็จจริงอ้าง source; ข้อสังเกต/สมมติฐานติดป้ายชัดเจน
- ทุก mutation วิกิอัปเดต index.md และเพิ่มท้าย log.md; lint ด้วย tools/wiki-lint.py
- แยก brand/content/analytics/astrology; ความรู้ดูดวงมาจากเจ้าของ ไม่แต่งวิธีหรือคำทำนายเป็นข้อเท็จจริง
- ข้อมูลส่วนบุคคลอยู่ในเครื่อง ไม่ส่งออกไปบริการภายนอก; วิกิมีเฉพาะธีมคอมเมนต์รวม
- token ใช้ Keychain เท่านั้น; ไม่บันทึกใน raw, code, logs หรือรายงาน
- งานหนักอยู่ ~/AIVideoLocal/maemorkratai/; การใช้เครดิต Higgsfield ต้องตรวจราคาและขออนุมัติ

## เริ่มงานต่อ

อ่าน [CLAUDE_HANDOFF.md](CLAUDE_HANDOFF.md) สำหรับสรุปส่งต่องานล่าสุด แล้วอ่าน HANDOFF.md และตรวจ git status ก่อนแก้ไฟล์.
