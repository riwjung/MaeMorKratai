// Operator-only import. Private input is never bundled with the website.
import {readFile} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {createHash} from 'node:crypto';
import {createClient} from '@supabase/supabase-js';
const root=resolve(process.argv[2]||'');if(!process.argv[2])throw new Error('Pass private intake directory');
const db=createClient(process.env.NEXT_PUBLIC_SUPABASE_URL,process.env.SUPABASE_SECRET_KEY,{auth:{persistSession:false}});
const check=r=>{if(r.error)throw new Error('Provider error '+(r.error.statusCode||r.error.code||''));return r.data};
const backup=JSON.parse(await readFile(join(root,'backup/data.json'),'utf8'));
const owners=check(await db.from('workshop_members').select('*').eq('role','owner').eq('active',true));if(owners.length!==1)throw new Error('Expected exactly one active owner');const owner=owners[0].user_id;
const rows=(await readFile(join(root,'development/cases.jsonl'),'utf8')).trim().split('\n').map(JSON.parse);
const styles=JSON.parse(await readFile(join(root,'development/review-draft.json'),'utf8'));
const catalog=JSON.parse(await readFile(new URL('../lib/cases.json',import.meta.url),'utf8'));
const live=check(await db.from('workshop_readings').select('*').eq('reader_id',owner));
if(rows.length!==40||new Set(rows.map(x=>x.caseId)).size!==40)throw new Error('Expected 40 unique development cases');
const sources=[];
for(const row of rows){
 const c=catalog.find(c=>c.id===row.caseId),old=backup.readings.find(x=>x.reader_id===owner&&x.case_id===row.caseId),current=live.find(x=>x.case_id===row.caseId);
 if(row.split!=='development'||c?.split!=='development'||c.version!==row.caseVersion||!old||!current||current.revision!==row.sourceRevision||JSON.stringify(current.baseline)!==JSON.stringify(old.baseline)||JSON.stringify(current.followup)!==JSON.stringify(old.followup))throw new Error('Source mismatch; no import performed');
 const payload={id:row.caseId,sourceRevision:row.sourceRevision,caseVersion:row.caseVersion};
 for(const stage of ['baseline','followup']){
  if(row[stage].originalText!==old[stage].answer)throw new Error('Original text mismatch');
  payload[stage]={originalText:row[stage].originalText,machineTranscript:row[stage].machineTranscript,reviewText:row[stage].reviewText,sourceType:row[stage].sourceType,notes:row[stage].notes,audioId:old[stage].audioId};
 }
 const sourceHash=createHash('sha256').update(JSON.stringify(payload)).digest('hex');
 sources.push({payload:{...payload,sourceHash},item:{id:row.caseId,title:'เคส '+String(c.number).padStart(2,'0')+' · '+c.title,category:c.category,sourceHash}});
}
if(styles.holdoutAnswersIncluded!==false||styles.styleObservations.some(o=>o.sources.some(id=>!rows.some(r=>r.caseId===id))))throw new Error('Style contains non-development references');
const style={id:'style',observations:styles.styleObservations},styleHash=createHash('sha256').update(JSON.stringify(style)).digest('hex');
sources.push({payload:{...style,sourceHash:styleHash},item:{id:'style',title:'สำนวน 6 ข้อ',category:'style',sourceHash:styleHash}});
const name='workshop-review',buckets=check(await db.storage.listBuckets()),existing=buckets.find(b=>b.id===name);
if(existing?.public)throw new Error('Review bucket must be private');
if(!existing)check(await db.storage.createBucket(name,{public:false,fileSizeLimit:1048576,allowedMimeTypes:['application/json']}));
const bucket=db.storage.from(name);
async function immutable(path,data){const body=JSON.stringify(data),previous=await bucket.download(path);if(!previous.error){if(await previous.data.text()!==body)throw new Error('Existing review source differs; refusing overwrite');return}if(!['404','400'].includes(String(previous.error.statusCode)))throw new Error('Cannot inspect destination');check(await bucket.upload(path,body,{contentType:'application/json',upsert:false}))}
for(const x of sources)await immutable(owner+'/'+x.payload.id+'/source.json',x.payload);
await immutable(owner+'/manifest.json',{format:'workshop-owner-review-v1',items:sources.map(x=>x.item)});
console.log(JSON.stringify({importedCases:40,styleProposals:styles.styleObservations.length,holdoutIncluded:0,approved:0,originalReadingsChanged:0,privateBucket:true}));
