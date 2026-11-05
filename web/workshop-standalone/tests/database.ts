import {PGlite} from '@electric-sql/pglite';
import {readFile} from 'node:fs/promises';
export const ids={
 owner:'11111111-1111-4111-8111-111111111111',
 reader:'22222222-2222-4222-8222-222222222222',
 other:'33333333-3333-4333-8333-333333333333',
 stranger:'44444444-4444-4444-8444-444444444444'
};
export async function database(){
 const db=new PGlite();
 await db.exec(`
 create role anon;create role authenticated;create role service_role bypassrls;
 create schema auth;create schema storage;
 create table auth.users(id uuid primary key);
 create function auth.uid() returns uuid language sql stable as $$
 select nullif(current_setting('request.jwt.claim.sub',true),'')::uuid;
 $$;
 grant usage on schema public,auth to authenticated,anon,service_role;
 grant execute on function auth.uid() to authenticated,anon,service_role;
 create table storage.buckets(id text primary key,name text,public boolean,file_size_limit integer,allowed_mime_types text[]);
 `);
 for(const file of ['001_workshop.sql','002_cases.sql','003_more_categories.sql'])await db.exec(await readFile(new URL('../supabase/migrations/'+file,import.meta.url),'utf8'));
 for(const id of Object.values(ids))await db.query('insert into auth.users(id) values($1)',[id]);
 for(const [role,id,name] of [['owner',ids.owner,'เจ้าของ'],['reader',ids.reader,'ผู้ทดลอง'],['reader',ids.other,'ผู้ทดลองอีกคน']])
  await db.query('insert into public.workshop_members(user_id,role,display_name) values($1,$2,$3)',[id,role,name]);
 return db;
}
export async function role(db:PGlite,who:string,role='authenticated'){
 await db.exec('reset role');
 await db.query("select set_config('request.jwt.claim.sub',$1,false)",[who]);
 await db.exec(`set role ${role}`);
}
