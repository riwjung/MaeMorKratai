import {createServerClient} from '@supabase/ssr';
import {NextResponse,type NextRequest} from 'next/server';
import {publicConfig} from './lib/config';
export async function proxy(request:NextRequest){
  const c=publicConfig();if(!c)return NextResponse.next();
  let response=NextResponse.next({request});
  const client=createServerClient(c.url,c.key,{cookies:{
    getAll:()=>request.cookies.getAll(),
    setAll:values=>{
      values.forEach(({name,value})=>request.cookies.set(name,value));
      response=NextResponse.next({request});
      values.forEach(({name,value,options})=>response.cookies.set(name,value,options));
    }
  }});
  await client.auth.getUser();
  response.headers.set('Cache-Control','private, no-store');
  return response;
}
export const config={matcher:['/','/review','/login','/access-denied','/api/:path*']};
