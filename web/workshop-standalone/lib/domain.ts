export const fields = ['answer','evidence','uncertainty','question','phrases','changes','unchanged'] as const;
export type Answers = Record<typeof fields[number], string> & {audioId: string | null};
export type Stage = 'baseline' | 'followup' | 'review';
export type Snapshot = {revision:number;stage:Stage;baseline:Answers;followup:Answers;updatedAt:string|null};
export const emptyAnswers = ():Answers => ({answer:'',evidence:'',uncertainty:'',question:'',phrases:'',changes:'',unchanged:'',audioId:null});
export const emptySnapshot = ():Snapshot => ({revision:0,stage:'baseline',baseline:emptyAnswers(),followup:emptyAnswers(),updatedAt:null});
export class Problem extends Error {constructor(public status:number,message:string){super(message)}}
export function parseAnswers(v:unknown):Answers {
 if(!v || typeof v!=='object') throw new Problem(400,'รูปแบบคำตอบไม่ถูกต้อง');
 const input=v as Record<string,unknown>;const out=emptyAnswers();
 for(const k of fields){if(typeof input[k]!=='string'||input[k].length>12000)throw new Problem(400,'ข้อความยาวเกินไปหรือรูปแบบไม่ถูกต้อง');out[k]=input[k].trim();}
 if(input.audioId!==null && (typeof input.audioId!=='string'|| !/^[\w-]{36}$/.test(input.audioId)))throw new Problem(400,'รหัสเสียงไม่ถูกต้อง');
 out.audioId=input.audioId as string|null;return out;
}
export function transition(current:Snapshot, input:{stage:string;action:string;answers:Answers}):Snapshot {
 if(current.stage==='review')throw new Problem(409,'เคสนี้ส่งทบทวนแล้ว ต้นฉบับถูกเก็บไว้');
 if(input.stage!==current.stage)throw new Problem(409,'ขั้นตอนเปลี่ยนแล้ว กรุณาโหลดเคสใหม่');
 if(!['save','seal','submit'].includes(input.action))throw new Problem(400,'คำสั่งไม่ถูกต้อง');
 if(input.action==='seal'&&input.stage!=='baseline'||input.action==='submit'&&input.stage!=='followup')throw new Problem(400,'คำสั่งไม่ตรงขั้นตอน');
 if(input.action!=='save'&&!input.answers.answer&&!input.answers.audioId)throw new Problem(400,'อัดเสียงหรือพิมพ์คำตอบก่อนดำเนินการ');
 return {...current,[current.stage]:input.answers,revision:current.revision+1,stage:input.action==='seal'?'followup':input.action==='submit'?'review':current.stage,updatedAt:new Date().toISOString()};
}
export function visibleCards<T>(cards:T[],snapshot:Snapshot){return cards.slice(0,snapshot.stage==='baseline'?3:4)}
export function audioType(bytes:Uint8Array):string|null {
 if(bytes.length<32)return null;
 const ascii=(a:number,b:number)=>String.fromCharCode(...bytes.slice(a,b));
 if(bytes[0]===0x1a&&bytes[1]===0x45&&bytes[2]===0xdf&&bytes[3]===0xa3)return 'audio/webm';
 if(ascii(4,8)==='ftyp')return 'audio/mp4';
 if(ascii(0,4)==='OggS')return 'audio/ogg';
 if(ascii(0,4)==='RIFF'&&ascii(8,12)==='WAVE')return 'audio/wav';
 return null;
}
