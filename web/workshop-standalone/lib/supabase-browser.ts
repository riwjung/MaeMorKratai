'use client';
import {createBrowserClient} from '@supabase/ssr';
import {publicConfig} from './config';
export function browserClient(){
  const c=publicConfig();if(!c)throw new Error('ห้องทดลองยังไม่พร้อมใช้งาน');
  return createBrowserClient(c.url,c.key);
}
