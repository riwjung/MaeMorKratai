"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Notice } from "./dashboard";
import ChannelAudit, { type ChannelAuditData } from "./channel-audit";

type Brand = {
  scope: "local_references_only";
  channel: { name: string; instagram: string; target: string };
  character: { summary: string; features: string[]; palette: Array<{ name: string; hex: string }>; primary_reference: string; references: Array<{ id: string; label: string; url: string; role: string }>; motion_rules: string[] };
  reference_video: { label: string; url: string; contact_sheet_url: string; duration_sec: number; observed_style: string[]; beats: Array<{ start: number; end: number; observation: string }>; limitations: string[] };
  pilot: { title: string; status: string; duration_sec: number; no_speech: boolean; shots: Array<{ start: number; end: number; action: string }>; image_prompt: string; video_prompt: string };
  limitations: string[];
  channel_audit?: ChannelAuditData;
};

const mediaURL = (url: string) => /^\/api\/brand\/media\/[A-Za-z0-9_-]+$/.test(url) ? url : "";
const time = (value: number) => `${value.toFixed(value % 1 ? 1 : 0)}s`;

export default function BrandView({ connected, refresh, notify, onConnect }: { connected: boolean; refresh: number; notify: Notice; onConnect: () => void }) {
  const [brand, setBrand] = useState<Brand | null>(null);
  const [failed, setFailed] = useState(false);
  const [selected, setSelected] = useState("");
  useEffect(() => {
    let active = true;
    api<Brand>("/api/brand").then(result => { if (active) { setBrand(result); setSelected(result.character.primary_reference); } }).catch(error => { if (active) { setFailed(true); notify(error.message, true); } });
    return () => { active = false; };
  }, [notify, refresh, connected]);
  const copy = async (text: string) => { try { await navigator.clipboard.writeText(text); notify("คัดลอกพรอมต์แล้ว ยังไม่ได้สร้างภาพหรือใช้เครดิต"); } catch { notify("คัดลอกไม่สำเร็จ สามารถเลือกข้อความในช่องแล้วคัดลอกเองได้", true); } };

  if (!brand) return <div className="chart-empty">{failed ? "ยังอ่านภาพและคลิปอ้างอิงไม่ได้ ตรวจบริการ API แล้วเปิดหน้านี้ใหม่" : "กำลังอ่านคาแรกเตอร์และคลิปอ้างอิง…"}</div>;
  const character = brand.character;
  const current = character.references.find(reference => reference.id === selected) || character.references[0];

  return <div className="view">
    <div className="brand-scope"><div><span className="pill">วิเคราะห์จากไฟล์อ้างอิงในเครื่อง</span><p>หน้านี้สรุปคาแรกเตอร์และภาษาภาพจากไฟล์ที่คุณให้มา</p><p className="footnote">{connected ? "ตรวจการเชื่อมบัญชีแล้ว · การสรุปผลตอบรับของผู้ชมต้องรอข้อมูลจากการซิงก์" : "ยังไม่ได้ยืนยัน mood & tone ของคอนเทนต์ทั้งช่อง ต้องเชื่อมบัญชีและอ่านโพสต์ก่อน"}</p></div>{!connected && <button className="secondary" onClick={onConnect}>เชื่อมข้อมูลช่อง ↗</button>}</div>
    <ChannelAudit data={brand.channel_audit} notify={notify} onConnect={onConnect} />
    <section className="panel character-panel"><div className="character-preview">{current && <img src={mediaURL(current.url)} alt={current.label} className="primary-reference" />}<div className="reference-thumbs">{character.references.map(reference => <button key={reference.id} className={selected === reference.id ? "selected" : ""} aria-label={`ดู ${reference.label}`} aria-pressed={selected === reference.id} onClick={() => setSelected(reference.id)}><img src={mediaURL(reference.url)} alt={reference.label} /></button>)}</div><p className="footnote">{current?.label} · {current?.role}</p></div><div className="character-description"><span className="eyebrow">CHARACTER DNA</span><h2>กระต่ายตัวเดิม ในเรื่องราวใหม่</h2><p>{character.summary}</p><ul className="feature-list">{character.features.map(feature => <li key={feature}>{feature}</li>)}</ul><h3>พาเลตจากภาพต้นแบบ</h3><div className="palette">{character.palette.map(color => <div key={color.name}><span className="color-swatch" style={{ background: /^#[0-9a-f]{6}$/i.test(color.hex) ? color.hex : "#ffffff" }} /><span>{color.name}<small>{color.hex}</small></span></div>)}</div><div className="creative-rule"><strong>เป้าหมาย: น่ารัก · ไม่มีบทพูด</strong><p>เล่าเรื่องด้วยสีหน้า ท่าทาง และการกระทำ ให้ดูเข้าใจได้แม้ปิดเสียง</p></div></div></section>
    <section className="panel"><div className="section-head"><div><span className="eyebrow">VISUAL & STORY REFERENCE</span><h2>{brand.reference_video.label}</h2><p>คลิปอ้างอิง {time(brand.reference_video.duration_sec)} · ใช้ศึกษางานภาพและจังหวะเล่าเรื่อง</p></div><span className="pill">คลิปที่คุณเลือก</span></div><div className="reference-layout"><div className="video-wrap"><video src={mediaURL(brand.reference_video.url)} controls muted playsInline preload="metadata" aria-label="คลิปต้นแบบการเล่าเรื่องแม่หมอกระต่าย" /></div><div><h3>ภาษาภาพที่สังเกตได้</h3><ul className="feature-list">{brand.reference_video.observed_style.map(style => <li key={style}>{style}</li>)}</ul><h3>จังหวะเรื่องราว</h3><div className="story-beats">{brand.reference_video.beats.map((beat, index) => <div className="story-beat" key={index}><span>{time(beat.start)}–{time(beat.end)}</span><p>{beat.observation}</p></div>)}</div></div></div><details className="contact-sheet"><summary>ดูเฟรมอ้างอิงตามลำดับเวลา</summary><img src={mediaURL(brand.reference_video.contact_sheet_url)} alt="เฟรมจากคลิปอ้างอิงตามเวลา เพื่อดูท่าทางและลำดับการเล่าเรื่อง" /></details>{brand.reference_video.limitations.length > 0 && <p className="footnote">{brand.reference_video.limitations.join(" · ")}</p>}</section>
    <div className="two-col"><section className="panel"><h2>กติกาการเคลื่อนไหวของตัวละคร</h2><ul className="feature-list">{character.motion_rules.map(rule => <li key={rule}>{rule}</li>)}</ul></section><section className="panel"><span className="pill">ร่างสำหรับตรวจ · ยังไม่ได้เจน</span><h2>{brand.pilot.title}</h2><p className="muted">{brand.pilot.duration_sec} วินาที · ไม่มีบทพูด · แสดงท่าทาง</p><div className="story-beats">{brand.pilot.shots.map((shot, index) => <div className="story-beat" key={index}><span>{time(shot.start)}–{time(shot.end)}</span><p>{shot.action}</p></div>)}</div></section></div>
    <section className="panel"><div className="section-head"><div><h2>พรอมต์ตั้งต้นสำหรับ Higgsfield</h2><p>ใช้ภาพอ้างอิงกระต่ายประจำช่อง พร้อมคงคาแรกเตอร์และแนวทางไร้บทพูด</p></div><span className="pill">ใช้เครดิต 0</span></div><div className="two-col"><div className="prompt-card"><div className="section-head"><h3>ภาพต้นแบบ / Start frame</h3><button className="source-button" onClick={() => void copy(brand.pilot.image_prompt)}>คัดลอก</button></div><pre>{brand.pilot.image_prompt}</pre></div><div className="prompt-card"><div className="section-head"><h3>การเคลื่อนไหว / Video</h3><button className="source-button" onClick={() => void copy(brand.pilot.video_prompt)}>คัดลอก</button></div><pre>{brand.pilot.video_prompt}</pre></div></div><p className="footnote">พรอมต์เป็นฉบับร่าง ก่อนสร้างจริงต้องเลือกโมเดล ตรวจราคา และอนุมัติงบ Higgsfield</p></section>
    <details className="panel"><summary>แหล่งอ้างอิงและข้อจำกัดของข้อสรุป</summary><ul className="help-list">{brand.limitations.map(value => <li key={value}>{value}</li>)}</ul></details>
  </div>;
}
