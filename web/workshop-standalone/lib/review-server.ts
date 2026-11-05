import 'server-only';
import {createHash} from 'node:crypto';
import {adminClient} from './supabase-server';
import {Problem} from './domain';
import {REVIEW_BUCKET,type ReviewState} from './review-domain';
import {databaseError,cases} from './workshop-server';
export type ReviewSource={id:string;sourceHash:string;sourceRevision?:number;caseVersion?:string;baseline?:{originalText:string;machineTranscript:string;reviewText:string;sourceType:string;notes:Record<string,string>;audioId:string|null};followup?:ReviewSource['baseline'];observations?:{id:string;observation:string;question:string;sources:string[]}[]};
const bucket=()=>adminClient().storage.from(REVIEW_BUCKET);
export async function document<T>(path:string):Promise<T>{const r=await bucket().download(path);if(r.error||!r.data)throw new Problem(503,'ยังเปิดชุดตรวจไม่ได้ กรุณาลองใหม่');return JSON.parse(await r.data.text())}
export async function manifest(owner:string){return document<{items:{id:string;title:string;category:string;sourceHash:string}[]}>(owner+'/manifest.json')}
export async function source(owner:string,id:string){
 const m=await manifest(owner);if(!m.items.some(x=>x.id===id))throw new Problem(404,'ไม่พบเคสในชุดพัฒนา');
 const s=await document<ReviewSource>(owner+'/'+id+'/source.json');
 const {sourceHash,...payload}=s;
 if(createHash('sha256').update(JSON.stringify(payload)).digest('hex')!==sourceHash||m.items.find(x=>x.id===id)?.sourceHash!==sourceHash)throw new Problem(409,'ต้นทางชุดตรวจเปลี่ยน กรุณาติดต่อผู้ดูแล');
 if(id!=='style'){
  const c=cases.find(c=>c.id===id);if(!c||c.split!=='development'||c.version!==s.caseVersion)throw new Problem(409,'เคสนี้ไม่อยู่ในชุดพัฒนารุ่นปัจจุบัน');
  const r=await adminClient().from('workshop_readings').select('revision').eq('reader_id',owner).eq('case_id',id).maybeSingle();databaseError(r.error);
  if(r.data?.revision!==s.sourceRevision)throw new Problem(409,'คำอ่านต้นฉบับเปลี่ยน ต้องเตรียมชุดตรวจใหม่ก่อน');
 }
 return s;
}
export async function history(owner:string,id:string){const r=await bucket().list(owner+'/'+id+'/revisions',{limit:100,sortBy:{column:'name',order:'desc'}});if(r.error)throw new Problem(503,'โหลดประวัติไม่ได้');return (r.data||[]).filter(x=>/^\d{8}\.json$/.test(x.name)).map(x=>x.name)}
export async function latest(owner:string,id:string):Promise<ReviewState|null>{const names=await history(owner,id);return names.length?document<ReviewState>(owner+'/'+id+'/revisions/'+names[0]):null}
export async function append(owner:string,id:string,state:ReviewState){
 const r=await bucket().upload(owner+'/'+id+'/revisions/'+String(state.revision).padStart(8,'0')+'.json',JSON.stringify(state),{contentType:'application/json',upsert:false});
 if(r.error){if(String(r.error.statusCode)==='409'||/already exists|duplicate/i.test(r.error.message))throw new Problem(409,'มีการบันทึกจากอีกหน้าต่างแล้ว กรุณาโหลดใหม่ก่อน');throw new Problem(503,'บันทึกไม่สำเร็จ ร่างในหน้านี้ยังอยู่ กรุณาลองอีกครั้ง')}
}
