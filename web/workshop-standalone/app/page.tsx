import {redirect} from 'next/navigation';
import {authorize} from '../lib/auth';
import {Problem} from '../lib/domain';
import {publicConfig} from '../lib/config';
import Workshop from './workshop';
export const dynamic='force-dynamic';
export default async function Page(){
 if(!publicConfig())redirect('/login');
 let auth;try{auth=await authorize()}catch(e){if(e instanceof Problem&&e.status===401)redirect('/login');if(e instanceof Problem&&e.status===403)redirect('/access-denied');throw e}
 return <Workshop member={auth.member}/>;
}
