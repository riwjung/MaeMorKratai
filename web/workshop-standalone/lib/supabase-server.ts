import 'server-only';
import {cookies} from 'next/headers';
import {createServerClient} from '@supabase/ssr';
import {createClient} from '@supabase/supabase-js';
import {publicConfig} from './config';
import {Problem} from './domain';
export async function serverClient(){
  const config=publicConfig();if(!config)throw new Problem(503,'ห้องทดลองยังไม่พร้อมใช้งาน');
  const jar=await cookies();
  return createServerClient(config.url,config.key,{cookies:{
    getAll:()=>jar.getAll(),
    setAll:values=>{try{for(const {name,value,options} of values)jar.set(name,value,options)}catch{/* Proxy refreshes cookies for Server Components. */}}
  }});
}
export function adminClient(){
  const c=publicConfig(),key=process.env.SUPABASE_SECRET_KEY;
  if(!c||!key)throw new Problem(503,'พื้นที่เก็บเสียงยังไม่พร้อมใช้งาน');
  return createClient(c.url,key,{auth:{autoRefreshToken:false,persistSession:false}});
}
