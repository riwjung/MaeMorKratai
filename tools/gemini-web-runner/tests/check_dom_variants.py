"""Regression for the reported zero-editor/zero-file-input failure. Offline only."""
from fixture_support import *

setup=r'''({shadow,ambiguous,paste})=>{
 document.querySelector('form').remove();
 const host=document.createElement('section');host.id='real-composer';document.body.append(host);
 const root=shadow?host.attachShadow({mode:'open'}):host;
 root.innerHTML='<style>.composer{position:fixed;left:20px;bottom:20px;padding:16px;width:55%;background:#eee} [contenteditable]{min-height:90px;width:90%;border:1px solid #aaa}button{padding:12px}img{width:40px}</style><div class="composer"><button data-qa="upload"><mat-icon>add_2</mat-icon></button><div data-qa="editor" contenteditable="" class="ql-editor"></div><div data-qa="preview"></div><button data-qa="send"><mat-icon>arrow_upward</mat-icon></button></div>';
 const editor=root.querySelector('[data-qa=editor]'),preview=root.querySelector('[data-qa=preview]');
 const attach=file=>{uploads.push([{name:file.name,size:file.size}]);const image=document.createElement('img');image.src=URL.createObjectURL(file);preview.append(image);};
 if(paste)editor.addEventListener('paste',event=>{const file=event.clipboardData.files[0];if(file){event.preventDefault();attach(file);}});
 root.querySelector('[data-qa=upload]').onclick=()=>{const menu=document.createElement('button');menu.setAttribute('role','menuitem');menu.textContent='Upload files';document.body.append(menu);menu.onclick=()=>{const input=document.createElement('input');input.type='file';input.accept='image/jpeg';input.hidden=true;input.onchange=event=>{attach(event.target.files[0]);menu.remove();};document.body.append(input);};};
 root.querySelector('[data-qa=send]').onclick=()=>{sent.push({text:editor.innerText,upload:uploads.at(-1)});const query=document.createElement('user-query');query.textContent=editor.innerText;document.querySelector('#history').append(query);editor.innerText='';preview.replaceChildren();const response=document.createElement('model-response'),image=document.createElement('img');image.src=FIXTURE_IMAGE;response.append(image);document.querySelector('#history').append(response);};
 if(ambiguous){const other=document.createElement('textarea');other.placeholder='Owner notes';other.value='Preserve my notes';document.body.prepend(other);}
}'''

def variant(browser,shadow=False,ambiguous=False,paste=False,saved_state=None,legacy=True):
 context=browser.new_context(viewport={'width':1440,'height':1000});page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
 page.route('**/*',lambda route:route.fulfill(body=ref,content_type='image/jpeg') if route.request.url.endswith('/mmkt-reference.jpg') else route.fulfill(body=fixture,content_type='text/html') if route.request.url==CHAT else route.abort())
 page.add_init_script(mock);page.goto(CHAT);page.evaluate('(x)=>{window.FIXTURE_IMAGE=x;window.SCENARIO="normal"}',image)
 if saved_state:page.evaluate('(state)=>localStorage.setItem("qa-storage",JSON.stringify({["mmkt-card-runner-v1-c1051ca2e5090320"]:state}))',saved_state)
 page.evaluate(setup,{'shadow':shadow,'ambiguous':ambiguous,'paste':paste})
 page.add_script_tag(path=str(P/'extension/deck-data.js'));page.add_script_tag(path=str(P/'extension/title-workflow.js'));page.add_script_tag(path=str(P/'extension/content.js'))
 expect(status(page)).to_contain_text('พร้อม ·')
 if legacy:
  page.locator('#mmkt-card-runner').locator('#mode').select_option('legacy');expect(status(page)).to_contain_text('เปิดคิวเดิมแล้ว')
 return context,page

with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True)
 # No aria-label, empty contenteditable attribute, and input created only by + menu.
 c,p=variant(b);panel=p.locator('#mmkt-card-runner');panel.locator('details summary').last.click();panel.get_by_role('button',name='ตรวจองค์ประกอบหน้า').click();expect(panel.locator('#diagnostic')).to_contain_text('ช่องพิมพ์ 1');expect(panel.locator('#diagnostic')).to_contain_text('ช่องไฟล์ 0');panel.get_by_role('button',name='เริ่มอัตโนมัติ').click();expect(status(p)).to_contain_text('จบรอบแล้ว',timeout=8000);assert len(p.evaluate('sent'))==1 and p.evaluate('uploads')[0][0]['name']=='IMG_5392.JPG';checks.append('empty-contenteditable editor + lazy file input via plus/upload menu + icon-only send');c.close()
 # Same editor inside an open shadow root, no file input: attach by image paste.
 c,p=variant(b,shadow=True,paste=True);p.locator('#mmkt-card-runner').get_by_role('button',name='เริ่มอัตโนมัติ').click();expect(status(p)).to_contain_text('จบรอบแล้ว',timeout=7000);assert len(p.evaluate('uploads'))==1 and len(p.evaluate('sent'))==1;checks.append('open shadow-root editor + paste reference image without file input');c.close()
 # Ambiguous page: capture one user click rather than write into an unrelated draft.
 c,p=variant(b,shadow=True,ambiguous=True,paste=True,saved_state={'cards':{'the-magician':{'status':'review','firstError':'Old editor not found'}},'events':[]});panel=p.locator('#mmkt-card-runner');panel.get_by_role('button',name='เลือกช่องพิมพ์',exact=True).click();p.locator('[data-qa=editor]').click();expect(status(p)).to_contain_text('เลือกช่องพิมพ์แล้ว');p.once('dialog',lambda d:d.accept());panel.get_by_role('button',name='ยังไม่ได้ส่ง — ปลดใบค้าง').click();expect(status(p)).to_contain_text('ปลดใบค้างแล้ว');panel.get_by_role('button',name='เตรียมใบถัดไป').click();expect(status(p)).to_contain_text('พร้อมภาพแล้ว',timeout=4000);assert p.evaluate('sent')==[] and p.locator('textarea:not(#repair-notes)').input_value()=='Preserve my notes';checks.append('manual picker + explicit unsent reset + prepare-only preserve unrelated draft');c.close()
 # Recovering a stale review when all editors are absent surfaces an error instead of rejecting silently.
 c,p=variant(b,saved_state={'cards':{'the-magician':{'status':'review'}},'events':[]});p.locator('[data-qa=editor]').evaluate('e=>e.remove()');p.once('dialog',lambda d:d.accept('UNSENT'));p.locator('#mmkt-card-runner').get_by_role('button',name='ยืนยันใบค้าง').click();expect(status(p)).to_contain_text('เลือกช่องพิมพ์');assert p.evaluate('sent')==[];checks.append('UNSENT with missing editor shows actionable error; no unhandled rejection');c.close()
 c,p=variant(b,shadow=True,paste=True,legacy=False);panel=p.locator('#mmkt-card-runner')
 panel.locator('#title-file').set_input_files({'name':'approved.jpg','mimeType':'image/jpeg','buffer':ref});expect(status(p)).to_contain_text('ตรวจชื่อ ขนาด');panel.locator('#approve-title').click();panel.locator('#start').click();expect(status(p)).to_contain_text('จบรอบแล้ว',timeout=10000)
 assert [u[0]['name'] for u in p.evaluate('uploads')]==['IMG_5392.JPG','MMKT_APPROVED_TITLE_REF.jpg'] and p.evaluate('sent.length')==1
 checks.append('multiple title references uploaded through shadow-root paste without file input');c.close()
 b.close()
report={'passed':not errors,'checks':checks,'browser_errors':errors,'live_gemini_tested':False,'api_calls':0,'images_generated':0}
(OUT/'dom-variants-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False));assert report['passed']
