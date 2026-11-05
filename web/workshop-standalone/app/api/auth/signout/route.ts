import {serverClient} from '../../../../lib/supabase-server';
import {sameOrigin} from '../../../../lib/origin';
export async function POST(req:Request){
 if(!sameOrigin(req))return new Response('Forbidden',{status:403});
 const c=await serverClient();await c.auth.signOut();
 return new Response(null,{status:303,headers:{Location:'/login','Cache-Control':'private, no-store'}});
}
