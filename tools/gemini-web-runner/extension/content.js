(() => {
 'use strict';
 if(globalThis.MMKT_RUNNER)return;
 const CHAT='c1051ca2e5090320',KEY='mmkt-card-runner-v1-'+CHAT;
 const DECK=globalThis.MMKT_DECK;
 const SELECTORS={editor:'textarea:not([disabled]):not([readonly]),[contenteditable]:not([contenteditable="false"]),.ql-editor[contenteditable],[role="textbox"][contenteditable]',responses:'model-response',queries:'user-query'};
 const quota=/you(?:’|')?ve reached|reached (?:your|the).*(?:limit|quota)|quota.{0,35}(?:exceeded|limit)|too many requests|try again (?:later|tomorrow)|daily limit|ถึงขีดจำกัด|เกินโควตา|ครบโควตา|ใช้.*ครบ.*(?:โควตา|จำนวน)|ลองอีกครั้ง(?:ในภายหลัง|วันพรุ่งนี้)|ไม่สามารถสร้างภาพเพิ่ม/i;
 const visible=e=>!!e&&!!(e.getClientRects().length)&&e.ownerDocument.defaultView.getComputedStyle(e).visibility!=='hidden';
 const label=e=>(e.getAttribute('aria-label')||e.getAttribute('title')||e.textContent||'').trim();
 const target=()=>location.origin==='https://gemini.google.com'&&location.pathname.split('/').includes(CHAT);
 const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
 let state={cards:{},events:[]},running=false,pause=false,reference=null,boundEditor=null,pickerCleanup=null;
 const host=document.createElement('div');host.id='mmkt-card-runner';document.documentElement.append(host);const ui=host.attachShadow({mode:'open'});
 ui.innerHTML=`<style>:host{all:initial}*{box-sizing:border-box}.panel{position:fixed;right:16px;bottom:16px;width:335px;max-height:calc(100vh - 32px);overflow:auto;max-width:calc(100vw - 24px);background:#402052;color:#fff7f2;border:1px solid #d5b4d6;border-radius:18px;padding:18px;z-index:2147483646;font:13px/1.6 system-ui;box-shadow:0 12px 60px #180a354d}h2{font-size:17px;margin:0 0 5px}p{margin:5px 0;color:#e1cce5}label{display:block;margin:10px 0}input[type=number]{width:68px;padding:5px;border:1px solid #b899c3;border-radius:6px;background:#2e193d;color:#fff}button,select{font:inherit;border-radius:10px;border:1px solid #cbb2cd;padding:8px 10px;cursor:pointer;background:#f2c7b4;color:#351a44}button:disabled{opacity:.5;cursor:default}.row{display:flex;gap:7px;flex-wrap:wrap}small{font-size:10px;color:#ceb3d6}#status{min-height:44px;margin:12px 0;padding:8px;background:#2d173d;border-radius:8px;overflow-wrap:anywhere}details{margin-top:10px}pre{font:10px/1.5 monospace;white-space:pre-wrap;max-height:140px;overflow:auto}.top{display:flex;justify-content:space-between;align-items:center}.min{background:none;color:#fff;padding:0;width:30px;height:30px}.hidden{display:none}a{color:#ffdcbe}</style>
 <section class="panel"><div class="top"><h2>🐰 แม่หมอกระต่าย · Gemini 1.2</h2><button class="min" id="fold" aria-label="ย่อแผง">−</button></div><div id="body"><p>แนบภาพต้นฉบับทุกใบ · ใช้หน้าแชทนี้</p><small>ไม่ใช้ API key · โควตาตามบัญชี Gemini</small><label><input type="checkbox" id="skip" checked> ข้าม 5 ใบที่มีภาพแล้ว</label><label>จำนวนรอบนี้ <input type="number" id="count" min="1" max="78" value="1"> ใบ · เว้น <input type="number" id="gap" min="5" max="600" value="15"> วินาที</label><label>เริ่มที่ <select id="first"><option value="">ใบถัดไปที่ยังไม่ทำ</option></select></label><div class="row"><button id="prepare">เตรียมใบถัดไป</button><button id="start">เริ่มอัตโนมัติ</button><button id="pause" disabled>พักหลังใบนี้</button></div><div class="row" style="margin-top:8px"><button id="bind">เลือกช่องพิมพ์</button><button id="clear-unsent">ยังไม่ได้ส่ง — ปลดใบค้าง</button></div><div id="status" role="status" aria-live="polite">กำลังเตรียมคิว…</div><p id="recovery-hint" role="note"></p><div class="row"><button id="save-pending">บันทึกภาพใบค้าง</button><button id="show-download">เปิดตำแหน่งไฟล์</button><button id="reconcile">ยืนยันใบค้าง</button><button id="export">บันทึกสถานะ</button></div><p id="save-location" style="font-size:11px;overflow-wrap:anywhere"></p><details><summary>สถานะคิว / วินิจฉัย</summary><p id="summary"></p><pre id="log"></pre><button id="diagnose">ตรวจองค์ประกอบหน้า</button><p id="diagnostic"></p></details><small>เริ่มทดสอบ 1 ใบก่อน แล้วเพิ่มจำนวนรอบถัดไปได้</small></div></section>`;
 const $=id=>ui.getElementById(id);
 for(const c of DECK){const o=document.createElement('option');o.value=c.id;o.textContent=c.sequence+' · '+c.name;$('first').append(o);}
 const storage={load:async()=>{const data=await chrome.storage.local.get(KEY);return data[KEY];},save:async()=>chrome.storage.local.set({[KEY]:state})};
 const message=async data=>{const r=await chrome.runtime.sendMessage(data);if(r?.ok===false)throw Error(r.error);return r;};
 function log(text){$('status').textContent=text;state.events.push({time:new Date().toISOString(),text});state.events=state.events.slice(-40);$('log').textContent=state.events.map(e=>e.time.slice(11,19)+' '+e.text).join('\n');render();}
 const stageNames={preparing:'แนบภาพหรือใส่ข้อความ (ยังไม่กดส่งอัตโนมัติ)',prepared:'เตรียมข้อความแล้ว (ยังไม่กดส่งอัตโนมัติ)',submitting:'กดส่งแล้ว รอยืนยัน',submitted:'ส่งแล้ว รอภาพ',generated:'มีภาพแล้ว รอดาวน์โหลด',downloading:'กำลังดาวน์โหลด',review:'รอตรวจ'};
 function unresolved(){return queue().find(c=>state.cards[c.id]&&!['pending','downloaded'].includes(state.cards[c.id].status));}
 function render(){const values=Object.values(state.cards);const card=unresolved(),entry=card&&state.cards[card.id];
  $('recovery-hint').textContent=!running&&card?('ใบที่ต้องตรวจ: '+card.name+' · '+(stageNames[entry.status]||entry.status)+' — '+(entry.firstError||entry.error||'ยังไม่ได้ยืนยันว่าบันทึกภาพแล้ว')+' · กด “ยืนยันใบค้าง”; ใช้ UNSENT เฉพาะตรวจแล้วว่าไม่เคยส่ง หรือ SAVED เมื่อดาวน์โหลดแล้ว'):'';
const last=values.filter(v=>v.filename&&v.status==='downloaded').sort((a,b)=>String(b.updated).localeCompare(String(a.updated)))[0];$('save-location').textContent=last?'บันทึกล่าสุด: '+last.filename:'ยังไม่มีภาพที่บันทึกอัตโนมัติสำเร็จ';
$('summary').textContent=`สำเร็จ ${values.filter(v=>v.status==='downloaded').length} · รอตรวจ ${values.filter(v=>!['pending','downloaded'].includes(v.status)).length} · คิวทั้งหมด 78`;for(const id of ['start','prepare','skip','first','count','gap','reconcile','bind','clear-unsent','save-pending'])$(id).disabled=running;$('pause').disabled=!running;}
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
 function inspectBlockers(root){
  const alerts=allVisible('[role="alert"],[role="dialog"]');const content=[root?.innerText||'',...alerts.map(e=>e.innerText)].join('\n');
  if(quota.test(content))throw Error('หยุด: Gemini แจ้งโควตา/ขีดจำกัด กรุณารอแล้วตรวจบัญชี ไม่ส่งซ้ำ');
  if(/verify (?:you are|that you are) human|ยืนยันว่าคุณเป็นมนุษย์|unusual traffic/i.test(content))throw Error('หยุด: ให้เจ้าของจัดการการยืนยันตัวตนในหน้าเว็บก่อน');
 }
 async function waitFor(fn,timeout,description){const until=Date.now()+timeout;while(Date.now()<until){assertTarget();const result=await fn();if(result)return result;await delay(350);}throw Error(description);}
 const attachmentImages=root=>queryAll('img',root).filter(img=>visible(img)&&/^(?:blob:|data:image)|googleusercontent/.test(img.currentSrc||img.src)&&!/(?:avatar|profile)/i.test(img.alt||''));
 async function attach(e){
  let box=composer(e);if(!box)throw Error('หาบริเวณแนบไฟล์ไม่พบ กดเลือกช่องพิมพ์ก่อน');
  if(attachmentImages(box).length||/IMG_5392\.JPG/i.test((box.innerText||'').replace(text(e),'')))throw Error('มีไฟล์แนบค้างอยู่ กรุณาจัดการในช่องพิมพ์ก่อนเริ่ม');
  const before=new Set(queryAll('img',box).map(i=>i.currentSrc||i.src));
  if(!reference){const r=await fetch(chrome.runtime.getURL('assets/IMG_5392.JPG'));if(!r.ok)throw Error('โหลดภาพต้นฉบับในextensionไม่สำเร็จ');reference=await r.blob();}
  const view=e.ownerDocument.defaultView;
  const file=new view.File([reference],'IMG_5392.JPG',{type:'image/jpeg'});const transfer=new view.DataTransfer();transfer.items.add(file);
  const ready=()=>{box=composer(e);return !queryAll('[role=progressbar],mat-progress-spinner',box).length&&(/IMG_5392\.JPG/i.test(box.innerText||'')||attachmentImages(box).some(i=>!before.has(i.currentSrc||i.src)));};
  const findInput=()=>queryAll('input[type=file]').find(i=>!i.accept||/image|\.jpg|\.jpeg|\*/i.test(i.accept));
  let input=findInput();
  if(!input){
   // Gemini may not create a file input until the + menu opens. First use its image-paste handler.
   e.focus();const event=new view.ClipboardEvent('paste',{bubbles:true,cancelable:true,composed:true,clipboardData:transfer});const accepted=!e.dispatchEvent(event);
   const until=Date.now()+1800;while(Date.now()<until){if(ready())return;await delay(150);}
   if(accepted||queryAll('[role=progressbar],mat-progress-spinner',box).length){await waitFor(ready,30000,'วางภาพแล้วแต่ยังไม่เห็นภาพแนบพร้อมส่ง จึงพักคิว');return;}
   const buttons=allVisible('button',box).filter(uploadButton);
   if(buttons.length!==1)throw Error('ไม่พบปุ่ม + แนบไฟล์ในบริเวณช่องพิมพ์ กรุณากด + เปิดเมนูไว้แล้วลองเตรียมอีกครั้ง');
   log('เปิดเมนู + เพื่อแนบ JPG ต้นฉบับ');buttons[0].click();await delay(400);input=findInput();
   if(!input){const items=allVisible('[role=menuitem],button').filter(b=>/upload files|upload from computer|อัปโหลดไฟล์|อัปโหลดจากคอมพิวเตอร์/i.test(label(b)));if(items.length!==1)throw Error('กรุณาเลือก Upload files ในเมนู + ก่อน ยังไม่ส่งข้อความ');items[0].click();await delay(400);input=findInput();}
  }
  if(!input)throw Error('ยังไม่พบช่องอัปโหลด กรุณาเปิด + → Upload files แล้วลองเตรียมใหม่');
  input.files=transfer.files;input.dispatchEvent(new view.Event('input',{bubbles:true,composed:true}));input.dispatchEvent(new view.Event('change',{bubbles:true,composed:true}));
  await waitFor(ready,30000,'ไม่เห็นภาพแนบในช่องพิมพ์ จึงหยุดก่อนส่ง');
 }

 function fill(e,prompt){
  e.focus();
  if(e.tagName==='TEXTAREA'){Object.getOwnPropertyDescriptor(e.ownerDocument.defaultView.HTMLTextAreaElement.prototype,'value').set.call(e,prompt);e.dispatchEvent(new Event('input',{bubbles:true}));}
  else{const doc=e.ownerDocument,selection=doc.getSelection(),range=doc.createRange();range.selectNodeContents(e);selection.removeAllRanges();selection.addRange(range);if(!doc.execCommand('insertText',false,prompt)){e.textContent=prompt;e.dispatchEvent(new InputEvent('input',{bubbles:true,inputType:'insertText',data:prompt}));}}
  if(!text(e).includes('CARD SCENE: '+DECK.find(c=>c.prompt===prompt)?.name.toUpperCase()))throw Error('ตรวจข้อความในช่องพิมพ์ไม่ผ่าน จึงยังไม่ส่ง');
 }
 function sendButton(){
  const e=editor(),box=composer(e);
  const isSend=b=>!b.disabled&&(b.matches('.send-button,[data-testid="send-button"]')||/^send(?: message| prompt)?$|^submit$|^ส่ง(?:ข้อความ|พรอมต์)?$/i.test(label(b))||Array.from(b.querySelectorAll('mat-icon,.material-icons,.material-symbols-outlined')).some(i=>/^(?:send|arrow_upward)$/.test(i.textContent.trim())));
  let list=allVisible('button',box).filter(isSend);if(!list.length)list=allVisible('button').filter(isSend);
  if(list.length!==1)throw Error('หาปุ่มส่งที่ชัดเจนไม่พบ จึงยังไม่ส่ง');return list[0];
 }

 function queue(){const first=$('first').value,start=first?DECK.findIndex(c=>c.id===first):0;return DECK.slice(start).filter(c=>(!$('skip').checked||!c.existing_generated_image)&&state.cards[c.id]?.status!=='downloaded');}
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
  if(url.startsWith('blob:')||url.startsWith('data:'))d=await message({type:'mmkt:download-data',cardId:card.id,dataUrl:await imageData(url)});
  else d=await message({type:'mmkt:download',cardId:card.id,url});
  await record(card,'downloading',{downloadId:d.downloadId});
  const result=await waitFor(async()=>{const r=await message({type:'mmkt:download-status',downloadId:d.downloadId});if(['interrupted','invalid','missing'].includes(r.state))throw Error('ดาวน์โหลดไม่สำเร็จ: '+(r.error||r.state)+' — ไม่ส่งพรอมต์นี้ซ้ำ');return r.state==='complete'?r:null;},120000,'ยังยืนยันดาวน์โหลดไม่สำเร็จ จึงพักคิว ไม่เจนซ้ำ');
  await record(card,'downloaded',{filename:result.filename,error:null,firstError:null});log('บันทึกแล้ว: '+card.name);
 }
 function existingImage(card){
  const entry=state.cards[card.id]||{},responses=responseRoots();
  if(entry.imageUrl){const exact=responses.flatMap(generatedImages).filter(img=>(img.currentSrc||img.src)===entry.imageUrl);if(exact.length===1)return exact[0];}
  // Resolve a renewed blob URL only when the associated user query identifies this card.
  for(const root of responses){const container=root.closest('conversation-container,[data-message-pair]');const queries=container?queryAll('user-query',container):[];if(queries.some(q=>(q.innerText||q.textContent||'').toUpperCase().includes('CARD SCENE: '+card.name.toUpperCase()))){const images=generatedImages(root);if(images.length===1)return images[0];}}
  const query=queryRoots().at(-1),last=responses.at(-1);
  if(Number.isInteger(entry.baseline)&&responses.length===entry.baseline+1&&query&&(query.innerText||query.textContent||'').toUpperCase().includes('CARD SCENE: '+card.name.toUpperCase())){const images=generatedImages(last);if(images.length===1)return images[0];}
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
  await record(card,'preparing',{baseline:responseRoots().length});log('แนบภาพต้นฉบับ: '+card.name);
  await attach(e);fill(e,card.prompt);await record(card,'prepared');
  if(!submit){log('เตรียม '+card.name+' พร้อมภาพแล้ว — คุณตรวจและกดส่งเองได้');return;}
  const button=await waitFor(()=>{try{return sendButton();}catch{return false;}},30000,'ปุ่มส่งยังไม่พร้อม จึงพักคิว');
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
   const jobs=queue().slice(0,submit?count:1);if(!jobs.length){log('คิวที่เลือกทำครบแล้ว');return;}
   for(let i=0;i<jobs.length;i++){card=jobs[i];await prepare(card,submit);if(!submit||pause)break;if(i<jobs.length-1){log('พัก '+gap+' วินาทีก่อนใบถัดไป');for(let j=0;j<gap*2&&!pause;j++){assertTarget();await delay(500);}if(pause)break;}}
   if(submit)log(pause?'พักคิวแล้ว เริ่มต่อได้':'จบรอบแล้ว ตรวจภาพก่อนเริ่มรอบถัดไป');
  }catch(e){if(card){const current=state.cards[card.id]||{};if(!e.message.startsWith('มีใบค้าง '))await record(card,current.status||'review',{error:e.message,firstError:current.firstError||e.message});}log(e.message);}
  finally{running=false;if(locked)try{await message({type:'mmkt:unlock'});}catch{}await storage.save();render();}
 }
 $('start').onclick=()=>run(true);$('prepare').onclick=()=>run(false);$('pause').onclick=()=>{pause=true;log('จะพักเมื่อจบใบปัจจุบัน โดยไม่ส่งใบถัดไป');};
 $('fold').onclick=()=>{$('body').classList.toggle('hidden');$('fold').textContent=$('body').classList.contains('hidden')?'+':'−';};
 $('export').onclick=()=>{const blob=new Blob([JSON.stringify({chatId:CHAT,...state},null,2)],{type:'application/json'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='maemorkratai-gemini-progress.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),5000);};
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
 storage.load().then(saved=>{if(saved?.cards)state=saved;log(target()?'พร้อม · เริ่มที่ 1 ใบเพื่อทดสอบ':'เปิดแชทแม่หมอกระต่ายที่กำหนดก่อนเริ่ม');});
 globalThis.MMKT_RUNNER={SELECTORS,generatedImages,queue,target,editorCandidates};
})();
