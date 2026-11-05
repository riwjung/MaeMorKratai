"use client";

import { useEffect, useState } from "react";
import { api, post } from "@/lib/api";
import type { Report } from "@/lib/types";
import type { Notice } from "./dashboard";

export default function ReportsView({ notify, changed, syncing }: { notify: Notice; changed: () => Promise<void>; syncing: boolean }) {
  const [report, setReport] = useState<Report | null>(null);
  const [busy, setBusy] = useState(false);
  const load = async () => { setReport(await api<Report>("/api/report/latest")); };
  useEffect(() => { void load().catch(() => {}); }, []);
  const create = async () => {
    setBusy(true);
    try { await post("/api/report"); await load(); await changed(); notify("บันทึกรายงาน หลักฐาน สารบัญ และ log ใน Obsidian แล้ว"); }
    catch (error) { notify(error instanceof Error ? error.message : "สร้างรายงานไม่สำเร็จ", true); }
    finally { setBusy(false); }
  };
  const download = () => {
    if (!report) return;
    const url = URL.createObjectURL(new Blob([report.content], { type: "text/markdown;charset=utf-8" }));
    const anchor = document.createElement("a"); anchor.href = url; anchor.download = "maemorkratai-channel-report.md"; anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };
  return <div className="view"><section className="panel"><div className="section-head"><div><span className="eyebrow">ข้อมูลจริง → ข้อสังเกต → แผนทดลอง</span><h2>รายงานสถานะช่อง</h2><p>ทุกผลวิเคราะห์ควรย้อนกลับถึงช่วงเวลาและหลักฐานต้นทางได้</p></div><button className="primary" onClick={() => void create()} disabled={busy || syncing}>{busy ? "กำลังสร้างรายงาน…" : "สร้างรายงานล่าสุด"}</button></div>{report ? <><div className="report-toolbar"><span className="footnote">{report.path}</span><button className="secondary" onClick={download}>ดาวน์โหลด Markdown ↓</button></div><pre className="report">{report.content}</pre></> : <div className="chart-empty"><strong>ยังไม่มีรายงานให้แสดง</strong><p>เชื่อมบัญชีหรือนำเข้าข้อมูล แล้วกดสร้างรายงานเพื่อบันทึกสถานะที่มี</p></div>}</section><div className="two-col"><section className="panel"><h2>Second Brain ของแม่หมอกระต่าย</h2><p>คลังแยกแบรนด์ ผลวิเคราะห์ แนวทางคอนเทนต์ และความรู้ดูดวงที่เจ้าของให้มา ข้อมูลดิบเพิ่มเป็นไฟล์ใหม่ พร้อมสารบัญและบันทึกการเปลี่ยนแปลง</p></section><section className="panel"><h2>จากข้อมูลช่องไปสู่อนิเมชัน</h2><p>ตรวจข้อมูลจริง → เลือกหัวข้อและอารมณ์ → สร้าง storyboard แบบไม่มีบทพูด → ตรวจราคา Higgsfield → อนุมัติก่อนสร้าง</p><p className="footnote">ภาพตัวละครและคลิปอ้างอิงใช้กำหนดทิศทางภาพได้ ส่วนสไตล์ที่ผู้ชมตอบรับต้องอาศัยข้อมูลช่อง</p></section></div></div>;
}
