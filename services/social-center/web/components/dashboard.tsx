"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { api, dateText, post } from "@/lib/api";
import type { Status } from "@/lib/types";
import OverviewView from "./overview";
import ConnectView from "./connect";
import ImportView from "./import";
import ReportsView from "./reports";
import BrandView from "./brand";

export type Notice = (message: string, error?: boolean) => void;
type View = "overview" | "connect" | "brand" | "import" | "reports";
const navigation: Array<{ id: View; label: string; icon: string; subtitle: string }> = [
  { id: "overview", label: "ภาพรวมช่อง", icon: "◉", subtitle: "ข้อมูลจริงจาก Facebook และ Instagram" },
  { id: "connect", label: "เชื่อม Social Media", icon: "↗", subtitle: "เชื่อมบัญชี Meta ทีละขั้นบน Mac ของคุณ" },
  { id: "brand", label: "คาแรกเตอร์ & สไตล์", icon: "✦", subtitle: "ภาพต้นแบบและทิศทางอนิเมชันแม่หมอกระต่าย" },
  { id: "import", label: "นำเข้า CSV", icon: "⇧", subtitle: "เริ่มวิเคราะห์จากข้อมูลที่ส่งออกไว้" },
  { id: "reports", label: "รายงาน / Second Brain", icon: "▤", subtitle: "ผลวิเคราะห์พร้อมหลักฐานสำหรับ Obsidian" },
];

export default function Dashboard() {
  const [view, setView] = useState<View>("overview");
  const [status, setStatus] = useState<Status | null>(null);
  const [notice, setNotice] = useState<{ text: string; error: boolean } | null>(null);
  const [busy, setBusy] = useState(false);
  const [refresh, setRefresh] = useState(0);
  const previousRunning = useRef(false);
  const notify = useCallback<Notice>((text, error = false) => setNotice({ text, error }), []);
  const refreshStatus = useCallback(async () => {
    const result = await api<Status>("/api/status");
    if (previousRunning.current && !result.sync_running) {
      setRefresh(n => n + 1);
      const last = result.jobs[0];
      if (last) notify(last.message || "ซิงก์ข้อมูลเสร็จแล้ว", last.status !== "complete");
    }
    previousRunning.current = result.sync_running;
    setStatus(result);
    return result;
  }, [notify]);

  useEffect(() => {
    const initial = window.location.hash.slice(1) as View;
    if (navigation.some(item => item.id === initial)) setView(initial);
    void refreshStatus().catch(() => notify("ยังติดต่อบริการข้อมูลบน Mac ไม่ได้ กรุณาเปิดบริการ API แล้วลองใหม่", true));
    const timer = setInterval(() => { void refreshStatus().catch(() => {}); }, 5000);
    return () => clearInterval(timer);
  }, [refreshStatus, notify]);

  const go = (next: View) => { setView(next); window.history.replaceState(null, "", `#${next}`); };
  const changed = async () => { await refreshStatus(); setRefresh(n => n + 1); };
  const sync = async () => {
    setBusy(true);
    try { await post("/api/sync"); notify("เริ่มซิงก์แล้ว ระบบจะอัปเดตสถานะเมื่อเก็บข้อมูลเสร็จ"); await refreshStatus(); }
    catch (error) { notify(error instanceof Error ? error.message : "เริ่มซิงก์ไม่สำเร็จ", true); }
    finally { setBusy(false); }
  };
  const current = navigation.find(item => item.id === view)!;
  const connectionLabel = status?.connected ? "ตรวจการเชื่อมต่อแล้ว" : status?.configured ? "เลือกบัญชีแล้ว · รอตรวจ" : "ยังไม่เชื่อม Meta";

  return <div className="app-shell">
    <aside className="sidebar">
      <a className="brand" href="#overview" onClick={event => { event.preventDefault(); go("overview"); }} aria-label="แม่หมอกระต่าย หน้าแรก">
        <span className="brand-mark" aria-hidden="true">🐰</span><span>แม่หมอกระต่าย<small>CONTENT & CREATIVE STUDIO</small></span>
      </a>
      <div className="nav-label">พื้นที่ทำงาน</div>
      <nav aria-label="เมนูหลัก">{navigation.map(item => <button key={item.id} onClick={() => go(item.id)} className={`nav ${view === item.id ? "active" : ""}`} aria-current={view === item.id ? "page" : undefined}><span aria-hidden="true">{item.icon}</span>{item.label}</button>)}</nav>
      <div className="sidebar-note"><span className="spark">✧</span><p>อ่านสไตล์ของช่อง<br />ก่อนสร้างเรื่องราวใหม่</p><button onClick={() => go("brand")}>ดูคาแรกเตอร์ ↗</button></div>
      <div className="sidebar-footer"><span className="dot" />บน Mac ของคุณ<small>{status?.scheduler.installed ? "ซิงก์รายวัน 08:00 น." : "ซิงก์เองได้จากปุ่มด้านบน"}</small><small>ไม่มีการใช้เครดิตจากหน้านี้</small></div>
    </aside>
    <main>
      <header className="main-header"><div><p className="eyebrow">แม่หมอกระต่าย / {current.label}</p><h1>{current.label}</h1><p className="muted">{current.subtitle}</p></div><div className="header-actions"><button className={`badge ${status?.connected ? "ready" : ""}`} onClick={() => go("connect")}><span className="status-dot" />{connectionLabel}</button><button className="primary" disabled={!status?.configured || status.sync_running || busy} onClick={() => void sync()}>{busy || status?.sync_running ? "กำลังซิงก์…" : "↻ ซิงก์ข้อมูล"}</button></div></header>
      <div className="status-line"><span>{status?.jobs[0] ? `งานล่าสุด ${dateText(status.jobs[0].ended_at || status.jobs[0].started_at)}` : "รอข้อมูลครั้งแรกจากบัญชีหรือไฟล์ CSV"}</span><span>Asia/Bangkok · ส่วนตัวบนเครื่อง</span></div>
      {notice && <div className={`notice ${notice.error ? "error" : ""}`} role={notice.error ? "alert" : "status"}><span>{notice.text}</span><button className="quiet" aria-label="ปิดข้อความ" onClick={() => setNotice(null)}>×</button></div>}
      {!status && <div className="loading-line">กำลังตรวจสถานะบริการข้อมูล…</div>}
      {view === "overview" && <OverviewView refresh={refresh} notify={notify} onConnect={() => go("connect")} onImport={() => go("import")} />}
      {view === "connect" && <ConnectView status={status} notify={notify} changed={changed} />}
      {view === "brand" && <BrandView refresh={refresh} connected={!!status?.connected} notify={notify} onConnect={() => go("connect")} />}
      {view === "import" && <ImportView notify={notify} changed={changed} />}
      {view === "reports" && <ReportsView notify={notify} changed={changed} syncing={!!status?.sync_running} />}
      <footer className="main-footer">แม่หมอกระต่าย · คลังข้อมูลส่วนตัว · ข้อมูลที่ขาดแสดงเป็น “ไม่มีข้อมูล”</footer>
    </main>
  </div>;
}
