"use client";

import { useState } from "react";
import { api, fmt, labels } from "@/lib/api";
import type { Preview } from "@/lib/types";
import type { Notice } from "./dashboard";

export default function ImportView({ notify, changed }: { notify: Notice; changed: () => Promise<void> }) {
  const [preview, setPreview] = useState<Preview | null>(null);
  const [mapping, setMapping] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);
  const [period, setPeriod] = useState("lifetime");
  const chooseFile = async (file: File | undefined) => {
    setPreview(null); setMapping({});
    if (!file) return;
    if (file.size > 20 * 1024 * 1024) { notify("ไฟล์ CSV ต้องไม่เกิน 20 MB", true); return; }
    setBusy(true);
    try { const form = new FormData(); form.append("file", file); const result = await api<Preview>("/api/import/preview", { method: "POST", body: form }); setPreview(result); setMapping(result.mapping); }
    catch (error) { notify(error instanceof Error ? error.message : "อ่านไฟล์ไม่ได้", true); }
    finally { setBusy(false); }
  };
  const submit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    form.append("mapping", JSON.stringify(mapping));
    setBusy(true);
    try { const result = await api<{ status: string; rows: number }>("/api/import", { method: "POST", body: form }); notify(result.status === "unchanged" ? "ไฟล์และการจับคู่ชุดนี้นำเข้าแล้ว ไม่มีข้อมูลซ้ำ" : `นำเข้า ${fmt(result.rows)} แถว พร้อมสร้างรายงานแล้ว`); await changed(); }
    catch (error) { notify(error instanceof Error ? error.message : "นำเข้าไม่สำเร็จ", true); }
    finally { setBusy(false); }
  };

  return <div className="view"><div className="import-layout"><section className="panel"><span className="eyebrow">ทางเลือกเมื่อยังไม่เชื่อม Meta</span><h2>นำเข้าจาก Meta Business Suite</h2><p>รองรับข้อมูลโพสต์/Reels ภาพรวมรายวัน และคอมเมนต์ ตรวจคอลัมน์ก่อนบันทึก</p><form onSubmit={event => void submit(event)}><label className="file-drop">เลือกไฟล์ CSV<input type="file" name="file" accept=".csv,text/csv" required onChange={event => void chooseFile(event.target.files?.[0])} /><small>สูงสุด 20 MB · UTF-8, UTF-16 หรือภาษาไทย CP874</small></label><div className="two-col"><label>แพลตฟอร์ม<select name="platform"><option value="instagram">Instagram</option><option value="facebook">Facebook</option></select></label><label>ชนิดข้อมูล<select name="kind"><option value="content">โพสต์ / Reels</option><option value="daily">ภาพรวมรายวัน</option><option value="comments">คอมเมนต์</option></select></label></div><label>Account / Page ID<input name="account_id" required placeholder="ใช้ ID ของบัญชีที่ส่งออกข้อมูล" /></label><label>Timezone ของไฟล์<input name="timezone" defaultValue="Asia/Bangkok" required /></label><label>ช่วงวัดของตัวเลข<select name="period" value={period} onChange={event => setPeriod(event.target.value)}><option value="lifetime">ยอดสะสมตั้งแต่เผยแพร่โพสต์</option><option value="total_over_range">ยอดเฉพาะช่วงวันที่ระบุ</option></select></label><div className="two-col"><label>วันเริ่มช่วง<input type="date" name="start" required={period === "total_over_range"} /></label><label>วันสิ้นสุดช่วง (ไม่รวมวันนี้)<input type="date" name="end" required={period === "total_over_range"} /></label></div><p className="footnote">ข้อมูลรายวันใช้วันที่ในแต่ละแถว ยอดเฉพาะช่วงจะไม่ปนกับอันดับยอดสะสม</p>
        {preview && <div className="csv-mapping"><h3>จับคู่คอลัมน์ · {fmt(preview.rows)} แถว</h3><div className="mapping-grid">{preview.fields.map(field => <label key={field}>{labels[field] || field}<select value={mapping[field] || ""} onChange={event => setMapping(value => ({ ...value, [field]: event.target.value }))}><option value="">ไม่มีคอลัมน์นี้</option>{preview.headers.map(header => <option key={header} value={header}>{header}</option>)}</select></label>)}</div></div>}<button className="primary" type="submit" disabled={busy || !preview}>{busy ? "กำลังอ่านข้อมูล…" : "นำเข้าและสร้างรายงาน"}</button></form></section><section className="panel import-help"><h2>เตรียมไฟล์อย่างไร</h2><ol className="help-list"><li>เปิด Meta Business Suite → Insights หรือ Content แล้วเลือก Facebook/Instagram ให้ถูกบัญชี</li><li>เลือกช่วงวันที่และส่งออก CSV แยกตามชนิดข้อมูลที่มี</li><li>เลือกไฟล์ในหน้านี้ แล้วตรวจว่าชื่อคอลัมน์ตรงกับข้อมูลที่ต้องการ</li><li>ใช้วันที่ YYYY-MM-DD และค่าตัวเลขเต็ม เช่น 1200 แทน 1.2K</li></ol><p className="footnote">การนำเข้า CSV ไม่ใช่การยืนยันสิทธิ์ API สถานะการเชื่อม Meta จะตรวจแยกต่างหาก</p></section></div></div>;
}
