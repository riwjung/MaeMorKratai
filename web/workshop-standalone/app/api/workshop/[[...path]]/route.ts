import {authorize,readerFor} from '../../../../lib/auth';
import {adminClient} from '../../../../lib/supabase-server';
import {cases,decode,scenario,detail,databaseError,readJson,isUuid} from '../../../../lib/workshop-server';
import {Problem,parseAnswers} from '../../../../lib/domain';
import {verifyAndComplete,type AudioRecord} from '../../../../lib/audio-server';
import {BUCKET} from '../../../../lib/config';
export const dynamic='force-dynamic';
export const runtime='nodejs';
const json=(body:unknown,status=200)=>Response.json(body,{status,headers:{'Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff'}});
function fail(e:unknown){if(e instanceof Problem)return json({error:e.message},e.status);console.error('workshop request failed',e instanceof Error?e.name:'unknown');return json({error:'เชื่อมต่อไม่สำเร็จ กรุณาลองอีกครั้ง ข้อมูลในหน้านี้ยังอยู่'},500)}
const pathOf=(r:Request)=>new URL(r.url).pathname.replace(/^\/api\/workshop\/?/,'').split('/').filter(Boolean);
export async function GET(req:Request){try{
 const {supabase,member}=await authorize(req),p=pathOf(req),reader=readerFor(req,member);
 if(reader!==member.user_id){
  const target=await supabase.from('workshop_members').select('user_id').eq('user_id',reader).eq('active',true).maybeSingle();
  databaseError(target.error);if(!target.data)throw new Problem(404,'ไม่พบผู้บันทึก');
 }
 if(!p.length){
  const r=await supabase.from('workshop_readings').select('*').eq('reader_id',reader);databaseError(r.error);
  return json({cases:cases.map(c=>{const s=decode(r.data?.find(r=>r.case_id===c.id)||null);return {id:c.id,number:c.number,title:c.title,category:c.category,situation:c.situation,stage:s.stage,revision:s.revision}})});
 }
 if(p[0]==='members'&&p.length===1){
  if(member.role!=='owner')throw new Problem(403,'เฉพาะเจ้าของห้อง');
  const r=await supabase.from('workshop_members').select('user_id,display_name,role,active').order('display_name');databaseError(r.error);
  const w=await supabase.from('workshop_withdrawals').select('reader_id,requested_at,completed_at').is('completed_at',null);databaseError(w.error);
  return json({members:r.data,withdrawals:w.data});
 }
 if(p[0]==='cases'&&p.length===2)return json(await detail(supabase,p[1],reader));
 if(p[0]==='audio'&&p.length===2){
  if(!isUuid(p[1]))throw new Problem(404,'ไม่พบเสียง');
  const r=await supabase.from('workshop_recordings').select('*').eq('id',p[1]).eq('status','ready').maybeSingle();databaseError(r.error);
  if(!r.data)throw new Problem(404,'ไม่พบเสียง');
  const download=new URL(req.url).searchParams.has('download');
  const extension=r.data.mime==='audio/mp4'?'m4a':r.data.mime.split('/')[1];
  const signed=await adminClient().storage.from(BUCKET).createSignedUrl(r.data.object_key,900,download?{download:`reading-${r.data.id}.${extension}`}:{});
  if(signed.error||!signed.data)throw new Problem(503,'เปิดไฟล์เสียงไม่สำเร็จ');
  return new Response(null,{status:302,headers:{Location:signed.data.signedUrl,'Cache-Control':'private, no-store'}});
 }
 if(p[0]==='export'&&p.length===1){
  if(member.role!=='owner')throw new Problem(403,'เฉพาะเจ้าของห้อง');
  const url=new URL(req.url),table=url.searchParams.get('table')||'readings',offset=Number(url.searchParams.get('offset')||0);
  if(!['readings','responses','recordings'].includes(table)||!Number.isSafeInteger(offset)||offset<0)throw new Problem(400,'ตัวเลือกส่งออกไม่ถูกต้อง');
  // Five snapshots keep each response below Vercel's payload limit.
  let q=supabase.from('workshop_'+table).select('*').eq('reader_id',reader);
  if(table==='recordings')q=q.eq('status','ready');
  const result=await q.order(table==='readings'?'case_id':'id').range(offset,offset+4);databaseError(result.error);
  return json({format:'maemorkratai-workshop-v2',table,reader,data:result.data,next:result.data?.length===5?offset+5:null});
 }
 throw new Problem(404,'ไม่พบข้อมูล');
 }catch(e){return fail(e)}}

export async function POST(req:Request){try{
 const {supabase,member}=await authorize(req,true),p=pathOf(req),input=await readJson(req);
 if(p[0]==='cases'&&p.length===2){
  scenario(p[1]);
  if(!isUuid(input.requestId)||!Number.isSafeInteger(input.revision))throw new Problem(400,'คำขอไม่ถูกต้อง');
  const answers=parseAnswers(input.answers);
  const result=await supabase.rpc('workshop_save',{p_case:p[1],p_request:input.requestId,p_revision:input.revision,p_stage:input.stage,p_action:input.action,p_answers:answers,p_consent:input.consent===true});
  databaseError(result.error);
  return json(await detail(supabase,p[1],member.user_id));
 }
 if(p[0]==='audio'&&p[1]==='reserve'&&p.length===2){
  if(!isUuid(input.id)||typeof input.caseId!=='string'||input.consent!==true)throw new Problem(400,'ข้อมูลเสียงไม่ถูกต้อง');
  scenario(input.caseId);
  if(!Number.isSafeInteger(input.bytes)||!Number.isSafeInteger(input.duration)||typeof input.mime!=='string'||!['audio/webm','audio/mp4','audio/ogg','audio/wav'].includes(input.mime))throw new Problem(400,'ข้อมูลเสียงไม่ถูกต้อง');
  const r=await supabase.rpc('workshop_reserve_audio',{p_id:input.id,p_case:input.caseId,p_stage:input.stage,p_mime:input.mime,p_bytes:input.bytes,p_duration:input.duration});databaseError(r.error);
  const row=(Array.isArray(r.data)?r.data[0]:r.data) as AudioRecord;
  if(row.status==='ready')return json({id:row.id,ready:true});
  // A retry after upload succeeded can finish without trying to overwrite it.
  try{await verifyAndComplete(row);return json({id:row.id,ready:true})}catch(e){if(!(e instanceof Problem&&e.status===400))throw e}
  const signed=await adminClient().storage.from(BUCKET).createSignedUploadUrl(row.object_key,{upsert:false});
  if(signed.error||!signed.data)throw new Problem(503,'เตรียมพื้นที่เสียงไม่สำเร็จ');
  return json({id:row.id,ready:false,path:row.object_key,token:signed.data.token,bucket:BUCKET});
 }
 if(p[0]==='audio'&&p[1]==='complete'&&p.length===2){
  if(!isUuid(input.id))throw new Problem(400,'ข้อมูลเสียงไม่ถูกต้อง');
  const row=await supabase.from('workshop_recordings').select('*').eq('id',input.id).eq('reader_id',member.user_id).maybeSingle();databaseError(row.error);
  if(!row.data)throw new Problem(404,'ไม่พบเสียง');
  await verifyAndComplete(row.data);return json({id:input.id});
 }
 if(p[0]==='withdraw'&&p.length===1){
  if(input.confirm!=='WITHDRAW')throw new Problem(400,'กรุณายืนยันคำขอ');
  const result=await supabase.rpc('workshop_withdraw');databaseError(result.error);
  await supabase.auth.signOut();
  return json({ok:true});
 }
 throw new Problem(404,'ไม่พบคำสั่ง');
 }catch(e){return fail(e)}}
