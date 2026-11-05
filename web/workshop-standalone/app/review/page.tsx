import {redirect} from 'next/navigation';
import {authorize} from '../../lib/auth';
import {Problem} from '../../lib/domain';
import Review from './review';
export const dynamic='force-dynamic';
export default async function Page(){try{const a=await authorize();if(a.member.role!=='owner')redirect('/access-denied')}catch(e){if(e instanceof Problem&&e.status===401)redirect('/login');if(e instanceof Problem&&e.status===403)redirect('/access-denied');throw e}return <Review/>}
