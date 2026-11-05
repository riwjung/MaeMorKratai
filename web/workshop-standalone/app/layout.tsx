import type {Metadata} from 'next';
import './globals.css';
export const metadata:Metadata={title:'ห้องฝึกอ่านไพ่ · แม่หมอกระต่าย',description:'บันทึกเสียงและวิธีอ่านไพ่ของแม่หมอ จาก 30 สถานการณ์ทดลอง',robots:{index:false,follow:false},icons:{icon:'/favicon.svg'}};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="th"><body>{children}</body></html>}
