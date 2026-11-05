import 'server-only';
import cases from './cases.json';
import cards from './cards.json';
import {emptySnapshot,Problem,visibleCards,type Snapshot} from './domain';
import type {SupabaseClient} from '@supabase/supabase-js';
export {cases};
export type Reading={reader_id:string;case_id:string;revision:number;stage:Snapshot['stage'];baseline:Snapshot['baseline'];followup:Snapshot['followup'];updated_at:string|null};
export function databaseError(error:{message:string;code?:string}|null){
 if(!error)return;
 const m=error.message;
 if(/CONFLICT|23505/.test(m)||error.code==='23505')throw new Problem(409,'มีการบันทึกหรือเปลี่ยนขั้นตอนแล้ว กรุณาโหลดเคสใหม่ก่อน');
 if(/FORBIDDEN|OWNER_WITHDRAW/.test(m))throw new Problem(403,'บัญชีนี้ทำรายการนี้ไม่ได้');
 if(/ANSWER_REQUIRED/.test(m))throw new Problem(400,'อัดเสียงหรือพิมพ์คำตอบก่อนดำเนินการ');
 if(/CONSENT/.test(m))throw new Problem(400,'กรุณายืนยันการเก็บคำตอบก่อนบันทึก');
 if(/AUDIO_NOT_READY/.test(m))throw new Problem(400,'เสียงยังอัปโหลดไม่ครบ กรุณาลองบันทึกอีกครั้ง');
 if(/INVALID/.test(m))throw new Problem(400,'ข้อมูลไม่ถูกต้อง กรุณาลองใหม่');
 if(/CASE_NOT_FOUND/.test(m))throw new Problem(404,'ไม่พบเคสนี้');
 throw new Problem(503,'เชื่อมต่อข้อมูลไม่สำเร็จ กรุณาลองอีกครั้ง');
}
export function scenario(id:string){const c=cases.find(c=>c.id===id);if(!c)throw new Problem(404,'ไม่พบเคสนี้');return c}
export function decode(r:Reading|null):Snapshot{return r?{revision:r.revision,stage:r.stage,baseline:r.baseline,followup:r.followup,updatedAt:r.updated_at}:emptySnapshot()}
export async function detail(c:SupabaseClient,id:string,reader:string){
 const sc=scenario(id);
 const [reading,audio]=await Promise.all([
  c.from('workshop_readings').select('*').eq('reader_id',reader).eq('case_id',id).maybeSingle(),
  c.from('workshop_recordings').select('id,stage,duration,mime,bytes,created_at').eq('reader_id',reader).eq('case_id',id).eq('status','ready').order('created_at',{ascending:false})
 ]);
 databaseError(reading.error);databaseError(audio.error);
 const s=decode(reading.data);
 return {...sc,cards:visibleCards(sc.cards,s).map((id,i)=>({...cards.find(c=>c.id===id)!,position:['อดีต','ปัจจุบัน','อนาคต','ขยายอนาคต'][i],orientation:'upright'})),snapshot:s,recordings:audio.data||[]};
}
export async function readJson(req:Request):Promise<Record<string,unknown>>{
 const reader=req.body?.getReader();if(!reader)throw new Problem(400,'ไม่มีข้อมูล');
 let bytes=0;const chunks:Uint8Array[]=[];
 while(true){const {done,value}=await reader.read();if(done)break;bytes+=value.length;if(bytes>150000){await reader.cancel();throw new Problem(413,'ข้อมูลยาวเกินไป')}chunks.push(value)}
 try{const v=JSON.parse(Buffer.concat(chunks).toString('utf8'));if(!v||typeof v!=='object'||Array.isArray(v))throw 0;return v}catch{throw new Problem(400,'ข้อมูลไม่ถูกต้อง')}
}
export const isUuid=(s:unknown):s is string=>typeof s==='string'&&/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(s);
