'use client';
export default function ErrorPage({reset}:{reset:()=>void}){return <main className="auth-shell"><section className="auth-card panel"><h1>เปิดห้องทดลองไม่สำเร็จ</h1><p>กรุณาลองอีกครั้ง หรือติดต่อเจ้าของห้องหากยังเข้าไม่ได้</p><button className="primary" onClick={reset}>ลองอีกครั้ง</button></section></main>}
