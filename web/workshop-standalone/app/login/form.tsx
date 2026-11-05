'use client';
import {useState} from 'react';
import {useRouter} from 'next/navigation';
import {browserClient} from '../../lib/supabase-browser';
export default function LoginForm(){
 const router=useRouter(),[email,setEmail]=useState(''),[password,setPassword]=useState(''),[busy,setBusy]=useState(false),[error,setError]=useState('');
 async function login(){setBusy(true);setError('');try{
  const {error}=await browserClient().auth.signInWithPassword({email:email.trim(),password});
  if(error)throw new Error('เข้าใช้ไม่สำเร็จ กรุณาตรวจอีเมลและรหัสผ่าน แล้วลองอีกครั้ง');
  setPassword('');
  router.replace('/');router.refresh();
 }catch(e){setError((e as Error).message)}finally{setBusy(false)}}
 return <form onSubmit={e=>{e.preventDefault();void login()}} className="auth-form">
 <label className="field">อีเมลที่ได้รับสิทธิ์<input type="email" autoComplete="username" required value={email} disabled={busy} onChange={e=>setEmail(e.target.value)}/></label>
 <label className="field">รหัสผ่าน<input type="password" autoComplete="current-password" required value={password} disabled={busy} onChange={e=>setPassword(e.target.value)}/></label>
 {error&&<p className="error banner" role="alert">{error}</p>}
 <button className="primary" disabled={busy}>{busy?'กรุณารอสักครู่…':'เข้าห้องทดลอง'}</button>
 <p className="muted small">ใช้รหัสผ่านที่ได้รับจากเจ้าของห้อง<br/>หากลืมรหัสผ่าน ติดต่อเจ้าของให้ตั้งใหม่ได้</p>
 </form>
}
