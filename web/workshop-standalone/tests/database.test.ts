import {test} from 'node:test';
import assert from 'node:assert/strict';
import {randomUUID} from 'node:crypto';
import {database,role,ids} from './database';
import {emptyAnswers} from '../lib/domain';
test('Postgres RPCs enforce membership, isolation, immutable baseline, idempotency, audio and withdrawal',async()=>{
 const db=await database();
 const answer={...emptyAnswers(),answer:'คำอ่านก่อนเห็นใบขยาย'};
 const save=(request:string,rev:number,stage:string,action:string,answers:unknown=answer,consent=true)=>
  db.query('select public.workshop_save($1,$2,$3,$4,$5,$6,$7) revision',['case-01',request,rev,stage,action,JSON.stringify(answers),consent]);
 try{
 await role(db,ids.stranger);
 await assert.rejects(save(randomUUID(),0,'baseline','save'),/FORBIDDEN/);
 assert.equal((await db.query('select * from public.workshop_cases')).rows.length,0);
 await role(db,ids.reader,'anon');
 await assert.rejects(save(randomUUID(),0,'baseline','save'),/permission denied/);
 await role(db,ids.reader);
 assert.equal((await db.query('select * from public.workshop_cases')).rows.length,60);
 await assert.rejects(db.query("insert into public.workshop_readings(reader_id,case_id) values($1,'case-01')",[ids.reader]),/permission denied/);
 await assert.rejects(save(randomUUID(),0,'baseline','save',{},true),/INVALID_INPUT/);
 await assert.rejects(save(randomUUID(),0,'baseline','save',answer,false),/CONSENT/);
 await assert.rejects(save(randomUUID(),0,'baseline','seal',emptyAnswers()),/ANSWER_REQUIRED/);
 const req=randomUUID();await save(req,0,'baseline','save');
 await save(req,0,'baseline','save'); // exact retry, one snapshot
 assert.equal((await db.query('select * from public.workshop_responses')).rows.length,1);
 await assert.rejects(save(req,0,'baseline','save',{...answer,answer:'changed'}),/REQUEST_CONFLICT/);
 await assert.rejects(save(randomUUID(),0,'baseline','save'),/REVISION_CONFLICT/);
 const audio=randomUUID();
 const reserve=()=>db.query('select * from public.workshop_reserve_audio($1,$2,$3,$4,$5,$6)',[audio,'case-01','baseline','audio/webm',1024,3]);
 await reserve();await reserve();
 await assert.rejects(save(randomUUID(),1,'baseline','save',{...answer,audioId:audio}),/AUDIO_NOT_READY/);
 await assert.rejects(db.query('select public.workshop_complete_audio($1,$2)',[audio,ids.reader]),/permission denied/);
 await role(db,ids.owner,'service_role');
 await db.query('select public.workshop_complete_audio($1,$2)',[audio,ids.reader]);
 await role(db,ids.other);
 assert.equal((await db.query('select * from public.workshop_readings')).rows.length,0);
 assert.equal((await db.query('select * from public.workshop_recordings')).rows.length,0);
 await assert.rejects(save(randomUUID(),0,'baseline','save',{...answer,audioId:audio}),/AUDIO_NOT_READY/);
 await role(db,ids.reader);
 await save(randomUUID(),1,'baseline','seal',{...answer,audioId:audio});
 await assert.rejects(save(randomUUID(),2,'baseline','save'),/REVISION_CONFLICT/);
 await assert.rejects(db.query('select * from public.workshop_reserve_audio($1,$2,$3,$4,$5,$6)',[randomUUID(),'case-01','baseline','audio/webm',1024,3]),/REVISION_CONFLICT/);
 await save(randomUUID(),2,'followup','submit',{...emptyAnswers(),answer:'คำอ่านหลังใบขยาย'});
 await assert.rejects(save(randomUUID(),3,'followup','save'),/REVISION_CONFLICT/);
 const reading=(await db.query<{baseline:typeof answer;stage:string}>('select * from public.workshop_readings')).rows[0];
 assert.equal(reading.baseline.answer,answer.answer);assert.equal(reading.stage,'review');
 await role(db,ids.owner);
 assert.equal((await db.query('select * from public.workshop_responses')).rows.length,3);
 await assert.rejects(db.query('select public.workshop_withdraw()'),/OWNER_WITHDRAW/);
 await role(db,ids.reader);
 await db.query('select public.workshop_withdraw()');
 assert.equal((await db.query('select * from public.workshop_readings')).rows.length,0);
 await assert.rejects(save(randomUUID(),0,'baseline','save'),/FORBIDDEN/);
 await role(db,ids.owner);
 assert.equal((await db.query('select * from public.workshop_readings')).rows.length,0);
 assert.equal((await db.query('select * from public.workshop_recordings')).rows.length,0);
 assert.equal((await db.query('select * from public.workshop_withdrawals')).rows.length,1);
 }finally{await db.close()}
});
