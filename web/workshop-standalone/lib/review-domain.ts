import {Problem} from './domain';
export const REVIEW_BUCKET='workshop-review';
export type ReviewContent={baseline:string;followup:string;notes:string;style:Record<string,string>};
export type ReviewState={revision:number;requestId:string;sourceHash:string;status:'draft'|'approved'|'needs_changes';content:ReviewContent;reviewedBy:string;updatedAt:string};
export function parseReview(v:Record<string,unknown>,styleIds:string[]=[]){
 if(!Number.isSafeInteger(v.revision)||(v.revision as number)<0||!['draft','approved','needs_changes'].includes(String(v.status))||typeof v.requestId!=='string'||! /^[0-9a-f-]{36}$/i.test(v.requestId)||typeof v.sourceHash!=='string')throw new Problem(400,'ข้อมูลการตรวจไม่ถูกต้อง');
 const c=v.content as ReviewContent;
 if(!c||typeof c!=='object'||Array.isArray(c))throw new Problem(400,'ไม่มีคำอ่านฉบับตรวจ');
 for(const field of ['baseline','followup','notes'] as const)if(typeof c[field]!=='string'||c[field].length>16000)throw new Problem(400,'ข้อความยาวเกินไปหรือไม่ถูกต้อง');
 if(!c.style||typeof c.style!=='object'||Array.isArray(c.style)||Object.keys(c.style).some(k=>!styleIds.includes(k))||Object.values(c.style).some(x=>typeof x!=='string'||x.length>4000))throw new Problem(400,'ความเห็นสำนวนไม่ถูกต้อง');
 if(v.status==='approved'){
  if(v.confirm!==true)throw new Problem(400,'กรุณายืนยันว่าได้ตรวจฉบับนี้แล้ว');
  if(styleIds.length?styleIds.some(id=>!c.style[id]?.trim()):(!c.baseline.trim()||!c.followup.trim()))throw new Problem(400,styleIds.length?'กรุณาระบุสำนวนที่ต้องการให้ครบทุกข้อ':'กรุณาตรวจคำอ่านทั้งก่อนและหลังใบขยาย');
 }
 return {revision:v.revision as number,requestId:v.requestId,sourceHash:v.sourceHash,status:v.status as ReviewState['status'],content:{baseline:c.baseline,followup:c.followup,notes:c.notes,style:c.style}};
}
