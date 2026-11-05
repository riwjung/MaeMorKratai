# เปิดซอร์สเพื่อ consult

ใช้cloneในโฟลเดอร์localที่ไม่ใช่iCloudสำหรับnpm/build. Node24LTS/npm และPython3.11+เป็นฐานเริ่มต้น; ใช้lockfileของแต่ละapp. คำสั่งจากrootrepo. รายละเอียดเฉพาะแอปอยู่READMEในแต่ละโฟลเดอร์.

## 1. เว็บลูกค้า — เปิดได้ทันทีโดยไม่ใช้key

```sh
cd web/tarot
npm ci
npm run dev
# http://127.0.0.1:3010/
npm run build
python3 -m http.server 3010 --bind 127.0.0.1 --directory out
```

หยุดdevก่อนserveportเดียวกัน. `out/`เป็นstaticexport; `/reading/`ต้องใช้trailing slashเมื่อserveด้วยhttp.server. คำอ่านJSONและภาพจำเป็นรวมในrepoแล้ว. ไม่มีrootworkspaceinstall; cdเข้าแอปให้ถูก.

## 2. ห้องทดลอง — ใช้Supabaseของdevเอง

```sh
cd web/workshop-standalone
npm ci
cp .env.example .env.local
```

กรอกURL/publishablekeyและserver-onlysecretใน`.env.local`ของฐานทดสอบส่วนตัว; ห้ามcommitหรือส่งkeyผ่านแชท. ใช้Supabaseprojectใหม่สำหรับdev แล้วรันSQL001,002,003ตามลำดับ. `workshop-audio`สร้างจากmigration001; privatebucket`workshop-review`ใช้กับขั้นimportreviewที่ownerจัดเตรียมในภายหลัง. สมาชิกทดสอบสร้างผ่านSupabaseAuthและแถว`workshop_members`โดยผู้ดูแลของฐานทดสอบ; ไม่มีสมาชิกเริ่มต้น/รหัสผ่านในrepo.

```sh
npm test
npm run typecheck
npm run dev
# http://127.0.0.1:3012/
```

`npm test`มีtestที่ใช้PGliteและfixtures; hostedtestsที่สร้างบัญชี/uploadaudioให้ใช้เฉพาะฐานทดสอบที่คุณควบคุม. การbuildหน้าที่ใช้serverconfigต้องมีenvครบตามแอป. อย่ารันprovision/reset/import/withdrawal scriptsกับproductionเพื่อทดลองอ่านโค้ด. หน้าไม่ตั้งenvจะแจ้งว่ายังเตรียมห้อง ไม่ใช่ฐานข้อมูลพัง.

## 3. Social Center — sourceพร้อมตรวจ, ทำงานเฉพาะเครื่อง

```sh
cd services/social-center
python3 -m venv .venv
.venv/bin/pip install -r requirements.lock.txt
export MAEMOR_DATA_DIR="$PWD/.local"
export MAEMOR_VAULT_DIR="$PWD/.local/vault"
.venv/bin/python -m maemorkratai.cli serve
# API http://127.0.0.1:8787/
```

อีกterminal (ในโฟลเดอร์เดียวกัน):

```sh
cd web
npm ci
npm run dev
# UI http://127.0.0.1:3000/
```

ทดสอบPythonด้วย`.venv/bin/pytest -q`จากservices/social-center. ไม่ต้องมีMetaTokenเพื่ออ่านโค้ดหรือรันunit tests; หน้าไม่มีข้อมูลจริงจนเชื่อมบัญชี/นำเข้าCSVเอง. macOSKeychainจำเป็นเมื่อติดต่อMeta; บนLinuxควรเริ่มจากtestsและreviewdesignก่อน ไม่ใส่plaintextfallback. ตั้งMAEMOR_DATA_DIR/MAEMOR_VAULT_DIRในAPIprocessก่อนรันเพื่อแยกข้อมูล. `scripts/open_center.py`เป็นhelperสำหรับMacเจ้าของ; build/reports/mediaบางส่วนอ้างpathsภายนอก.

## 4. คลิปและแหล่งความรู้

ดูsource referenceใน`animations/TheFools_Type/funmaxxing-expression-cut-v1`. ไม่สามารถrenderคลิปครบจากpubliccloneอย่างเดียว เพราะไม่มีassetส่วนตัว/เสียง/GLB/font/Blender scenesขนาดใหญ่. ขอassetmanifestเฉพาะส่วนที่ได้รับสิทธิ์จากเจ้าของ; เริ่มออกแบบworkerจากconfigและtoolcontractsที่มีในrepo.

rawchatและholdoutanswersไม่อยู่Git. ข้อมูลรายวันที่เผยแพร่อยู่`web/tarot/lib/daily-cards.json`; คำถามworkshopอยู่`lib/cases.json`เป็นcatalog ไม่ใช่คำตอบจริง. ไม่ต้องใช้productioncredentialsเพื่อเริ่มconsult.

## Deploy

WebหลักVercelproject`mae-mor-kratai`, RootDirectory`web/tarot`, build`npm run build`, output`out`. Workshopproject`maemorkratai-workshop`, RootDirectory`web/workshop-standalone`, fullstackNext.jsและenvเฉพาะproject. การpushครั้งนี้อัปเดตGitเพื่อreview; ไม่ได้ตั้งGitautodeployหรือแก้configurationVercelเอง. หากเชื่อมautodeployอยู่ก่อนแล้วให้ตรวจdeploymentที่triggerและenvironmentก่อนปล่อยต่อ.
