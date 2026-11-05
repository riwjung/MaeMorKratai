/**
 * Loopback-only Auth/REST/Storage transport fixture for browser QA.
 * Executes the real migrations/RPC/RLS in PGlite. This is NOT Supabase service QA.
 * No fixture code is imported by the app.
 */
import {createServer} from 'node:http';
import {randomUUID} from 'node:crypto';
import {spawn} from 'node:child_process';
import {database,ids,role} from './database';

const db=await database(),objects=new Map<string,{bytes:Buffer;mime:string}>(),tokens=new Map<string,string>();
let queue:Promise<unknown>=Promise.resolve();
const jwt=(id:string)=>[
 Buffer.from(JSON.stringify({alg:'HS256',typ:'JWT'})).toString('base64url'),
 Buffer.from(JSON.stringify({sub:id,role:'authenticated',aud:'authenticated',exp:Math.floor(Date.now()/1000)+7200})).toString('base64url'),
 'loopback-test-signature'].join('.');
const identity=(header:string|undefined)=>{
 try{return JSON.parse(Buffer.from(header?.replace('Bearer ','').split('.')[1]||'','base64url').toString()).sub as string}catch{return ''}
};
const user=(id:string)=>({id,aud:'authenticated',role:'authenticated',email:(Object.entries(ids).find(([,v])=>v===id)?.[0]||'unknown')+'@example.test',created_at:new Date().toISOString(),app_metadata:{provider:'email'},user_metadata:{}});
const server=createServer(async(req,res)=>{
 res.setHeader('Access-Control-Allow-Origin','http://127.0.0.1:3012');
 res.setHeader('Access-Control-Allow-Headers','*');res.setHeader('Access-Control-Allow-Methods','GET,POST,PUT,HEAD,OPTIONS');
 const send=(data:unknown,status=200)=>{res.statusCode=status;res.setHeader('Content-Type','application/json');res.end(JSON.stringify(data))};
 if(req.method==='OPTIONS'){res.end();return}
 const url=new URL(req.url||'/','http://127.0.0.1:55123'),path=url.pathname;
 const chunks:Buffer[]=[];for await(const part of req)chunks.push(part);const body=Buffer.concat(chunks);
 const input=()=>body.length?JSON.parse(body.toString()):{};
 const id=identity(req.headers.authorization),admin=req.headers.authorization==='Bearer loopback-service-test-key';
 try{
  if(path==='/auth/v1/otp'){send({});return}
  if(path==='/auth/v1/token'&&url.searchParams.get('grant_type')==='password'){
   const b=input(),id=ids[b.email.split('@')[0] as keyof typeof ids];
   if(!id||b.password!=='loopback-password'){send({msg:'Invalid credentials',error_code:'invalid_credentials'},400);return}
   send({access_token:jwt(id),refresh_token:'loopback-refresh',token_type:'bearer',expires_in:7200,user:user(id)});return;
  }
  if(path==='/auth/v1/user'){if(!Object.values(ids).includes(id))send({msg:'Unauthorized'},401);else send(user(id));return}
  if(path==='/auth/v1/logout'){send({});return}
  if(path.startsWith('/rest/v1/')){
   const run=async()=>{
    await role(db,id,admin?'service_role':id?'authenticated':'anon');
    const name=path.slice('/rest/v1/'.length);
    if(name.startsWith('rpc/')){
     const fn=name.slice(4),b=input();
     const spec:Record<string,string[]>={workshop_save:['p_case','p_request','p_revision','p_stage','p_action','p_answers','p_consent'],
      workshop_reserve_audio:['p_id','p_case','p_stage','p_mime','p_bytes','p_duration'],
      workshop_complete_audio:['p_id','p_reader'],workshop_withdraw:[]};
     if(!spec[fn])throw new Error('Unknown RPC');
     const keys=spec[fn],params=keys.map(k=>k==='p_answers'?JSON.stringify(b[k]):b[k]);
     const sql=fn==='workshop_reserve_audio'?`select * from public.${fn}(${keys.map((_,i)=>'$'+(i+1))})`:
      `select public.${fn}(${keys.map((_,i)=>'$'+(i+1))}) as result`;
     const result=await db.query(sql,params);
     return fn==='workshop_reserve_audio'?result.rows:(result.rows[0] as {result:unknown}).result;
    }
    if(!/^workshop_(members|cases|readings|responses|recordings|withdrawals)$/.test(name))throw new Error('Unknown table');
    const columns=url.searchParams.get('select')||'*';
    if(!/^[a-z_,*]+$/.test(columns))throw new Error('Invalid columns');
    const values:unknown[]=[],where:string[]=[];
    for(const [k,v] of url.searchParams){
     if(['select','order','offset','limit'].includes(k))continue;
     if(!/^[a-z_]+$/.test(k))throw new Error('Invalid filter');
     if(v==='is.null'){where.push(k+' is null');continue}
     if(!v.startsWith('eq.'))throw new Error('Unsupported filter');
     values.push(v.slice(3));where.push(`${k}=$${values.length}`);
    }
    const order=(url.searchParams.get('order')||'').split(',').filter(Boolean).map(o=>{
     const [key,dir]=o.split('.');if(!/^[a-z_]+$/.test(key)||!['asc','desc'].includes(dir))throw new Error('Invalid order');return key+' '+dir;
    });
    const limit=Number(url.searchParams.get('limit')||1000),offset=Number(url.searchParams.get('offset')||0);
    if(!Number.isSafeInteger(limit)||!Number.isSafeInteger(offset))throw new Error('Invalid range');
    const result=await db.query(`select ${columns} from public.${name}${where.length?' where '+where.join(' and '):''}${order.length?' order by '+order.join(','):''} limit ${limit} offset ${offset}`,values);
    return req.headers.accept?.includes('vnd.pgrst.object')?(result.rows[0]||null):result.rows;
   };
   const pending=queue.then(run);queue=pending.catch(()=>{});
   try{send(await pending)}catch(e){const err=e as Error&{code?:string};send({message:err.message,code:err.code||'fixture'},400)}
   return;
  }
  const upload='/storage/v1/object/upload/sign/',download='/storage/v1/object/sign/';
  if(path.startsWith(upload)){
   const key=path.slice(upload.length);
   if(req.method==='POST'&&admin){const token=randomUUID();tokens.set(token,key);send({url:'/object/upload/sign/'+key+'?token='+token});return}
   if(req.method==='PUT'&&tokens.get(url.searchParams.get('token')||'')===key){
    if(objects.has(key)){send({message:'Already exists'},409);return}
    const request=new Request(url,{method:'POST',headers:{'content-type':req.headers['content-type']||''},body});
    const form=await request.formData();let file:File|undefined;
    for(const value of form.values())if(typeof value!=='string')file=value;
    if(!file)throw new Error('Missing audio');
    objects.set(key,{bytes:Buffer.from(await file.arrayBuffer()),mime:file.type});send({Key:key});return;
   }
  }
  if(path.startsWith(download)){
   const key=path.slice(download.length),object=objects.get(key);
   if(!object){send({message:'Not found',statusCode:404},404);return}
   if(req.method==='POST'&&admin){const token=randomUUID();tokens.set(token,key);send({signedURL:'/object/sign/'+key+'?token='+token});return}
   if(tokens.get(url.searchParams.get('token')||'')===key&&['GET','HEAD'].includes(req.method||'')){
    const range=req.headers.range?.match(/bytes=(\d+)-(\d*)/);
    const start=range?Number(range[1]):0,end=range&&range[2]?Math.min(Number(range[2]),object.bytes.length-1):object.bytes.length-1;
    if(start>object.bytes.length-1){res.statusCode=416;res.end();return}
    res.setHeader('Content-Type',object.mime);res.setHeader('Accept-Ranges','bytes');
    res.setHeader('Content-Length',end-start+1);
    if(range){res.statusCode=206;res.setHeader('Content-Range',`bytes ${start}-${end}/${object.bytes.length}`)}
    res.end(req.method==='HEAD'?undefined:object.bytes.subarray(start,end+1));return;
   }
  }
  send({message:'Forbidden fixture endpoint'},403);
 }catch(e){send({message:e instanceof Error?e.message:'Fixture failed'},500)}
});
await new Promise<void>(resolve=>server.listen(55123,'127.0.0.1',resolve));
const app=spawn('npm',['run','dev'],{stdio:'inherit',env:{...process.env,
 NEXT_PUBLIC_SUPABASE_URL:'http://127.0.0.1:55123',
 NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY:'loopback-public-test-key',
 SUPABASE_SECRET_KEY:'loopback-service-test-key'}});
const stop=()=>{app.kill('SIGTERM');server.close();void db.close();setTimeout(()=>process.exit(),300).unref()};
process.on('SIGTERM',stop);process.on('SIGINT',stop);
console.log('Loopback fixture ready; synthetic password accounts only');
