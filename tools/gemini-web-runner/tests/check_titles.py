"""Offline title workflow checks; no generation and no owner's browser profile."""
from fixture_support import *
TITLE_KEY='mmkt-card-runner-title-v1-c1051ca2e5090320'
def title_state(p):return p.evaluate('(k)=>JSON.parse(localStorage.getItem("qa-storage"))[k]',TITLE_KEY)
def file(name):return {'name':name,'mimeType':'image/jpeg','buffer':ref}
def panel(p):return p.locator('#mmkt-card-runner')
def approve(p):
 panel(p).locator('#title-file').set_input_files(file('approved-first-title.jpg'))
 expect(status(p)).to_contain_text('ตรวจชื่อ ขนาด')
 panel(p).locator('#approve-title').click();expect(panel(p).locator('#title-state')).to_contain_text('อนุมัติ ref:')
def start(p):panel(p).locator('#start').click()
def done(p):expect(status(p)).to_contain_text('จบรอบแล้ว',timeout=15000)
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True)
 c,p=open_fixture(b,legacy=False);start(p);expect(status(p)).to_contain_text('อนุมัติ ref');assert p.evaluate('sent.length')==0 and title_state(p)['cards']=={}
 panel(p).locator('#candidate').check();panel(p).locator('#count').fill('3');start(p);done(p)
 assert p.evaluate('sent.length')==1 and p.evaluate('uploads.length')==1
 sent=p.evaluate('sent[0].text');assert 'CARD TITLE: THE MAGICIAN' in sent and '2.4%' in sent and 'No words, letters' not in sent
 assert p.evaluate('downloads[0].variant')=='title-v1';checks.append('missing reference stops before preparing; candidate caps batch at one; title-specific output')
 approve(p);panel(p).locator('#count').fill('2');panel(p).locator('#gap').fill('5');start(p);done(p)
 uploads=p.evaluate('uploads');assert [u[0]['name'] for u in uploads]==['IMG_5392.JPG','IMG_5392.JPG','MMKT_APPROVED_TITLE_REF.jpg','IMG_5392.JPG','MMKT_APPROVED_TITLE_REF.jpg']
 assert 'CARD TITLE: THE HIGH PRIESTESS' in p.evaluate('sent[1].text') and 'CARD TITLE: THE EMPRESS' in p.evaluate('sent[2].text')
 entries=title_state(p)['cards'];assert entries['the-high-priestess']['titleReferenceSha256']==entries['the-empress']['titleReferenceSha256'];assert 'data:image' not in json.dumps(title_state(p));checks.append('approved first result accompanies original art reference on every subsequent card; SHA256 provenance')
 p.screenshot(path=str(OUT/'title-workflow-new.png'));c.close()
 c,p=open_fixture(b,legacy=False);panel(p).locator('#mode').select_option('edit');expect(status(p)).to_contain_text('เปิดคิวชื่อไพ่แล้ว');start(p);expect(status(p)).to_contain_text('นำเข้าภาพเดิมก่อน')
 approve(p);panel(p).locator('#source-card').select_option('the-fool');panel(p).locator('#source-file').set_input_files(file('Gemini-original-unknown-name.jpg'));expect(status(p)).to_contain_text('จับคู่ภาพเดิมกับ The Fool');start(p);done(p)
 assert [u[0]['name'] for u in p.evaluate('uploads')]==['IMG_5392.JPG','MMKT_APPROVED_TITLE_REF.jpg','TARGET_ORIGINAL_the-fool.jpg']
 prompt=p.evaluate('sent[0].text');assert 'ADD TITLE ONLY' in prompt and 'Do not redraw' in prompt and 'begins a gentle adventure' not in prompt and 'CARD TITLE: THE FOOL' in prompt
 assert title_state(p)['cards']['the-fool']['sourceSha256'];checks.append('edit original existing Fool with three references; preserve-art prompt; original five are not skipped')
 panel(p).locator('#source-batch').set_input_files([file('THE_MAGICIAN.jpeg'),file('02-the-high-priestess.jpg')]);expect(status(p)).to_contain_text('นำเข้าภาพเดิมแล้ว');assert p.evaluate('MMKT_RUNNER.queue().map(c=>c.id)')==['the-magician','the-high-priestess']
 panel(p).locator('#source-batch').set_input_files([file('the-empress.jpg'),file('unknown-card.jpg')]);expect(status(p)).to_contain_text('ไม่รู้ว่าไฟล์');assert p.evaluate('MMKT_RUNNER.queue().map(c=>c.id)')==['the-magician','the-high-priestess']
 panel(p).locator('#source-batch').set_input_files([file('THE_MAGICIAN.jpeg')]);expect(status(p)).to_contain_text('ภาพซ้ำ');checks.append('batch filename matching is atomic; unknown/duplicate names never silently misassign art')
 p.screenshot(path=str(OUT/'title-workflow-edit.png'));c.close()
 # Legacy progress stays untouched while title-v1 has its own progress.
 old={'cards':{'the-magician':{'status':'downloaded','manuallyVerified':True}},'events':[]}
 c,p=open_fixture(b,saved=old,legacy=False);assert p.evaluate('MMKT_RUNNER.queue()[0].id')=='the-magician';approve(p);start(p);done(p)
 assert saved(p)==old;panel(p).locator('#mode').select_option('legacy');expect(status(p)).to_contain_text('เปิดคิวเดิมแล้ว');assert p.evaluate('MMKT_RUNNER.queue()[0].id')=='the-high-priestess';checks.append('legacy progress preserved; titled versions have independent queue')
 # Simulate content-script reload; imported refs must be explicitly reselected.
 p.evaluate('document.getElementById("mmkt-card-runner").remove();delete globalThis.MMKT_RUNNER')
 p.add_script_tag(path=str(P/'extension/content.js'));expect(status(p)).to_contain_text('พร้อม ·');start(p);expect(status(p)).to_contain_text('อนุมัติ ref');assert p.evaluate('sent.length')==1;checks.append('reload retains progress but never pretends local reference files remain approved');c.close()
 # A stale title job must never auto-bind the legacy same-card result.
 c,p=open_fixture(b,legacy=False)
 pending={'cards':{'the-magician':{'status':'generated','baseline':0,'jobToken':'MMKT-TITLE-JOB-test'}},'events':[]}
 p.evaluate('x=>{const s=JSON.parse(localStorage.getItem("qa-storage")||"{}");s[x.key]=x.value;localStorage.setItem("qa-storage",JSON.stringify(s));document.getElementById("mmkt-card-runner").remove();delete globalThis.MMKT_RUNNER;}',{'key':TITLE_KEY,'value':pending})
 p.add_script_tag(path=str(P/'extension/content.js'));expect(status(p)).to_contain_text('พร้อม ·')
 p.evaluate('()=>{const q=document.createElement("user-query");q.textContent="CARD SCENE: THE MAGICIAN";document.getElementById("history").prepend(q)}')
 start(p);expect(status(p)).to_contain_text('ไม่พบภาพที่ตรงกับ');assert p.evaluate('sent.length')==p.evaluate('downloads.length')==0;checks.append('same-card legacy image cannot satisfy a titled recovery job')
 c.close()
 # Provider accepts first image but replaces its preview on second; must not send incomplete references.
 c,p=open_fixture(b,legacy=False);approve(p)
 p.evaluate("()=>{document.querySelector('input[type=file]').onchange=e=>{uploads.push([...e.target.files].map(f=>({name:f.name,size:f.size})));const i=document.createElement('img');i.src=URL.createObjectURL(e.target.files[0]);document.querySelector('#preview').replaceChildren(i);};}")
 start(p);expect(status(p)).to_contain_text('ไม่เห็นภาพแนบ MMKT_APPROVED_TITLE_REF',timeout=35000)
 assert p.evaluate('sent.length')==0 and title_state(p)['cards']['the-magician']['status']=='preparing'
 checks.append('incomplete multi-reference upload stops before sending instead of silently omitting art reference')
 c.close();b.close()
report={'passed':not errors,'checks':checks,'browser_errors':errors,'live_gemini_tested':False,'images_generated':0}
(OUT/'title-workflow-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False));assert report['passed']
