import 'server-only';
import {adminClient} from './supabase-server';
import {BUCKET} from './config';
import {audioType,Problem} from './domain';
import {databaseError} from './workshop-server';
export type AudioRecord={id:string;reader_id:string;case_id:string;stage:string;object_key:string;mime:string;bytes:number;duration:number;status:string;created_at:string};
export async function verifyAndComplete(row:AudioRecord){
 if(row.status==='ready')return;
 const admin=adminClient();
 const {data,error}=await admin.storage.from(BUCKET).createSignedUrl(row.object_key,60);
 if(error||!data)throw new Problem(400,'ยังไม่พบไฟล์เสียง กรุณาลองอัปโหลดอีกครั้ง');
 const head=await fetch(data.signedUrl,{method:'HEAD',cache:'no-store',signal:AbortSignal.timeout(15000)});
 if(!head.ok||Number(head.headers.get('content-length'))!==row.bytes)throw new Problem(400,'ขนาดไฟล์เสียงไม่ตรงกับที่บันทึก');
 const response=await fetch(data.signedUrl,{headers:{Range:'bytes=0-31'},cache:'no-store',signal:AbortSignal.timeout(15000)});
 if(!response.ok||!response.body)throw new Problem(400,'ตรวจไฟล์เสียงไม่ได้');
 const stream=response.body.getReader(),prefix=new Uint8Array(32);let at=0;
 try{while(at<32){const {done,value}=await stream.read();if(done)break;const part=value.subarray(0,32-at);prefix.set(part,at);at+=part.length}}finally{await stream.cancel()}
 if(at<32||audioType(prefix)!==row.mime)throw new Problem(400,'รูปแบบไฟล์เสียงไม่ถูกต้อง กรุณาอัดใหม่');
 const result=await admin.rpc('workshop_complete_audio',{p_id:row.id,p_reader:row.reader_id});
 databaseError(result.error);
}
