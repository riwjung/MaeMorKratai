"""Model selection and explicit repair attempts. Offline only; not visual QA."""
from fixture_support import *
REPAIR_KEY='mmkt-card-runner-repair-v1-c1051ca2e5090320'
def state(p):return p.evaluate('(k)=>JSON.parse(localStorage.getItem("qa-storage")||"{}")[k]',REPAIR_KEY)
def panel(p):return p.locator('#mmkt-card-runner')
def f(name,buf=ref):return {'name':name,'mimeType':'image/jpeg','buffer':buf}
def done(p):expect(status(p)).to_contain_text('จบรอบแล้ว',timeout=12000)
def mode_fixture(p,missing=False,unchanged=False):
 p.evaluate('''({missing,unchanged})=>{
 const picker=document.querySelector('#gemini-model-picker');picker.textContent='Fast';window.modelClicks=0;window.purchaseClicks=0;
 picker.onclick=()=>{modelClicks++;const menu=document.createElement('div');menu.setAttribute('role','menu');const option=document.createElement('button');option.setAttribute('role','menuitemradio');option.textContent=missing?'Upgrade to Pro':'Pro';option.onclick=()=>{if(missing)purchaseClicks++;else if(!unchanged){picker.textContent='Pro';menu.remove();}};menu.append(option);document.body.append(menu);};
 }''',{'missing':missing,'unchanged':unchanged})
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True)
 c,p=open_fixture(b);mode_fixture(p);panel(p).locator('#start').click();done(p);assert p.evaluate('modelClicks')==1 and p.evaluate('sent.length')==1
 assert saved(p)['cards']['the-magician']['verifiedChatModel']=='Pro';checks.append('default Pro switches Fast to Pro and verifies selected control before send');c.close()
 c,p=open_fixture(b);mode_fixture(p,missing=True);panel(p).locator('#start').click();expect(status(p)).to_contain_text('ไม่พบ Pro ที่ใช้งานได้',timeout=8000);assert p.evaluate('sent.length')==p.evaluate('uploads.length')==p.evaluate('purchaseClicks')==0;checks.append('missing Pro stops before attachments; never clicks upgrade or falls back');c.close()
 c,p=open_fixture(b);mode_fixture(p,unchanged=True);panel(p).locator('#start').click();expect(status(p)).to_contain_text('ยังยืนยันว่าเลือก Pro ไม่ได้',timeout=8000);assert p.evaluate('sent.length')==0;checks.append('click alone is not confirmation of Pro');c.close()
 c,p=open_fixture(b);p.locator('#gemini-model-picker').evaluate('e=>e.remove()');panel(p).locator('#start').click();expect(status(p)).to_contain_text('หาเมนูโมเดลไม่ชัดเจน');assert p.evaluate('sent.length')==0
 panel(p).locator('#model-policy').select_option('current');panel(p).locator('#start').click();done(p);checks.append('unknown model DOM stops safely; owner may explicitly choose current model');c.close()
 c,p=open_fixture(b)
 p.evaluate("()=>{const input=document.querySelector('input[type=file]'),old=input.onchange;input.onchange=e=>{old(e);document.querySelector('#gemini-model-picker').textContent='Fast'}}")
 panel(p).locator('#start').click();expect(status(p)).to_contain_text('โมเดลไม่ใช่ Pro');assert p.evaluate('sent.length')==0 and saved(p)['cards']['the-magician']['status']=='prepared';checks.append('rechecks Pro immediately before send after uploads');c.close()
 c,p=open_fixture(b,legacy=False);panel(p).locator('#mode').select_option('repair');expect(status(p)).to_contain_text('เปิดคิวซ่อมภาพแล้ว');expect(panel(p).locator('#candidate')).not_to_be_visible();expect(panel(p).locator('#first')).not_to_be_visible()
 panel(p).locator('#source-card').select_option('the-emperor');panel(p).locator('#queue-repair').click();expect(status(p)).to_contain_text('เลือกไฟล์ภาพเดิม');assert p.evaluate('sent.length')==0
 panel(p).locator('#source-file').set_input_files(f('the-emperor.jpg'));expect(status(p)).to_contain_text('เลือกจุดแก้');assert panel(p).locator('#repair-issue').input_value()=='frame'
 panel(p).locator('#queue-repair').click();expect(status(p)).to_contain_text('เข้าคิวซ่อมแล้ว');assert state(p)['cards']['the-emperor']['attempt']==1
 panel(p).locator('#start').click();done(p)
 text=p.evaluate('sent[0].text');assert 'LOCAL CORRECTIONS ONLY' in text and 'complete bottom edge' in text and 'missing matching counterpart' not in text and '2.4%' not in text
 assert 'CARD TITLE: THE EMPEROR' in text and 'current letterforms' in text
 assert [u[0]['name'] for u in p.evaluate('uploads')]==['IMG_5392.JPG','TARGET_ORIGINAL_the-emperor.jpg']
 assert p.evaluate('downloads[0].variant')=='repair-v1';assert state(p)['cards']['the-emperor']['qualityStatus']=='owner-review-required';checks.append('Emperor frame-only repair preserves art/title, requires original, and uses separate output')
 first=state(p)['cards']['the-emperor'];panel(p).locator('#queue-repair').click();expect(status(p)).to_contain_text('เข้าคิวซ่อมแล้ว');assert state(p)['history'][0]['jobToken']==first['jobToken'] and state(p)['cards']['the-emperor']['attempt']==2
 panel(p).locator('#start').click();done(p);assert p.evaluate('sent.length')==2 and state(p)['cards']['the-emperor']['jobToken']!=first['jobToken'];checks.append('explicit repair of completed card archives previous attempt and preserves old files')
 panel(p).locator('#source-card').select_option('the-chariot');panel(p).locator('#source-file').set_input_files(f('the-chariot.jpg'));expect(status(p)).to_contain_text('เลือกจุดแก้');assert panel(p).locator('#repair-issue').input_value()=='brows'
 panel(p).locator('#queue-repair').click();expect(status(p)).to_contain_text('เข้าคิวซ่อมแล้ว');panel(p).locator('#start').click();done(p)
 text=p.evaluate('sent[2].text');assert 'missing matching counterpart' in text and 'complete bottom edge' not in text and 'Do not change the eyes' in text;checks.append('Chariot repairs paired eyebrows only; no unnecessary redraw or frame edits')
 panel(p).locator('#source-card').select_option('the-fool');panel(p).locator('#source-file').set_input_files(f('the-fool.jpg'));expect(status(p)).to_contain_text('เลือกจุดแก้');panel(p).locator('#repair-issue').select_option('custom');panel(p).locator('#queue-repair').click();expect(status(p)).to_contain_text('ระบุจุด');panel(p).locator('#repair-notes').fill('Repair a missing paw only');panel(p).locator('#queue-repair').click();expect(status(p)).to_contain_text('เข้าคิวซ่อมแล้ว')
 panel(p).locator('#source-file').set_input_files(f('the-fool.jpg',ref+b'\0'));expect(status(p)).to_contain_text('เลือกจุดแก้');panel(p).locator('#start').click();expect(status(p)).to_contain_text('ภาพเดิมเปลี่ยนหลังเข้าคิว');assert p.evaluate('sent.length')==3;checks.append('custom repair needs notes; changed source requires requeue before send')
 p.screenshot(path=str(OUT/'pro-repair-panel.png'));c.close()
 # Queue states and old downloaded jobs are not reset to pending when entering repair mode.
 old={'cards':{'the-emperor':{'status':'downloaded','filename':'old.jpg'}},'events':[]}
 c,p=open_fixture(b,saved=old);panel(p).locator('#mode').select_option('repair');expect(status(p)).to_contain_text('เปิดคิวซ่อมภาพแล้ว');assert p.evaluate('MMKT_RUNNER.queue().length')==0 and saved(p)['cards']==old['cards'];checks.append('repair queue is independent; original completion records remain unchanged');c.close();b.close()
report={'passed':not errors,'checks':checks,'browser_errors':errors,'live_gemini_tested':False,'real_images_generated':0}
(OUT/'pro-repair-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False));assert report['passed']
