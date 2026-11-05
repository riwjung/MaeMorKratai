import {authorize} from '../../../lib/auth';
import {Problem} from '../../../lib/domain';
import {readJson,cases} from '../../../lib/workshop-server';
import cards from '../../../lib/cards.json';
import {manifest,source,latest,history,document,append} from '../../../lib/review-server';
import {parseReview,type ReviewState} from '../../../lib/review-domain';
export const dynamic='force-dynamic';
export const runtime='nodejs';
const json=(v:unknown,status=200)=>Response.json(v,{status,headers:{'Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff'}});
function fail(e:unknown){return e instanceof Problem?json({error:e.message},e.status):json({error:'เชื่อมต่อไม่สำเร็จ กรุณาลองใหม่'},503)}
async function owner(req:Request,write=false){const a=await authorize(req,write);if(a.member.role!=='owner')throw new Problem(403,'เฉพาะแม่หมอเจ้าของห้อง');return a.member.user_id}
export async function GET(req:Request){try{
 const who=await owner(req),url=new URL(req.url),id=url.searchParams.get('id');
 if(!id){const m=await manifest(who);return json({items:await Promise.all(m.items.map(async x=>{const s=await latest(who,x.id);return {...x,status:s?.status||'pending',revision:s?.revision||0}}))})}
 const s=await source(who,id),rev=url.searchParams.get('revision');
 if(rev){if(!/^[1-9]\d{0,6}$/.test(rev))throw new Problem(400,'รุ่นไม่ถูกต้อง');const names=await history(who,id),name=String(Number(rev)).padStart(8,'0')+'.json';if(!names.includes(name))throw new Problem(404,'ไม่พบรุ่นนี้');return json({state:await document(who+'/'+id+'/revisions/'+name)})}
 const c=cases.find(c=>c.id===id);
 return json({source:s,scenario:c?{...c,cards:c.cards.map((id,i)=>({...cards.find(x=>x.id===id),position:['อดีต','ปัจจุบัน','อนาคต','ขยายอนาคต'][i]}))}:null,state:await latest(who,id),history:(await history(who,id)).map(n=>Number(n.slice(0,8)))});
 }catch(e){return fail(e)}}
export async function POST(req:Request){try{
 const who=await owner(req,true),v=await readJson(req);if(typeof v.id!=='string')throw new Problem(400,'ไม่พบเคส');
 const s=await source(who,v.id),input=parseReview(v,s.observations?.map(x=>x.id)),prev=await latest(who,v.id);
 if(input.sourceHash!==s.sourceHash)throw new Problem(409,'ชุดตรวจไม่ตรงกับต้นทาง กรุณาโหลดใหม่');
 if(prev?.requestId===input.requestId){if(prev.status!==input.status||JSON.stringify(prev.content)!==JSON.stringify(input.content))throw new Problem(409,'คำขอเดิมมีข้อมูลต่างกัน');return json({state:prev})}
 if((prev?.revision||0)!==input.revision)throw new Problem(409,'มีการบันทึกฉบับใหม่แล้ว กรุณาโหลดใหม่ก่อน ร่างในหน้านี้ยังอยู่');
 const state:ReviewState={...input,revision:input.revision+1,reviewedBy:who,updatedAt:new Date().toISOString()};await append(who,v.id,state);return json({state});
 }catch(e){return fail(e)}}
