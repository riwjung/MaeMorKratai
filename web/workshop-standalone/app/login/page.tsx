import {publicConfig} from '../../lib/config';
import LoginForm from './form';
export const dynamic='force-dynamic';
export default function Login(){
 return <main className="auth-shell"><section className="auth-card panel"><span className="brand-mark">✧</span><span className="eyebrow">แม่หมอกระต่าย · READING STUDIO</span><h1>สมุดคำอ่านของเรา</h1><p className="auth-copy">พื้นที่ส่วนตัวสำหรับเล่าคำอ่าน เก็บเสียง<br/>และค่อย ๆ สร้างความรู้ในแบบของคุณ</p>{publicConfig()?<LoginForm/>:<div className="banner" role="status">กำลังเตรียมห้องทดลอง<br/>เมื่อพร้อมแล้ว เจ้าของจะส่งลิงก์ให้เข้ามาใช้งาน</div>}<p className="muted small">เฉพาะผู้ที่เจ้าของเพิ่มสิทธิ์ไว้</p></section></main>
}
