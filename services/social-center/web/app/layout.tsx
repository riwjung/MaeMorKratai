import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "แม่หมอกระต่าย · ศูนย์คอนเทนต์",
  description: "ข้อมูลช่อง คลังความรู้ และห้องออกแบบอนิเมชันแม่หมอกระต่ายบน Mac",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="th"><body>{children}</body></html>;
}
