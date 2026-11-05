"use client";

import { useEffect, useRef, useState } from "react";
import { api, fmt } from "@/lib/api";
import { safePermalink } from "@/lib/media";
import type { Notice } from "./dashboard";
import MediaThumbnail from "./media-thumbnail";

export type ChannelAuditData = {
  status: "awaiting_connection" | "awaiting_content" | "review_ready";
  post_count: number;
  method: string;
  samples: Array<{ platform: string; post_id: string; caption: string; permalink: string; media_type: string; thumbnail_url: string; media_url: string; source_id: string }>;
  caption_observations: string[];
  limitations: string[];
};

export default function ChannelAudit({ data, notify, onConnect }: { data?: ChannelAuditData; notify: Notice; onConnect: () => void }) {
  const [evidence, setEvidence] = useState<unknown>(null);
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => { if (evidence !== null && dialog.current && !dialog.current.open) dialog.current.showModal(); }, [evidence]);
  const showEvidence = async (id: string) => {
    if (!/^[A-Za-z0-9_-]+$/.test(id)) return;
    try { setEvidence(await api(`/api/source/${encodeURIComponent(id)}`)); }
    catch (error) { notify(error instanceof Error ? error.message : "อ่านหลักฐานไม่ได้", true); }
  };
  const awaitingConnection = !data || data.status === "awaiting_connection";

  return <section className="panel channel-audit"><div className="section-head"><div><span className="eyebrow">ข้อมูลช่อง · แยกจากไฟล์อ้างอิงด้านล่าง</span><h2>โพสต์จริงของช่องจาก API</h2><p>ดูภาพและคำบรรยายต้นทาง เพื่อศึกษา mood, tone และรูปแบบคอนเทนต์ของแม่หมอกระต่าย</p></div><span className="pill">{awaitingConnection ? "รอเชื่อมบัญชี" : data?.status === "awaiting_content" ? "รอข้อมูลโพสต์" : "มีตัวอย่างให้ตรวจ"}</span></div>
    {awaitingConnection ? <div className="channel-pending"><div><strong>เชื่อมบัญชีก่อนอ่านสไตล์จากโพสต์จริง</strong><p>เมื่อ Meta อนุญาตและซิงก์ข้อมูลแล้ว ภาพตัวอย่างและคำบรรยายจะปรากฏที่นี่</p></div><button className="secondary" onClick={onConnect}>ไปขั้นตอนเชื่อมบัญชี ↗</button></div> : data?.status === "awaiting_content" && <div className="channel-pending"><div><strong>ยังไม่มีโพสต์จาก API สำหรับตรวจภาพ</strong><p>กด “ซิงก์ข้อมูล” ด้านบน แล้วตรวจขอบเขตข้อมูลที่ Meta อ่านให้ได้</p></div></div>}
    {data && data.samples.length > 0 && <><p className="audit-count">โพสต์ในคลัง {fmt(data.post_count)} รายการ · แสดงตัวอย่าง {fmt(data.samples.length)} รายการ</p><div className="channel-samples">{data.samples.map(sample => {
      const link = safePermalink(sample.permalink);
      const image = sample.thumbnail_url || (["IMAGE", "PHOTO"].includes(sample.media_type) ? sample.media_url : "");
      return <article className="channel-sample" key={`${sample.platform}-${sample.post_id}`}><div className="channel-sample-preview"><MediaThumbnail url={image} alt={`ภาพโพสต์ ${sample.caption.slice(0, 120) || sample.post_id}`} placeholder /></div><div className="channel-sample-body"><div className="sample-meta"><span>{sample.platform === "instagram" ? "Instagram" : sample.platform === "facebook" ? "Facebook" : "โพสต์ช่อง"}</span><span className="pill">{sample.media_type}</span></div><p className="sample-caption">{sample.caption || "โพสต์นี้ไม่มีคำบรรยาย"}</p><div className="sample-actions">{link && <a href={link} target="_blank" rel="noopener noreferrer">เปิดโพสต์ต้นทาง ↗</a>}{sample.source_id && <button className="source-button" onClick={() => void showEvidence(sample.source_id)}>ดูหลักฐาน</button>}</div></div></article>;
    })}</div></>}
    {data && data.caption_observations.length > 0 && <div className="caption-observations"><h3>ข้อสังเกตจากคำบรรยายที่เก็บได้</h3><ul className="feature-list">{data.caption_observations.map((observation, index) => <li key={index}>{observation}</li>)}</ul></div>}
    <p className="footnote">ภาพตัวอย่างและข้อสังเกตจากคำบรรยายยังไม่ใช่ข้อสรุปภาพ เสียง และสไตล์ของทั้งช่อง ต้องตรวจคลิปจริงและขอบเขตข้อมูลประกอบ</p>
    {data?.method && <p className="footnote">วิธีคัดตัวอย่าง: {data.method}</p>}
    {!!data?.limitations.length && <details className="audit-limitations"><summary>ขอบเขตและข้อจำกัดของตัวอย่างช่อง</summary><ul className="help-list">{data.limitations.map((limitation, index) => <li key={index}>{limitation}</li>)}</ul></details>}
    <dialog ref={dialog} onClose={() => setEvidence(null)} className="detail-dialog"><div className="dialog-head"><h2>หลักฐานโพสต์จากต้นทาง</h2><button className="quiet" aria-label="ปิดหลักฐาน" onClick={() => dialog.current?.close()}>×</button></div>{evidence !== null && <pre className="dialog-code">{JSON.stringify(evidence, null, 2)}</pre>}</dialog>
  </section>;
}
