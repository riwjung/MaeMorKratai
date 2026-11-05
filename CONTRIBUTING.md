# ทำงานร่วมกับเพื่อน dev

อ่าน [docs/consult/START_HERE.md](docs/consult/START_HERE.md) และอ่านAGENTS.md/CLAUDE.mdของโฟลเดอร์ที่แก้. ใช้branchของแต่ละงานและPRที่อธิบายพฤติกรรมที่เปลี่ยน/หลักฐานตรวจ/ความเสี่ยง. หลีกเลี่ยงรวมการย้ายhosting,แก้schemaและแก้คำอ่านในPRเดียว.

- แยกสิ่งที่ใช้งานจริง/ข้อเสนอ/ข้อมูลที่ยังไม่ตรวจ. ไม่แก้คำทำนายหรือรับรองเนื้อหาแทนแม่หมอ
- ไม่commit.env,APIkeys,cookies,DBbackup,คำตอบ/เสียงผู้ทดลอง,privateintake/holdoutหรือprovideraccountdata. `.env.example`ต้องมีแต่placeholder
- ใช้database/projectทดสอบและsyntheticfixtures. อ่านสิทธิ์ก่อนรันscriptsที่provision/reset/import/delete; ไม่ทดสอบmutationกับproduction
- เว็บลูกค้า: `npm ci && npm run build` ใน`web/tarot`. ถ้าแก้flowไพ่/ข้อมูลให้ใช้domain/UIchecksที่เกี่ยวข้องและตรวจcardID/sourceparity
- Workshop: `npm ci`, `npm test`, `npm run typecheck`; buildโดยตั้งenvฐานทดสอบ. แก้สิทธิ์/SQLต้องทดสอบRLSและconcurrencyที่เกี่ยวข้อง
- SocialCenter: `.venv/bin/pytest -q`; sourceนี้จำกัดlocalและmacOSKeychain. การย้ายขึ้นserverต้องออกแบบAuth/secretstorageใหม่
- ซอร์สคลิปreferenceต้องมีassetmanifestก่อนrender. ค่าproviderต้องขออนุมัติราคา; ห้ามให้retryสร้างpaidjobซ้ำเมื่อไม่ทราบสถานะเดิม
- การแก้วิกิให้updateindex/logและรัน`tools/wiki-lint.py`บนvaultเจ้าของ. Publiccloneไม่มีrawส่วนตัวที่บางหน้าอ้าง จึงอาจรันstrictlintชุดเดิมไม่ได้; เอกสารconsultใช้relativepathsที่มีในrepo

Repoเป็นpublic. ให้เจ้าของเพิ่มสิทธิ์GitHubหรือบัญชีบริการตามหน้าที่เมื่อจำเป็น; การได้ลิงก์repoไม่ได้ให้สิทธิ์productiondatabaseหรือการเผยแพร่ช่อง.

ก่อนcommitให้stageเฉพาะไฟล์ของงาน แล้วรัน `python3 tools/check_public_release.py` เพื่อตรวจblockedfilesและรูปแบบcredentialเบื้องต้น; ตัวตรวจไม่echoค่าที่ตรงและไม่แทนการreviewข้อมูล/ประวัติGit.
