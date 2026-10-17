'use strict';
const CHAT = 'c1051ca2e5090320';
const validSender = sender => {try {const u=new URL(sender.url);return u.origin==='https://gemini.google.com'&&u.pathname.split('/').includes(CHAT)&&Number.isInteger(sender.tab?.id);} catch{return false;}};
async function handle(message,sender){
 if(!validSender(sender))throw Error('เปิดแชทแม่หมอกระต่ายที่ระบุก่อน');
 const tabId=sender.tab.id;
 if(message.type==='mmkt:lock'){
  const {mmktLock:lock}=await chrome.storage.local.get('mmktLock');
  if(lock&&lock.tabId!==tabId){let exists=false;try{await chrome.tabs.get(lock.tabId);exists=true;}catch{}if(exists)throw Error('มีแท็บอื่นกำลังทำงานอยู่ ให้พักแท็บนั้นก่อน');}
  await chrome.storage.local.set({mmktLock:{tabId}});return {ok:true};
 }
 if(message.type==='mmkt:unlock'){
  const {mmktLock:lock}=await chrome.storage.local.get('mmktLock');if(lock?.tabId===tabId)await chrome.storage.local.remove('mmktLock');return {ok:true};
 }
 if(message.type==='mmkt:download'||message.type==='mmkt:download-data'){
  if(!/^[a-z0-9-]+$/.test(message.cardId))throw Error('ชื่อไพ่ไม่ถูกต้อง');
  if(message.variant&&!['original','title-v1','repair-v1'].includes(message.variant))throw Error('รุ่นภาพไม่ถูกต้อง');
  const folder=message.variant==='repair-v1'?'cards-repaired/v1/':message.variant==='title-v1'?'cards-titled/v1/':'cards/';
  let url,extension='png';
  if(message.type==='mmkt:download-data'){
   const match=/^data:(image\/(png|jpeg|webp|gif|avif));base64,([A-Za-z0-9+/]+={0,2})$/.exec(message.dataUrl||'');
   if(!match||message.dataUrl.length>33554432)throw Error('ข้อมูลภาพไม่ถูกต้องหรือใหญ่เกิน32MB');
   const bytes=atob(match[3].slice(0,Math.min(64,match[3].length)));
   const signature=bytes.startsWith('\x89PNG\r\n\x1a\n')?'png':bytes.startsWith('\xff\xd8\xff')?'jpeg':bytes.startsWith('RIFF')&&bytes.slice(8,12)==='WEBP'?'webp':/^GIF8[79]a/.test(bytes)?'gif':bytes.slice(4,8)==='ftyp'&&/avif|avis/.test(bytes.slice(8,32))?'avif':null;
   if(signature!==match[2])throw Error('ชนิดข้อมูลภาพไม่ตรงกับไฟล์จริง');
   url=message.dataUrl;extension=signature==='jpeg'?'jpg':signature;
  }else{
   const u=new URL(message.url);
   if(u.protocol!=='https:'||!(u.hostname==='gemini.google.com'||u.hostname.endsWith('.googleusercontent.com')))throw Error('ต้องอ่านข้อมูลภาพจากหน้าGeminiก่อนดาวน์โหลด');
   url=u.href;
  }
  const id=await chrome.downloads.download({url,filename:'MaeMorKratai/'+folder+message.cardId+'.'+extension,saveAs:false,conflictAction:'uniquify'});
  const {mmktDownloads:downloads={}}=await chrome.storage.local.get('mmktDownloads');downloads[id]={tabId,cardId:message.cardId};await chrome.storage.local.set({mmktDownloads:downloads});
  return {ok:true,downloadId:id};
 }
 if(message.type==='mmkt:show-download'){
  const {mmktDownloads:downloads={}}=await chrome.storage.local.get('mmktDownloads');
  const ids=Object.keys(downloads).map(Number).sort((a,b)=>b-a);
  for(const id of ids){const [item]=await chrome.downloads.search({id});if(item?.state==='complete'&&item.mime?.startsWith('image/')){await chrome.downloads.show(id);return {ok:true,filename:item.filename,found:true};}}
  await chrome.downloads.showDefaultFolder();return {ok:true,found:false};
 }
 if(message.type==='mmkt:download-status'){
  if(!Number.isInteger(message.downloadId))throw Error('ไม่มีรหัสดาวน์โหลด');
  const {mmktDownloads:downloads={}}=await chrome.storage.local.get('mmktDownloads');if(downloads[message.downloadId]?.tabId!==tabId)throw Error('ไม่ใช่งานดาวน์โหลดของแท็บนี้');
  const [item]=await chrome.downloads.search({id:message.downloadId});
  if(!item)return {state:'missing'};
  if(item.mime&&!item.mime.startsWith('image/'))return {state:'invalid',error:'ไฟล์ที่ได้ไม่ใช่ภาพ กรุณาดาวน์โหลดจากGeminiเอง'};
  return {state:item.state,error:item.error||null,mime:item.mime||null,filename:item.filename};
 }
 throw Error('คำสั่งไม่รองรับ');
}
let serial=Promise.resolve();
chrome.runtime.onMessage.addListener((message,sender,reply)=>{
 if(!message?.type?.startsWith('mmkt:'))return;
 // Serialize lock claims so two tabs cannot claim an empty lock simultaneously.
 const task=serial.then(()=>handle(message,sender));serial=task.catch(()=>{});
 task.then(reply,error=>reply({ok:false,error:error.message}));return true;
});
chrome.tabs.onRemoved.addListener(async tabId=>{const {mmktLock:lock}=await chrome.storage.local.get('mmktLock');if(lock?.tabId===tabId)await chrome.storage.local.remove('mmktLock');});
