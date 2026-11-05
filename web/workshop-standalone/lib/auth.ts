import 'server-only';
import {serverClient} from './supabase-server';
import {Problem} from './domain';
import {sameOrigin} from './origin';
export type Member={user_id:string;role:'owner'|'reader';display_name:string;active:boolean};
export async function authorize(request?:Request,write=false){
  if(write&&request){
    if(!sameOrigin(request))throw new Problem(403,'กรุณาบันทึกจากหน้าห้องทดลอง');
  }
  const supabase=await serverClient();
  const {data:{user},error}=await supabase.auth.getUser();
  if(error||!user)throw new Problem(401,'กรุณาเข้าสู่ระบบก่อน');
  const {data:member,error:memberError}=await supabase.from('workshop_members').select('*').eq('user_id',user.id).maybeSingle();
  if(memberError)throw new Problem(503,'ยังตรวจสิทธิ์ไม่ได้ กรุณาลองใหม่');
  if(!member?.active)throw new Problem(403,'บัญชีนี้ยังไม่มีสิทธิ์ หรือได้ถอนความยินยอมแล้ว');
  return {supabase,user,member:member as Member};
}
export function readerFor(req:Request,member:Member){
  const target=new URL(req.url).searchParams.get('reader')||member.user_id;
  if(target!==member.user_id&&member.role!=='owner')throw new Problem(403,'ไม่มีสิทธิ์ดูคำอ่านนี้');
  if(!/^[a-f0-9-]{36}$/i.test(target))throw new Problem(400,'ข้อมูลผู้บันทึกไม่ถูกต้อง');
  return target;
}
