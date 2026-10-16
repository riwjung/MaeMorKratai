"""Offline DOM fixture tests. No Google session and no live generation requests."""
from pathlib import Path
import json,base64
from playwright.sync_api import sync_playwright,expect
P=Path(__file__).resolve().parents[1];OUT=P/'tests/artifacts';OUT.mkdir(exist_ok=True)
CHAT='https://gemini.google.com/u/0/app/c1051ca2e5090320'
ref=(P/'extension/assets/IMG_5392.JPG').read_bytes()
image='data:image/jpeg;base64,'+base64.b64encode(ref).decode()
fixture='''<!doctype html><html><head><title>MMKT offline QA fixture</title><style>body{font:16px system-ui;background:#f5ecf7;padding:30px}form{position:fixed;bottom:20px;left:20px;width:50%;padding:16px;border:1px solid #ccc}textarea{width:95%;height:100px}model-response,user-query{display:block;margin:15px}model-response img{width:100px}#preview img{width:48px;height:48px}</style></head><body><h1>Offline UI fixture — no Gemini requests</h1><div id="history"><model-response><p>Historical reply</p><img id="old-image"></model-response></div><form onsubmit="return false"><textarea aria-label="Enter a prompt"></textarea><input type="file" accept="image/*" style="display:none"><div id="preview"></div><button class="send-button" type="button" aria-label="Send message">Send</button></form><script>
window.sent=[];window.uploads=[];window.downloads=[];window.downloadChecks=0;
document.querySelector('input').onchange=e=>{window.uploads.push([...e.target.files].map(f=>({name:f.name,size:f.size})));const i=document.createElement('img');i.src=URL.createObjectURL(e.target.files[0]);document.querySelector('#preview').replaceChildren(i);};
document.querySelector('.send-button').onclick=()=>{const box=document.querySelector('textarea');sent.push({text:box.value,upload:uploads.at(-1)});const u=document.createElement('user-query');u.textContent=box.value;historyElement().append(u);box.value='';document.querySelector('#preview').replaceChildren();document.querySelector('input').value='';const r=document.createElement('model-response');r.textContent='Working';historyElement().append(r);const stop=document.createElement('button');stop.setAttribute('aria-label','Stop response');document.body.append(stop);setTimeout(()=>{stop.remove();if(window.SCENARIO==='quota'){r.textContent='You have reached your daily limit. Try again tomorrow.';return;}if(window.SCENARIO==='text-only'){r.textContent='No image returned.';return;}const i=document.createElement('img');i.src=window.FIXTURE_IMAGE;r.replaceChildren(i);},250);};
function historyElement(){return document.querySelector('#history')}
</script></body></html>'''
mock='''(() => {
 const read=()=>JSON.parse(localStorage.getItem('qa-storage')||'{}');
 globalThis.chrome={storage:{local:{get:async key=>({[key]:read()[key]}),set:async value=>localStorage.setItem('qa-storage',JSON.stringify({...read(),...value}))}},runtime:{getURL:()=>location.origin+'/mmkt-reference.jpg',sendMessage:async msg=>{if(msg.type==='mmkt:download'||msg.type==='mmkt:download-data'){window.downloads.push(msg);return {ok:true,downloadId:window.downloads.length};}if(msg.type==='mmkt:show-download')return {ok:true,found:window.downloads.length>0,filename:'/qa/Downloads/MaeMorKratai/cards/the-empress.jpg'};if(msg.type==='mmkt:download-status'){window.downloadChecks++;return window.SCENARIO==='download-failed'?{state:'interrupted',error:'NETWORK_FAILED'}:{state:'complete',mime:'image/png',filename:'Downloads/MaeMorKratai/cards/card.png'};}return {ok:true};}}};
})();'''
checks=[];errors=[]
def open_fixture(browser,scenario='normal',saved=None):
 context=browser.new_context(viewport={'width':1440,'height':1000})
 page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
 page.route('**/*',lambda route:route.fulfill(body=ref,content_type='image/jpeg') if route.request.url.endswith('/mmkt-reference.jpg') else route.fulfill(body=fixture,content_type='text/html') if route.request.url==CHAT else route.abort())
 page.add_init_script(mock)
 page.goto(CHAT)
 page.evaluate('(x)=>{window.FIXTURE_IMAGE=x.image;window.SCENARIO=x.scenario;document.getElementById("old-image").src=x.image}',{'image':image,'scenario':scenario})
 if saved:page.evaluate('(state)=>localStorage.setItem("qa-storage",JSON.stringify({["mmkt-card-runner-v1-c1051ca2e5090320"]:state}))',saved)
 page.add_script_tag(path=str(P/'extension/deck-data.js'));page.add_script_tag(path=str(P/'extension/content.js'))
 page.locator('#mmkt-card-runner').get_by_text('พร้อม · เริ่มที่ 1 ใบเพื่อทดสอบ',exact=True).wait_for()
 return context,page

def status(page):return page.locator('#mmkt-card-runner').locator('#status')
def saved(page):return page.evaluate('JSON.parse(localStorage.getItem("qa-storage"))["mmkt-card-runner-v1-c1051ca2e5090320"]')
