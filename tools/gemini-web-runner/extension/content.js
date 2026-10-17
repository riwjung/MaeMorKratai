(() => {
 'use strict';
 if(globalThis.MMKT_RUNNER)return;
 const CHAT='c1051ca2e5090320';
 let KEY='mmkt-card-runner-title-v1-'+CHAT,mode='new',approvedTitle=null,titleCandidate=null;
 const sourceArt=new Map(),TITLES=globalThis.MMKT_TITLES;
 const DECK=globalThis.MMKT_DECK;
 const SELECTORS={editor:'textarea:not([disabled]):not([readonly]),[contenteditable]:not([contenteditable="false"]),.ql-editor[contenteditable],[role="textbox"][contenteditable]',responses:'model-response',queries:'user-query'};
 const quota=/you(?:’|')?ve reached|reached (?:your|the).*(?:limit|quota)|quota.{0,35}(?:exceeded|limit)|too many requests|try again (?:later|tomorrow)|daily limit|ถึงขีดจำกัด|เกินโควตา|ครบโควตา|ใช้.*ครบ.*(?:โควตา|จำนวน)|ลองอีกครั้ง(?:ในภายหลัง|วันพรุ่งนี้)|ไม่สามารถสร้างภาพเพิ่ม/i;
 const visible=e=>!!e&&!!(e.getClientRects().length)&&e.ownerDocument.defaultView.getComputedStyle(e).visibility!=='hidden';
 const label=e=>(e.getAttribute('aria-label')||e.getAttribute('title')||e.textContent||'').trim();
 const target=()=>location.origin==='https://gemini.google.com'&&location.pathname.split('/').includes(CHAT);
 const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
 let state={cards:{},events:[]},running=false,pause=false,reference=null,boundEditor=null,pickerCleanup=null;
 const host=document.createElement('div');host.id='mmkt-card-runner';document.documentElement.append(host);const ui=host.attachShadow({mode:'open'});
 ui.innerHTML=`<style>:host{all:initial}*{box-sizing:border-box}[hidden]{display:none!important}.panel{position:fixed;right:16px;bottom:16px;width:335px;max-height:calc(100vh - 32px);overflow:auto;max-width:calc(100vw - 24px);background:#402052;color:#fff7f2;border:1px solid #d5b4d6;border-radius:18px;padding:18px;z-index:2147483646;font:13px/1.6 system-ui;box-shadow:0 12px 60px #180a354d}h2{font-size:17px;margin:0 0 5px}p{margin:5px 0;color:#e1cce5}label{display:block;margin:10px 0}input[type=number]{width:68px;padding:5px;border:1px solid #b899c3;border-radius:6px;background:#2e193d;color:#fff}button,select{font:inherit;border-radius:10px;border:1px solid #cbb2cd;padding:8px 10px;cursor:pointer;background:#f2c7b4;color:#351a44}button:disabled{opacity:.5;cursor:default}.row{display:flex;gap:7px;flex-wrap:wrap}small{font-size:10px;color:#ceb3d6}#status{min-height:44px;margin:12px 0;padding:8px;background:#2d173d;border-radius:8px;overflow-wrap:anywhere}details{margin-top:10px}pre{font:10px/1.5 monospace;white-space:pre-wrap;max-height:140px;overflow:auto}.top{display:flex;justify-content:space-between;align-items:center}.min{background:none;color:#fff;padding:0;width:30px;height:30px}.hidden{display:none}a{color:#ffdcbe}</style>
 <section class="panel"><div class="top"><h2>🐰 แม่หมอกระต่าย · Gemini 1.4</h2><button class="min" id="fold" aria-label="ย่อแผง">−</button></div><div id="body"><p>แนบภาพต้นฉบับทุกใบ · ใช้หน้าแชทนี้</p><small>ไม่ใช้ API key · โควตาตามบัญชี Gemini</small><label>งานรอบนี้ <select id="mode"><option value="new">สร้างภาพใหม่พร้อมชื่อ</option><option value="edit">เพิ่มชื่อภาพเดิม</option><option value="repair">ซ่อมภาพเดิมที่มีตำหนิ</option><option value="legacy">คิวเดิม / กู้ภาพไม่มีชื่อ</option></select></label>
 <label>โมเดลแชท <select id="model-policy"><option value="pro">Pro (ค่าเริ่มต้น · ต้องตรวจยืนยัน)</option><option value="current">ใช้โมเดลที่เลือกเอง</option></select></label><small>โมเดลสร้างภาพขึ้นกับ Gemini; Nano Banana Pro อาจต้องกด Redo with Pro ในผลภาพ</small>
 <div id="title-controls"><p id="title-description">ชื่ออังกฤษตัวพิมพ์ใหญ่ · ขนาดและตำแหน่งเดียวกัน</p>
 <label><input type="checkbox" id="candidate">ทำต้นแบบชื่อ 1 ใบ (ยังไม่มี ref ที่อนุมัติ)</label>
 <label>ภาพชื่อเวอร์ชันแรกที่ชอบ <input id="title-file" type="file" accept="image/png,image/jpeg,image/webp"></label>
 <img id="title-preview" alt="ภาพต้นแบบชื่อที่เลือก" hidden style="width:90px;max-height:145px;object-fit:contain">
 <button id="approve-title" disabled>อนุมัติภาพนี้เป็น ref ตัวอักษร</button><p id="title-state">ยังไม่มี ref ที่อนุมัติ · เลือกไฟล์ใหม่ทุกครั้งหลังรีเฟรช</p>
 <div id="source-controls" hidden><label>จับคู่ภาพเดิมทีละใบ <select id="source-card"></select><input id="source-file" type="file" accept="image/png,image/jpeg,image/webp"></label>
 <label>หรือนำเข้าหลายใบตามชื่อไฟล์ card-id <input id="source-batch" type="file" multiple accept="image/png,image/jpeg,image/webp"></label><div id="repair-controls" hidden><label>จุดที่ต้องซ่อม <select id="repair-issue"><option value="frame">กรอบไม่ครบ / ขาดตรงแถบชื่อ</option><option value="brows">คิ้วข้างเดียว → เติมอีกข้าง</option><option value="both">กรอบและคิ้ว</option><option value="custom">จุดอื่นตามคำอธิบาย</option></select></label><label>รายละเอียดเพิ่มเติม <textarea id="repair-notes" maxlength="1000" rows="2" placeholder="แก้เฉพาะจุดนี้ รักษารูปเดิม" style="width:100%"></textarea></label><button id="queue-repair">เพิ่มใบนี้เข้าคิวซ่อม / ซ่อมอีกครั้ง</button><p>ใช้ชื่อเดิม ไม่ต้องเลือก ref ตัวอักษรใหม่ · เก็บไฟล์เดิมทุกเวอร์ชัน · ตรวจผลเองก่อนรับ · ไม่วนเจนซ้ำอัตโนมัติ</p></div><p id="source-state">ยังไม่ได้นำเข้าภาพเดิม</p><details><summary>ภาพเดิมที่นำเข้า</summary><div id="source-list"></div></details></div></div>
 <label><input type="checkbox" id="skip" checked> ข้าม 5 ใบที่มีภาพแล้ว</label><label>จำนวนรอบนี้ <input type="number" id="count" min="1" max="78" value="1"> ใบ · เว้น <input type="number" id="gap" min="5" max="600" value="15"> วินาที</label><label>เริ่มที่ <select id="first"><option value="">ใบถัดไปที่ยังไม่ทำ</option></select></label><div class="row"><button id="prepare">เตรียมใบถัดไป</button><button id="start">เริ่มอัตโนมัติ</button><button id="pause" disabled>พักหลังใบนี้</button></div><div class="row" style="margin-top:8px"><button id="bind">เลือกช่องพิมพ์</button><button id="clear-unsent">ยังไม่ได้ส่ง — ปลดใบค้าง</button></div><div id="status" role="status" aria-live="polite">กำลังเตรียมคิว…</div><p id="recovery-hint" role="note"></p><div class="row"><button id="save-pending">บันทึกภาพใบค้าง</button><button id="show-download">เปิดตำแหน่งไฟล์</button><button id="reconcile">ยืนยันใบค้าง</button><button id="export">บันทึกสถานะ</button></div><p id="save-location" style="font-size:11px;overflow-wrap:anywhere"></p><details><summary>สถานะคิว / วินิจฉัย</summary><p id="summary"></p><pre id="log"></pre><button id="diagnose">ตรวจองค์ประกอบหน้า</button><p id="diagnostic"></p></details><small>เริ่มทดสอบ 1 ใบก่อน แล้วเพิ่มจำนวนรอบถัดไปได้</small></div></section>`;
 const $=id=>ui.getElementById(id);
 for(const c of DECK){const o=document.createElement('option');o.value=c.id;o.textContent=c.sequence+' · '+c.name;$('first').append(o);$('source-card').append(o.cloneNode(true));}
 const storage={load:async()=>{const data=await chrome.storage.local.get(KEY);return data[KEY];},save:async()=>chrome.storage.local.set({[KEY]:state})};
 const message=async data=>{const r=await chrome.runtime.sendMessage(data);if(r?.ok===false)throw Error(r.error);return r;};
 function log(text){$('status').textContent=text;state.events.push({time:new Date().toISOString(),text});state.events=state.events.slice(-40);$('log').textContent=state.events.map(e=>e.time.slice(11,19)+' '+e.text).join('\n');render();}
 const stageNames={preparing:'แนบภาพหรือใส่ข้อความ (ยังไม่กดส่งอัตโนมัติ)',prepared:'เตรียมข้อความแล้ว (ยังไม่กดส่งอัตโนมัติ)',submitting:'กดส่งแล้ว รอยืนยัน',submitted:'ส่งแล้ว รอภาพ',generated:'มีภาพแล้ว รอดาวน์โหลด',downloading:'กำลังดาวน์โหลด',review:'รอตรวจ'};
 function unresolved(){return queue().find(c=>state.cards[c.id]&&!['pending','downloaded'].includes(state.cards[c.id].status));}
 function render(){const values=Object.values(state.cards);const card=unresolved(),entry=card&&state.cards[card.id];
  $('recovery-hint').textContent=!running&&card?('ใบที่ต้องตรวจ: '+card.name+' · '+(stageNames[entry.status]||entry.status)+' — '+(entry.firstError||entry.error||'ยังไม่ได้ยืนยันว่าบันทึกภาพแล้ว')+' · กด “ยืนยันใบค้าง”; ใช้ UNSENT เฉพาะตรวจแล้วว่าไม่เคยส่ง หรือ SAVED เมื่อดาวน์โหลดแล้ว'):'';
const last=values.filter(v=>v.filename&&v.status==='downloaded').sort((a,b)=>String(b.updated).localeCompare(String(a.updated)))[0];$('save-location').textContent=last?'บันทึกล่าสุด: '+last.filename:'ยังไม่มีภาพที่บันทึกอัตโนมัติสำเร็จ';
$('summary').textContent=`สำเร็จ ${values.filter(v=>v.status==='downloaded').length} · รอตรวจ ${values.filter(v=>!['pending','downloaded'].includes(v.status)).length} · คิวทั้งหมด 78`;for(const id of ['start','prepare','skip','first','count','gap','reconcile','bind','clear-unsent','save-pending','mode','candidate','title-file','source-file','source-batch','source-card','model-policy','repair-issue','repair-notes','queue-repair'])$(id).disabled=running;$('pause').disabled=!running;$('approve-title').disabled=running||!titleCandidate||!!approvedTitle;$('title-controls').hidden=mode==='legacy';$('source-controls').hidden=!['edit','repair'].includes(mode);$('repair-controls').hidden=mode!=='repair';$('candidate').closest('label').hidden=mode==='repair';$('title-file').closest('label').hidden=mode==='repair';$('approve-title').hidden=mode==='repair';$('title-state').hidden=mode==='repair';$('title-preview').hidden=mode==='repair'||!titleCandidate;$('skip').closest('label').hidden=mode==='repair';$('first').closest('label').hidden=mode==='repair';$('title-description').textContent=mode==='repair'?'รักษาภาพและชื่อเดิม · ซ่อมเฉพาะจุดที่เลือก':'ชื่ออังกฤษตัวพิมพ์ใหญ่ · ขนาดและตำแหน่งเดียวกัน';$('skip').disabled=running||['edit','repair'].includes(mode);}
 async function record(card,status,extra={}){state.cards[card.id]={...state.cards[card.id],status,updated:new Date().toISOString(),...extra};await storage.save();render();}
 function assertTarget(){if(!target())throw Error('หยุด: เปิดแชทแม่หมอกระต่ายที่กำหนดก่อน');}
 function roots(base=document){
  const list=[],seen=new Set();
  const visit=root=>{if(!root||seen.has(root))return;seen.add(root);list.push(root);for(const e of root.querySelectorAll('*')){if(e===host)continue;if(e.shadowRoot)visit(e.shadowRoot);if(e.tagName==='IFRAME'){try{if(e.contentDocument&&e.contentDocument.location.origin===location.origin)visit(e.contentDocument);}catch{}}}};
  visit(base);return list;
 }
 function queryAll(selector,base=document){return [...new Set(roots(base).flatMap(root=>Array.from(root.querySelectorAll(selector))))];}
 const allVisible=(selector,root=document)=>queryAll(selector,root).filter(visible);
 const editable=e=>!!e&&(e.tagName==='TEXTAREA'&&!e.disabled&&!e.readOnly||e.isContentEditable||e.hasAttribute('contenteditable')&&e.getAttribute('contenteditable')!=='false');
 function editorCandidates(){return allVisible(SELECTORS.editor).filter(editable).filter(e=>!e.parentElement?.closest('[contenteditable]:not([contenteditable="false"])'));}
 function editor(){
  if(boundEditor?.isConnected&&visible(boundEditor)&&editable(boundEditor))return boundEditor;
  const list=editorCandidates();if(list.length===1)return list[0];
  const named=list.filter(e=>/ask gemini|enter a prompt|message gemini|ถาม gemini|ป้อนพรอมต์|พิมพ์ข้อความ/i.test([label(e),e.getAttribute('placeholder'),e.getAttribute('data-placeholder')].join(' ')));
  if(named.length===1)return named[0];
  throw Error('หาช่องพิมพ์ Gemini ไม่ชัดเจน ('+list.length+' ช่อง) กด “เลือกช่องพิมพ์” แล้วคลิก Ask Gemini');
 }
 function uploadButton(e){return /add files|upload|attach|เพิ่มไฟล์|อัปโหลด|แนบไฟล์/i.test(label(e))||Array.from(e.querySelectorAll('mat-icon,.material-icons,.material-symbols-outlined')).some(i=>/^(?:add|add_2|attach_file|upload|upload_file)$/.test(i.textContent.trim()));}
 function parentElement(e){return e.parentElement||(e.getRootNode()?.host)||null;}
 function composer(e){
  const known=e.closest('input-area-v2,input-area,input-container,form,.input-area-container,.input-container');if(known)return known;
  let a=parentElement(e);for(let i=0;a&&a!==document.body&&a!==document.documentElement&&i<10;i++,a=parentElement(a))if(queryAll('input[type=file]',a).length||allVisible('button',a).some(uploadButton))return a;
  return parentElement(parentElement(e)||e)||parentElement(e);
 }
 const text=e=>e.tagName==='TEXTAREA'?e.value:(e.innerText||e.textContent||'');
 function bindPicker(){
  pickerCleanup?.();let finished=false;const listeners=[];
  const clear=()=>{for(const [root,type,handler] of listeners)root.removeEventListener(type,handler,true);clearTimeout(timer);pickerCleanup=null;};
  const pick=event=>{if(finished||event.composedPath().includes(host))return;
   let e=event.composedPath().find(n=>n?.nodeType===1&&editable(n));
   if(!e)return;while(e.parentElement?.isContentEditable)e=e.parentElement;
   if(!visible(e))return;finished=true;event.preventDefault();event.stopPropagation();boundEditor=e;clear();e.focus();
   const old=e.style.outline;e.style.outline='3px solid #c28ed1';setTimeout(()=>e.style.outline=old,1800);log('เลือกช่องพิมพ์แล้ว — กดเตรียมใบถัดไปได้ (ยังไม่ส่ง)');
  };
  for(const root of roots()){root.addEventListener('click',pick,true);listeners.push([root,'click',pick]);}
  const timer=setTimeout(()=>{clear();log('หมดเวลาเลือกช่องพิมพ์ กดเลือกใหม่ได้');},30000);pickerCleanup=clear;
  log('คลิกในช่อง Ask Gemini ด้านล่างของหน้าเว็บ ไม่ต้องพิมพ์หรือกดส่ง');
 }

 function responseRoots(){return queryAll(SELECTORS.responses);}
 function queryRoots(){return queryAll(SELECTORS.queries);}
 function busy(){return allVisible('button').some(b=>/stop response|stop generating|หยุดการตอบ|หยุดสร้าง/i.test(label(b))||b.classList.contains('stop-button'));}

 // Inspect only the model picker / its menu, never a plan or upgrade button.
 const proName=value=>/^(?:gemini\s+[0-9.]+\s+)?pro(?:\s|$)/i.test(value.trim())&&!/upgrade|subscribe|buy|อัปเกรด|สมัคร|ซื้อ/i.test(value);
 function modelPicker(){
  const known=allVisible('button[data-test-id="bard-mode-menu-button"],button[data-testid="model-selector"],button.input-area-switch,button[aria-label*="model" i],button[aria-label*="โมเดล"]');
  const usable=e=>!e.disabled&&!/upgrade|subscribe|plan|อัปเกรด|สมัคร/i.test(label(e));
  const candidates=(known.length?known:allVisible('button[aria-haspopup="menu"],button[aria-haspopup="listbox"]')).filter(usable).filter(e=>known.includes(e)||/^(?:fast|flash|thinking|pro)(?:\s|$)/i.test(label(e)));
  if(candidates.length!==1)throw Error('หาเมนูโมเดลไม่ชัดเจน กรุณาเลือก Pro บนหน้า Gemini ก่อน ไม่ส่งด้วยโมเดลอื่น');return candidates[0];
 }
 function isPro(picker){return proName(label(picker))||proName(picker.innerText||picker.textContent||'');}
 function assertProModel(){if($('model-policy').value==='pro'&&!isPro(modelPicker()))throw Error('โมเดลไม่ใช่ Pro จึงหยุดก่อนส่ง กรุณาตรวจเมนูโมเดล');}
 async function ensureProModel(){
  if($('model-policy').value!=='pro')return;
  const picker=modelPicker();if(isPro(picker))return;
  picker.click();
  const option=await waitFor(()=>{
   const options=allVisible('[role="menuitem"],[role="menuitemradio"],[role="option"]').filter(e=>proName(label(e))&&!e.disabled&&e.getAttribute('aria-disabled')!=='true');
   if(options.length>1)throw Error('พบตัวเลือก Pro หลายรายการ กรุณาเลือกโมเดลเองก่อน');return options[0]||false;
  },5000,'ไม่พบ Pro ที่ใช้งานได้ในเมนู จึงหยุดคิว ไม่เปลี่ยนโมเดลหรือซื้อแพ็กเกจแทน');
  option.click();await waitFor(()=>{try{return isPro(modelPicker());}catch{return false;}},5000,'ยังยืนยันว่าเลือก Pro ไม่ได้ จึงยังไม่ส่ง');
  log('เลือกโมเดลแชท Pro แล้ว');
 }
 function inspectBlockers(root){
  const alerts=allVisible('[role="alert"],[role="dialog"]');const content=[root?.innerText||'',...alerts.map(e=>e.innerText)].join('\n');
  if(quota.test(content))throw Error('หยุด: Gemini แจ้งโควตา/ขีดจำกัด กรุณารอแล้วตรวจบัญชี ไม่ส่งซ้ำ');
  if(/verify (?:you are|that you are) human|ยืนยันว่าคุณเป็นมนุษย์|unusual traffic/i.test(content))throw Error('หยุด: ให้เจ้าของจัดการการยืนยันตัวตนในหน้าเว็บก่อน');
 }
 async function waitFor(fn,timeout,description){const until=Date.now()+timeout;while(Date.now()<until){assertTarget();const result=await fn();if(result)return result;await delay(350);}throw Error(description);}
 const attachmentImages=root=>queryAll('img',root).filter(img=>visible(img)&&/^(?:blob:|data:image)|googleusercontent/.test(img.currentSrc||img.src)&&!/(?:avatar|profile)/i.test(img.alt||''));
 async function attach(e,files){
  let box=composer(e);if(!box)throw Error('หาบริเวณแนบไฟล์ไม่พบ กดเลือกช่องพิมพ์ก่อน');
  if(attachmentImages(box).length||/IMG_5392\.JPG/i.test((box.innerText||'').replace(text(e),'')))throw Error('มีไฟล์แนบค้างอยู่ กรุณาจัดการในช่องพิมพ์ก่อนเริ่ม');
  if(!reference){const r=await fetch(chrome.runtime.getURL('assets/IMG_5392.JPG'));if(!r.ok)throw Error('โหลดภาพต้นฉบับในextensionไม่สำเร็จ');reference=await r.blob();}
  const view=e.ownerDocument.defaultView;
  const expectedFiles=[new view.File([reference],'IMG_5392.JPG',{type:'image/jpeg'}),...files];
  for(const file of expectedFiles){
  const beforeCount=attachmentImages(composer(e)).length;
  const transfer=new view.DataTransfer();transfer.items.add(file);
  const ready=()=>{box=composer(e);return !queryAll('[role=progressbar],mat-progress-spinner',box).length&&((box.innerText||'').includes(file.name)||attachmentImages(box).length>beforeCount);};
  const findInput=()=>queryAll('input[type=file]').find(i=>!i.accept||/image|\.jpg|\.jpeg|\*/i.test(i.accept));
  let input=findInput();
  if(!input){
   // Gemini may not create a file input until the + menu opens. First use its image-paste handler.
   e.focus();const event=new view.ClipboardEvent('paste',{bubbles:true,cancelable:true,composed:true,clipboardData:transfer});const accepted=!e.dispatchEvent(event);
   const until=Date.now()+1800;while(Date.now()<until){if(ready())break;await delay(150);}
   if(ready())continue;
   if(accepted||queryAll('[role=progressbar],mat-progress-spinner',box).length){await waitFor(ready,30000,'วางภาพแล้วแต่ยังไม่เห็นภาพแนบพร้อมส่ง จึงพักคิว');continue;}
   const buttons=allVisible('button',box).filter(uploadButton);
   if(buttons.length!==1)throw Error('ไม่พบปุ่ม + แนบไฟล์ในบริเวณช่องพิมพ์ กรุณากด + เปิดเมนูไว้แล้วลองเตรียมอีกครั้ง');
   log('เปิดเมนู + เพื่อแนบ JPG ต้นฉบับ');buttons[0].click();await delay(400);input=findInput();
   if(!input){const items=allVisible('[role=menuitem],button').filter(b=>/upload files|upload from computer|อัปโหลดไฟล์|อัปโหลดจากคอมพิวเตอร์/i.test(label(b)));if(items.length!==1)throw Error('กรุณาเลือก Upload files ในเมนู + ก่อน ยังไม่ส่งข้อความ');items[0].click();await delay(400);input=findInput();}
  }
  if(!input)throw Error('ยังไม่พบช่องอัปโหลด กรุณาเปิด + → Upload files แล้วลองเตรียมใหม่');
  input.files=transfer.files;input.dispatchEvent(new view.Event('input',{bubbles:true,composed:true}));input.dispatchEvent(new view.Event('change',{bubbles:true,composed:true}));
  await waitFor(ready,30000,'ไม่เห็นภาพแนบ '+file.name+' ในช่องพิมพ์ จึงหยุดก่อนส่ง');
  }
  await waitFor(()=>{const box=composer(e);return !queryAll('[role=progressbar],mat-progress-spinner',box).length&&(expectedFiles.every(f=>(box.innerText||'').includes(f.name))||attachmentImages(box).length>=expectedFiles.length);},30000,'ภาพแนบไม่ครบทุก reference จึงยังไม่ส่ง');
 }

 function fill(e,prompt,card){
  e.focus();
  if(e.tagName==='TEXTAREA'){Object.getOwnPropertyDescriptor(e.ownerDocument.defaultView.HTMLTextAreaElement.prototype,'value').set.call(e,prompt);e.dispatchEvent(new Event('input',{bubbles:true}));}
  else{const doc=e.ownerDocument,selection=doc.getSelection(),range=doc.createRange();range.selectNodeContents(e);selection.removeAllRanges();selection.addRange(range);if(!doc.execCommand('insertText',false,prompt)){e.textContent=prompt;e.dispatchEvent(new InputEvent('input',{bubbles:true,inputType:'insertText',data:prompt}));}}
  if(!text(e).includes('CARD SCENE: '+card.name.toUpperCase()))throw Error('ตรวจข้อความในช่องพิมพ์ไม่ผ่าน จึงยังไม่ส่ง');
 }
 function sendButton(){
  const e=editor(),box=composer(e);
  const isSend=b=>!b.disabled&&(b.matches('.send-button,[data-testid="send-button"]')||/^send(?: message| prompt)?$|^submit$|^ส่ง(?:ข้อความ|พรอมต์)?$/i.test(label(b))||Array.from(b.querySelectorAll('mat-icon,.material-icons,.material-symbols-outlined')).some(i=>/^(?:send|arrow_upward)$/.test(i.textContent.trim())));
  let list=allVisible('button',box).filter(isSend);if(!list.length)list=allVisible('button').filter(isSend);
  if(list.length!==1)throw Error('หาปุ่มส่งที่ชัดเจนไม่พบ จึงยังไม่ส่ง');return list[0];
 }

 function queue(){if(mode==='repair')return DECK.filter(c=>state.cards[c.id]&&state.cards[c.id].status!=='downloaded');const first=$('first').value,start=first?DECK.findIndex(c=>c.id===first):0;return DECK.slice(start).filter(c=>(mode==='edit'?sourceArt.has(c.id):(!$('skip').checked||!c.existing_generated_image))&&state.cards[c.id]?.status!=='downloaded');}
 function generatedImages(root){return queryAll('img',root).filter(i=>i.complete&&i.naturalWidth>=256&&i.naturalHeight>=256&&!/image\/svg|avatar|profile/i.test((i.currentSrc||i.src)+' '+i.alt));}
 async function imageData(url){
  if(url.startsWith('data:image/'))return url;
  const parsed=new URL(url,location.href);
  if(parsed.protocol==='blob:'&&!url.startsWith('blob:'+location.origin+'/'))throw Error('ไม่ใช่ภาพblobของแชทนี้');
  if(!['blob:','https:'].includes(parsed.protocol))throw Error('ชนิดลิงก์ภาพไม่รองรับ');
  if(parsed.protocol==='https:'&&!(parsed.hostname==='gemini.google.com'||parsed.hostname.endsWith('.googleusercontent.com')))throw Error('ไม่ใช่ลิงก์ภาพGemini');
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),30000);
  let response;try{response=await fetch(url,{credentials:'include',signal:controller.signal});}finally{clearTimeout(timer);}
  if(!response.ok)throw Error('อ่านภาพไม่สำเร็จ HTTP '+response.status);
  const blob=await response.blob();if(!/^image\/(png|jpeg|webp|gif|avif)$/.test(blob.type)||blob.size>24*1024*1024)throw Error('ไฟล์ไม่ใช่ภาพที่รองรับหรือใหญ่เกิน24MB');
  return await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result);reader.onerror=()=>reject(Error('อ่านbytesภาพไม่สำเร็จ'));reader.readAsDataURL(blob);});
 }
 async function download(card,img){
  const url=img.currentSrc||img.src;await record(card,'generated',{imageUrl:url.startsWith('data:')?null:url,sourceKind:url.split(':',1)[0]});log('กำลังบันทึกภาพ: '+card.name);
  let d;
  if(url.startsWith('blob:')||url.startsWith('data:'))d=await message({type:'mmkt:download-data',cardId:card.id,variant:mode==='legacy'?'original':mode==='repair'?'repair-v1':'title-v1',dataUrl:await imageData(url)});
  else d=await message({type:'mmkt:download',cardId:card.id,variant:mode==='legacy'?'original':mode==='repair'?'repair-v1':'title-v1',url});
  await record(card,'downloading',{downloadId:d.downloadId});
  const result=await waitFor(async()=>{const r=await message({type:'mmkt:download-status',downloadId:d.downloadId});if(['interrupted','invalid','missing'].includes(r.state))throw Error('ดาวน์โหลดไม่สำเร็จ: '+(r.error||r.state)+' — ไม่ส่งพรอมต์นี้ซ้ำ');return r.state==='complete'?r:null;},120000,'ยังยืนยันดาวน์โหลดไม่สำเร็จ จึงพักคิว ไม่เจนซ้ำ');
  await record(card,'downloaded',{filename:result.filename,error:null,firstError:null,qualityStatus:'owner-review-required'});log('บันทึกแล้ว: '+card.name);
 }
 function existingImage(card){
  const entry=state.cards[card.id]||{},responses=responseRoots();
  const matches=q=>{const t=q.innerText||q.textContent||'';return t.toUpperCase().includes('CARD SCENE: '+card.name.toUpperCase())&&(mode==='legacy'||!!entry.jobToken&&t.includes(entry.jobToken));};
  if(entry.imageUrl){const exact=responses.flatMap(generatedImages).filter(img=>(img.currentSrc||img.src)===entry.imageUrl);if(exact.length===1)return exact[0];}
  // Resolve a renewed blob URL only when the associated user query identifies this card.
  for(const root of responses){const container=root.closest('conversation-container,[data-message-pair]');const queries=container?queryAll('user-query',container):[];if(queries.some(matches)){const images=generatedImages(root);if(images.length===1)return images[0];}}
  const query=queryRoots().at(-1),last=responses.at(-1);
  if(Number.isInteger(entry.baseline)&&responses.length===entry.baseline+1&&query&&matches(query)){const images=generatedImages(last);if(images.length===1)return images[0];}
  return null;
 }
 async function saveExisting(card){const entry=state.cards[card.id]||{};if(Number.isInteger(entry.downloadId)){let result=null;try{result=await message({type:'mmkt:download-status',downloadId:entry.downloadId});}catch{}if(result?.state==='complete'){await record(card,'downloaded',{filename:result.filename,error:null,firstError:null});log('บันทึกแล้ว: '+card.name);return;}if(result?.state==='in_progress')throw Error('ไฟล์ใบนี้กำลังดาวน์โหลดอยู่ รอให้เสร็จแล้วกดบันทึกใบค้างอีกครั้ง โดยไม่เจนซ้ำ');}const img=existingImage(card);if(!img)throw Error('ไม่พบภาพที่ตรงกับ '+card.name+' ให้กดบันทึกภาพใบค้างแล้วคลิกภาพนั้น — ไม่ต้องเจนใหม่');await download(card,img);}
 async function pickExisting(card){
  log('คลิกภาพ '+card.name+' ที่เจนแล้วในแชท เพื่อบันทึกภาพเดิม (ไม่ใช่รูปต้นฉบับที่แนบ)');
  return await new Promise((resolve,reject)=>{
   const listeners=[];const clear=()=>{clearTimeout(timer);for(const [root,handler] of listeners)root.removeEventListener('click',handler,true);};
   const choose=event=>{if(event.composedPath().includes(host))return;const candidates=responseRoots().flatMap(generatedImages).filter(img=>{const r=img.getBoundingClientRect();return event.clientX>=r.left&&event.clientX<=r.right&&event.clientY>=r.top&&event.clientY<=r.bottom;});if(candidates.length!==1)return;event.preventDefault();event.stopPropagation();if(!confirm('บันทึกภาพที่เลือกเป็น '+card.name+' ใช่ไหม?'))return;clear();resolve(candidates[0]);};
   for(const root of roots()){root.addEventListener('click',choose,true);listeners.push([root,choose]);}
   const timer=setTimeout(()=>{clear();reject(Error('หมดเวลาเลือกภาพใบค้าง กดใหม่ได้โดยไม่เจนซ้ำ'));},30000);
  });
 }

 async function finish(card,baseline){
  let stable='',since=0;
  const img=await waitFor(()=>{
   const roots=responseRoots(),root=roots.length>baseline?roots.at(-1):null;inspectBlockers(root);if(!root)return false;
   const images=generatedImages(root);if(images.length>1)throw Error('พบภาพมากกว่าหนึ่งภาพในคำตอบ ให้ตรวจและดาวน์โหลดใบนี้เองก่อนทำต่อ');
   if(images.length!==1||busy()){stable='';return false;}
   const source=images[0].currentSrc||images[0].src;if(source!==stable){stable=source;since=Date.now();}
   return Date.now()-since>=2000?images[0]:false;
  },600000,'ยังไม่พบภาพใหม่ที่เสร็จครบ จึงพักคิว กรุณาตรวจคำตอบGeminiก่อนทำต่อ');
  await download(card,img);
 }
 async function prepare(card,submit){
  assertTarget();inspectBlockers(null);if(busy())throw Error('Geminiกำลังตอบอยู่ รอให้จบก่อน');
  const old=state.cards[card.id];if(submit&&old&&['generated','downloading'].includes(old.status)){await saveExisting(card);return;}if(old&&!['pending','prepared'].includes(old.status))throw Error('มีใบค้าง '+card.name+' · '+(stageNames[old.status]||old.status)+' กรุณากดยืนยันใบค้างก่อน ไม่ส่งซ้ำอัตโนมัติ');
  const e=editor();if(text(e).trim())throw Error('ช่องพิมพ์มีข้อความอยู่แล้ว กรุณาจัดการร่างเดิมก่อนเริ่ม');
  const job=await titleJob(card);await ensureProModel();
  await record(card,'preparing',{baseline:responseRoots().length,...job.metadata,requestedChatModel:$('model-policy').value,verifiedChatModel:$('model-policy').value==='pro'?'Pro':null});log('แนบภาพอ้างอิง: '+card.name);
  await attach(e,job.files);fill(e,job.prompt,card);await record(card,'prepared');
  if(!submit){log('เตรียม '+card.name+' พร้อมภาพแล้ว — คุณตรวจและกดส่งเองได้');return;}
  const button=await waitFor(()=>{try{return sendButton();}catch{return false;}},30000,'ปุ่มส่งยังไม่พร้อม จึงพักคิว');
  assertProModel();
  const baseline=responseRoots().length,queries=queryRoots().length;
  // Persist uncertainty BEFORE clicking: reloading never silently resends a job.
  await record(card,'submitting',{baseline});button.click();
  await waitFor(()=>{inspectBlockers(responseRoots().length>baseline?responseRoots().at(-1):null);return (!text(e).trim()&&queryRoots().length>queries)||responseRoots().length>baseline;},30000,'ยังยืนยันว่าส่งแล้วไม่ได้ ให้ตรวจแชทและกดยืนยันใบค้างก่อน');
  await record(card,'submitted');log('กำลังรอภาพ: '+card.name);await finish(card,baseline);
 }
 async function run(submit){
  if(running)return;let card=null,locked=false;
  try{assertTarget();await message({type:'mmkt:lock'});locked=true;running=true;pause=false;render();
   const count=Math.max(1,Math.min(78,Number($('count').value)||1)),gap=Math.max(5,Number($('gap').value)||15);
   const jobs=queue().slice(0,submit&&!(mode!=='legacy'&&$('candidate').checked)?count:1);if(!jobs.length){log(mode==='repair'?'นำเข้าภาพเดิม เลือกจุดแก้ แล้วกดเพิ่มใบนี้เข้าคิวซ่อม':mode==='edit'&&!sourceArt.size?'นำเข้าภาพเดิมก่อน โดยเลือกไพ่และไฟล์ภาพให้ตรงกัน':'คิวที่เลือกทำครบแล้ว');return;}
   for(let i=0;i<jobs.length;i++){card=jobs[i];await prepare(card,submit);if(!submit||pause)break;if(i<jobs.length-1){log('พัก '+gap+' วินาทีก่อนใบถัดไป');for(let j=0;j<gap*2&&!pause;j++){assertTarget();await delay(500);}if(pause)break;}}
   if(submit)log(pause?'พักคิวแล้ว เริ่มต่อได้':'จบรอบแล้ว ตรวจภาพก่อนเริ่มรอบถัดไป');
  }catch(e){if(card&&state.cards[card.id]){const current=state.cards[card.id]||{};if(!e.message.startsWith('มีใบค้าง '))await record(card,current.status||'review',{error:e.message,firstError:current.firstError||e.message});}log(e.message);}
  finally{running=false;if(locked)try{await message({type:'mmkt:unlock'});}catch{}await storage.save();render();}
 }
 $('start').onclick=()=>run(true);$('prepare').onclick=()=>run(false);$('pause').onclick=()=>{pause=true;log('จะพักเมื่อจบใบปัจจุบัน โดยไม่ส่งใบถัดไป');};
 $('fold').onclick=()=>{$('body').classList.toggle('hidden');$('fold').textContent=$('body').classList.contains('hidden')?'+':'−';};
 $('export').onclick=()=>{const blob=new Blob([JSON.stringify({chatId:CHAT,...state},null,2)],{type:'application/json'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=mode==='legacy'?'maemorkratai-gemini-progress.json':mode==='repair'?'maemorkratai-gemini-repair-progress.json':'maemorkratai-gemini-title-progress.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),5000);};
 $('show-download').onclick=async()=>{try{const r=await message({type:'mmkt:show-download'});log(r.found?'เปิดตำแหน่งไฟล์แล้ว: '+r.filename:'ยังไม่มีภาพบันทึกอัตโนมัติ เปิดโฟลเดอร์ดาวน์โหลดของChromeให้แล้ว');}catch(e){log(e.message);}};
 $('save-pending').onclick=async()=>{if(running)return;let locked=false;try{const card=unresolved();if(!card)throw Error('ไม่มีภาพใบค้างให้บันทึก');if(!['generated','downloading','submitted'].includes(state.cards[card.id].status))throw Error('ใบนี้ยังไม่มีหลักฐานว่าส่งแล้ว จึงไม่เลือกภาพจากประวัติให้');await message({type:'mmkt:lock'});locked=true;running=true;render();const img=existingImage(card)||await pickExisting(card);await download(card,img);}catch(e){log(e.message);}finally{running=false;if(locked)try{await message({type:'mmkt:unlock'});}catch{}render();}};
 $('bind').onclick=bindPicker;
 async function resetUnsent(pending){
  const e=editor();if(text(e).trim()||attachmentImages(composer(e)).length){log('ยังมีร่างหรือไฟล์แนบ กรุณาจัดการในช่องพิมพ์ก่อน');return;}
  await record(pending,'pending',{manuallyVerifiedUnsent:true,error:null,firstError:null});log('ปลดใบค้างแล้ว — กดเตรียมใบถัดไปได้');
 }
 $('clear-unsent').onclick=async()=>{try{const pending=unresolved();if(!pending){log('ไม่มีใบค้างให้ปลด');return;}editor();if(!confirm('ยืนยันว่า '+pending.name+' ยังไม่เคยถูกส่งไปในแชทใช่ไหม?\nถ้าส่งไปแล้วให้ยกเลิก เพื่อไม่ให้เจนซ้ำ'))return;await resetUnsent(pending);}catch(e){log(e.message);}};
 $('diagnose').onclick=()=>{let e=null;try{e=editor();}catch{}const files=queryAll('input[type=file]').length;$('diagnostic').textContent=`ช่องพิมพ์ ${e?1:0} (พบตัวเลือก ${editorCandidates().length}) · ช่องไฟล์ ${files}${files?'':' — อาจยังไม่เปิดเมนู +'} · คำตอบ ${responseRoots().length} · อยู่แชทที่กำหนด ${target()?'ใช่':'ไม่ใช่'}`;if(!e)log('กด “เลือกช่องพิมพ์” แล้วคลิกช่อง Ask Gemini ด้านล่าง');};
 $('reconcile').onclick=async()=>{try{
  const pending=queue().find(c=>state.cards[c.id]&&state.cards[c.id].status!=='downloaded');if(!pending){log('ไม่มีใบค้างในคิวที่เลือก');return;}
  const entry=state.cards[pending.id];
  const choice=prompt('ใบค้าง: '+pending.name+' ('+entry.status+')\nพิมพ์ SAVED ถ้าตรวจภาพและดาวน์โหลดไว้แล้ว\nพิมพ์ UNSENT เฉพาะเมื่อยืนยันว่าไม่เคยส่ง และล้างร่าง/ไฟล์แนบแล้ว\nพิมพ์ RETRY เฉพาะตรวจแล้วว่าไม่ได้ภาพและโควตากลับมาแล้ว\nกดยกเลิกเพื่อคงสถานะเดิม');
  if(choice==='SAVED'){await record(pending,'downloaded',{manuallyVerified:true});log('เจ้าของยืนยันว่าบันทึก '+pending.name+' แล้ว');}
  if(choice==='UNSENT'||choice==='RETRY'){if(text(editor()).trim()||attachmentImages(composer(editor())).length){log('ยังมีร่าง/ไฟล์แนบ กรุณาจัดการก่อน');return;}await record(pending,'pending',{manuallyVerifiedUnsent:choice==='UNSENT',manuallyRequestedRetry:choice==='RETRY',error:null,firstError:null});log(choice==='RETRY'?'เจ้าของเลือกให้ลองใบนี้ใหม่ในรอบถัดไป':'เจ้าของยืนยันว่าไม่เคยส่ง '+pending.name+' แล้ว');}
 }catch(e){log(e.message);}
 };


 function repairPreset(){const id=$('source-card').value;$('repair-issue').value=id==='the-emperor'?'frame':id==='the-chariot'?'brows':'both';$('repair-notes').value='';}
 $('source-card').onchange=repairPreset;
 $('queue-repair').onclick=()=>configure(async()=>{
  if(mode!=='repair')return;
  const id=$('source-card').value,card=DECK.find(c=>c.id===id),source=sourceArt.get(id),old=state.cards[id];
  if(!source)throw Error('เลือกไฟล์ภาพเดิมของ '+card.name+' ก่อน');
  if(old&&old.status!=='downloaded'&&!(old.status==='pending'&&!old.jobToken))throw Error('ใบนี้มีงานซ่อมค้างอยู่ ใช้บันทึกภาพใบค้างหรือยืนยันใบค้างก่อน ไม่เพิ่มงานซ้ำ');
  const repair={issue:$('repair-issue').value,notes:$('repair-notes').value.trim()};
  if(repair.issue==='custom'&&!repair.notes)throw Error('ระบุจุดที่ต้องการแก้ก่อน');
  if(old?.status==='downloaded'){state.history=state.history||[];state.history.push({cardId:id,...old});}
  state.cards[id]={status:'pending',attempt:old?.status==='pending'?old.attempt:(old?.attempt||0)+1,repair,sourceSha256:source.hash,updated:new Date().toISOString()};
  await storage.save();log('เพิ่ม '+card.name+' เข้าคิวซ่อมแล้ว · กดเตรียมหรือเริ่มเมื่อต้องการส่ง');
 });
 async function readImage(file){
  if(!file||!/^image\/(png|jpeg|webp)$/.test(file.type)||file.size>12*1024*1024)throw Error('เลือกภาพ JPG/PNG/WebP ไม่เกิน 12 MB');
  const bitmap=await createImageBitmap(file);if(bitmap.width<128||bitmap.height<128){bitmap.close();throw Error('ภาพเล็กเกินไป');}bitmap.close();
  const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',await file.arrayBuffer())),v=>v.toString(16).padStart(2,'0')).join('');
  return {file,hash};
 }
 function namedImage(image,name){const extension={"image/jpeg":"jpg","image/png":"png","image/webp":"webp"}[image.file.type];return new File([image.file],name+'.'+extension,{type:image.file.type});}
 async function titleJob(card){
  if(mode==='legacy')return {files:[],prompt:TITLES.prompt(card,{mode}),metadata:{mode}};
  if(mode!=='repair'&&!approvedTitle&&!$('candidate').checked)throw Error('เลือกและอนุมัติ ref ตัวอักษรก่อน หรือเลือกทำต้นแบบชื่อ 1 ใบ');
  const source=sourceArt.get(card.id);if(['edit','repair'].includes(mode)&&!source)throw Error('ยังไม่มีภาพเดิมของ '+card.name);
  if(mode==='repair'&&state.cards[card.id]?.sourceSha256!==source.hash)throw Error('ภาพเดิมเปลี่ยนหลังเข้าคิว ให้กดเพิ่มใบนี้เข้าคิวซ่อมอีกครั้งเพื่อยืนยันภาพใหม่');
  const files=[];if(approvedTitle)files.push(namedImage(approvedTitle,'MMKT_APPROVED_TITLE_REF'));
  const sourceName='TARGET_ORIGINAL_'+card.id;if(['edit','repair'].includes(mode))files.push(namedImage(source,sourceName));
  const jobToken='MMKT-TITLE-JOB-'+crypto.randomUUID();
  return {files,prompt:TITLES.prompt(card,{mode,approved:!!approvedTitle,sourceName,repair:state.cards[card.id]?.repair})+'\n\nREQUEST ID (metadata only, NEVER print on image): '+jobToken,metadata:{jobToken,mode,titleSystem:'title-v1',titleReferenceSha256:approvedTitle?.hash||null,sourceSha256:['edit','repair'].includes(mode)?source.hash:null,candidate:mode!=='repair'&&!approvedTitle}};
 }
 function sourceSummary(){
  $('source-state').textContent='นำเข้าภาพเดิม '+sourceArt.size+' ใบ · เก็บเฉพาะแท็บนี้';
  for(const img of $('source-list').querySelectorAll('img'))URL.revokeObjectURL(img.src);
  $('source-list').replaceChildren();
  for(const [id,value] of sourceArt){const line=document.createElement('p'),img=document.createElement('img');img.src=URL.createObjectURL(value.file);img.alt=DECK.find(c=>c.id===id).name;img.style.cssText='width:35px;vertical-align:middle;margin-right:5px';line.append(img,document.createTextNode(id));$('source-list').append(line);}
  render();
 }
 async function configure(fn){if(running)return;running=true;render();try{await fn();}catch(e){log(e.message);}finally{running=false;render();}}
 $('title-file').onchange=()=>configure(async()=>{
  approvedTitle=null;titleCandidate=null;$('title-state').textContent='ยังไม่ได้อนุมัติภาพใหม่';$('title-preview').hidden=true;
  const image=await readImage($('title-file').files[0]);titleCandidate=image;
  URL.revokeObjectURL($('title-preview').src);$('title-preview').src=URL.createObjectURL(image.file);$('title-preview').hidden=false;
  log('ตรวจชื่อ ขนาดตัวอักษร และตำแหน่งในภาพ แล้วกดอนุมัติ ref');
 });
 $('approve-title').onclick=()=>{if(running||!titleCandidate)return;approvedTitle=titleCandidate;$('candidate').checked=false;$('title-state').textContent='อนุมัติ ref: '+titleCandidate.file.name;log('จะใช้ภาพที่อนุมัตินี้คุมตัวอักษรทุกใบ พร้อม art style เดิม');};
 $('source-file').onchange=()=>configure(async()=>{const image=await readImage($('source-file').files[0]),id=$('source-card').value;sourceArt.set(id,image);$('first').value=id;sourceSummary();repairPreset();log('จับคู่ภาพเดิมกับ '+DECK.find(c=>c.id===id).name+(mode==='repair'?' แล้ว เลือกจุดแก้และกดเพิ่มเข้าคิวซ่อม':' แล้ว ตรวจภาพในรายการก่อนเริ่ม'));});
 $('source-batch').onchange=()=>configure(async()=>{
  const staged=new Map();
  for(const file of $('source-batch').files){const card=TITLES.cardForFile(file.name,DECK);if(!card)throw Error('ไม่รู้ว่าไฟล์ '+file.name+' เป็นไพ่ใด ให้จับคู่ทีละใบหรือเปลี่ยนชื่อเป็น card-id');if(staged.has(card.id)||sourceArt.has(card.id))throw Error('ภาพซ้ำสำหรับ '+card.name+' ใช้จับคู่ทีละใบเพื่อเปลี่ยนภาพ');staged.set(card.id,await readImage(file));}
  for(const [id,image] of staged)sourceArt.set(id,image);$('first').value='';sourceSummary();log('นำเข้าภาพเดิมแล้ว ตรวจรายการคู่ภาพและชื่อก่อนเริ่ม');
 });
 $('mode').onchange=()=>configure(async()=>{
  await storage.save();mode=$('mode').value;KEY=(mode==='legacy'?'mmkt-card-runner-v1-':mode==='repair'?'mmkt-card-runner-repair-v1-':'mmkt-card-runner-title-v1-')+CHAT;
  state=(await storage.load())||{cards:{},events:[]};$('first').value='';$('skip').checked=!['edit','repair'].includes(mode);repairPreset();
  log(mode==='legacy'?'เปิดคิวเดิมแล้ว · สถานะภาพเก่ายังคงอยู่':mode==='repair'?'เปิดคิวซ่อมภาพแล้ว · นำเข้าภาพและเลือกจุดแก้':'เปิดคิวชื่อไพ่แล้ว · แยกจากภาพเดิม');
 });

 storage.load().then(saved=>{if(saved?.cards)state=saved;log(target()?'พร้อม · เริ่มที่ 1 ใบเพื่อทดสอบ':'เปิดแชทแม่หมอกระต่ายที่กำหนดก่อนเริ่ม');});
 globalThis.MMKT_RUNNER={SELECTORS,generatedImages,queue,target,editorCandidates};
})();
