import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = {
 title:'แม่หมอกระต่าย · ห้องไพ่ใต้แสงจันทร์',
 description:'ตั้งคำถามในใจ ให้แม่หมอกระต่ายเปิดไพ่หนึ่งใบ ชวนทบทวนเรื่องความรักในห้องไพ่ใต้แสงจันทร์',
 robots:{index:false,follow:false},
};
export default function Layout({children}:{children:React.ReactNode}) {
 return <html lang="th"><body>{children}</body></html>;
}
