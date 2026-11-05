// Operator-only. Run through credentials.py; no secrets or email lists in source.
import {createClient} from '@supabase/supabase-js';
import {createInterface} from 'node:readline/promises';
import {mkdir,writeFile,access,readFile} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {createHash} from 'node:crypto';

const url=process.env.NEXT_PUBLIC_SUPABASE_URL,key=process.env.SUPABASE_SECRET_KEY;
if(!url||!key)throw new Error('Run through scripts/credentials.py run');
const db=createClient(url,key,{auth:{persistSession:false,autoRefreshToken:false}});
const bucket=db.storage.from('workshop-audio');
const tables=['members','cases','readings','responses','recordings','withdrawals'];
const check=({data,error})=>{if(error)throw new Error(`Service request failed (${error.code||error.status||'unknown'})`);return data};
async function all(table){
 const rows=[];
 for(let offset=0;;offset+=500){
  let q=db.from('workshop_'+table).select('*');
  if(['members','withdrawals'].includes(table))q=q.order(table==='members'?'user_id':'reader_id');
  else if(table==='readings')q=q.order('reader_id').order('case_id');
  else q=q.order('id');
  const page=check(await q.range(offset,offset+499));rows.push(...page);if(page.length<500)return rows;
 }
}
async function addUser(){
 const input=createInterface({input:process.stdin,output:process.stdout});
 try{
  const email=(await input.question('อีเมลผู้ใช้ (ไม่เขียนลง source): ')).trim().toLowerCase();
  const role=(await input.question('สิทธิ์ owner หรือ reader: ')).trim();
  const display_name=(await input.question('ชื่อที่แสดง: ')).trim();
  if(!email.includes('@')||!['owner','reader'].includes(role)||!display_name)throw new Error('Invalid input');
  if((await input.question(`เพิ่มสิทธิ์ ${role} ให้บัญชีที่ระบุ? พิมพ์ ADD: `))!=='ADD')return;
  let user=null;
  for(let page=1;;page++){
   const result=check(await db.auth.admin.listUsers({page,perPage:100}));
   user=result.users.find(u=>u.email?.toLowerCase()===email);
   if(user||result.users.length<100)break;
  }
  if(!user)user=check(await db.auth.admin.createUser({email,email_confirm:true})).user;
  if(!user)throw new Error('Cannot create user');
  const old=check(await db.from('workshop_members').select('*').eq('user_id',user.id).maybeSingle());
  if(old&&!old.active)throw new Error('บัญชีนี้ระงับสิทธิ์/ถอนความยินยอมแล้ว ต้องจัดการคำขอก่อน ไม่เปิดสิทธิ์กลับอัตโนมัติ');
  check(await db.from('workshop_members').upsert({user_id:user.id,role,display_name,active:true}));
  console.log('เพิ่มสิทธิ์แล้ว ตั้งรหัสเริ่มต้นด้วย scripts/passwords.py provision ก่อนเข้าเว็บ');
 }finally{input.close()}
}
async function syncCases(){
 const catalog=JSON.parse(await readFile(new URL('../lib/cases.json',import.meta.url),'utf8'));
 const metadata=catalog.map(({id,version,split})=>({id,version,split}));
 const existing=await all('cases'),byId=new Map(existing.map(c=>[c.id,c]));
 for(const c of metadata){
  const old=byId.get(c.id);
  if(old&&(old.version!==c.version||old.split!==c.split))throw new Error(`Case metadata conflict: ${c.id}; stopped without overwriting`);
 }
 const missing=metadata.filter(c=>!byId.has(c.id));
 if(missing.length)check(await db.from('workshop_cases').upsert(missing,{onConflict:'id',ignoreDuplicates:true}));
 const after=new Map((await all('cases')).map(c=>[c.id,c]));
 if(metadata.some(c=>after.get(c.id)?.version!==c.version||after.get(c.id)?.split!==c.split))throw new Error('Case registration verification failed');
 console.log(`ลงทะเบียนเคสครบ ${metadata.length} เคส (เพิ่ม ${missing.length}); ไม่แก้คำอ่านหรือเสียง`);
}
async function backup(){
 const folder=resolve(process.argv[3]||join('backups',new Date().toISOString().replace(/[:.]/g,'-')));
 try{await access(folder);throw new Error('Backup destination already exists')}catch(e){if(e.code!=='ENOENT')throw e}
 await mkdir(folder,{recursive:true,mode:0o700});
 await mkdir(join(folder,'audio'),{mode:0o700});
 const data={};
 // Run while readers are idle. This is a portable export, not a transactional DB snapshot.
 for(const name of tables)data[name]=await all(name);
 const active=new Set(data.members.filter(m=>m.active).map(m=>m.user_id));
 for(const name of ['readings','responses','recordings'])data[name]=data[name].filter(r=>active.has(r.reader_id));
 const files=[];
 for(const row of data.recordings.filter(r=>r.status==='ready')){
  const blob=check(await bucket.download(row.object_key)),bytes=Buffer.from(await blob.arrayBuffer());
  if(bytes.length!==row.bytes)throw new Error('Audio size mismatch; incomplete backup');
  const name=`audio/${row.id}.${row.mime==='audio/mp4'?'m4a':row.mime.split('/')[1]}`;
  await writeFile(join(folder,name),bytes,{mode:0o600});
  files.push({id:row.id,reader_id:row.reader_id,path:name,object_key:row.object_key,bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')});
 }
 await writeFile(join(folder,'data.json'),JSON.stringify(data,null,2),{mode:0o600});
 const reviewFiles=[];
 const reviewBucket=(check(await db.storage.listBuckets())).find(b=>b.id==='workshop-review');
 if(reviewBucket){
  if(reviewBucket.public)throw new Error('Review bucket unexpectedly public');
  const store=db.storage.from('workshop-review');
  for(const id of active){for(const path of await objectPaths(id,store)){
   const blob=check(await store.download(path)),bytes=Buffer.from(await blob.arrayBuffer());
   const local=join(folder,'review',path);await mkdir(resolve(local,'..'),{recursive:true,mode:0o700});await writeFile(local,bytes,{mode:0o600});
   reviewFiles.push({path:'review/'+path,object_key:path,bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')});
  }}
 }
 const manifest={format:'maemorkratai-workshop-v2',createdAt:new Date().toISOString(),complete:true,files,reviewFiles,
  note:'Run while readers are idle. Auth identities must be remapped on restore. Withdrawn readers are excluded from readings/audio.'};
 await writeFile(join(folder,'manifest.json'),JSON.stringify(manifest,null,2),{mode:0o600});
 console.log(`สำรองสำเร็จ ${files.length} ไฟล์เสียง ใน ${folder}`);
}
async function objectPaths(prefix,store=bucket){
 const paths=[];
 for(let offset=0;;offset+=100){
  const page=check(await store.list(prefix,{limit:100,offset,sortBy:{column:'name',order:'asc'}}));
  for(const item of page){const p=prefix+'/'+item.name;if(item.id)paths.push(p);else paths.push(...await objectPaths(p,store))}
  if(page.length<100)break;
 }
 return paths;
}
async function purge(){
 const pending=check(await db.from('workshop_withdrawals').select('*').is('completed_at',null));
 let count=0;
 for(const row of pending){
  // Supabase signed upload URLs last 2 hours. Allow pending requests and clock skew.
  if(Date.now()-Date.parse(row.requested_at)<150*60*1000)continue;
  const member=check(await db.from('workshop_members').select('active').eq('user_id',row.reader_id).single());
  if(member.active)throw new Error('Refusing to purge an active member');
  const paths=await objectPaths(row.reader_id);
  for(let i=0;i<paths.length;i+=100)check(await bucket.remove(paths.slice(i,i+100)));
  if((check(await db.storage.listBuckets())).some(b=>b.id==='workshop-review')){
   const review=db.storage.from('workshop-review'),reviewPaths=await objectPaths(row.reader_id,review);
   for(let i=0;i<reviewPaths.length;i+=100)check(await review.remove(reviewPaths.slice(i,i+100)));
  }
  check(await db.from('workshop_readings').delete().eq('reader_id',row.reader_id)); // cascades revisions/recordings
  check(await db.from('workshop_withdrawals').update({completed_at:new Date().toISOString()}).eq('reader_id',row.reader_id));
  count++;
 }
 console.log(`ลบข้อมูลและเสียงบนบริการ ${count} รายการ; คำขอต้องเก่ากว่า 2 ชั่วโมง 30 นาที`);
 console.log('ตรวจและลบสำเนา export/backup ในเครื่อง รวมถึง retention ของผู้ให้บริการด้วย ไม่ได้ลบโดยคำสั่งนี้');
}
try{
 switch(process.argv[2]){
  case 'add-user':await addUser();break;
  case 'sync-cases':await syncCases();break;
  case 'backup':await backup();break;
  case 'purge-withdrawals':await purge();break;
  case 'check':{
   check(await db.from('workshop_cases').select('id').limit(1));
   const b=check(await db.storage.getBucket('workshop-audio'));
   if(b.public)throw new Error('Audio bucket must be private');
   console.log('เชื่อมฐานข้อมูลได้ และ bucket เสียงเป็นส่วนตัว');
   const publicKey=process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;
   if(!publicKey)throw new Error('ยังไม่มี publishable key สำหรับหน้าเข้าสู่ระบบ');
   const settings=await fetch(url+'/auth/v1/settings',{
    headers:{apikey:publicKey},signal:AbortSignal.timeout(15000)
   });
   if(!settings.ok)throw new Error(`ตรวจ publishable key ไม่ผ่าน (HTTP ${settings.status}); คัดลอกใหม่จาก API Keys ของโปรเจกต์เดียวกัน แล้วใช้ credentials.py configure`);
   const auth=await settings.json();
   if(!auth.external?.email)throw new Error('ยังไม่ได้เปิด Email provider ใน Supabase Auth');
   console.log('publishable key และ Email provider พร้อม; รุ่นนี้เข้าใช้ด้วยอีเมลและรหัสผ่าน ไม่ต้องตั้ง SMTP');
   if(!auth.disable_signup)console.log('การสมัครจาก client ยังเปิดอยู่; ห้องทดลองตรวจ membership เพิ่ม แต่ควรปิดการสมัครเองใน Auth settings');
   break;
  }
  default:console.log('manage.mjs add-user | sync-cases | check | backup [folder] | purge-withdrawals');
 }
}catch(e){console.error(e.message);process.exitCode=1}
