"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { api, fmt, labels } from "@/lib/api";
import type { Findings, Overview, Platform, Post } from "@/lib/types";
import type { Notice } from "./dashboard";
import MediaThumbnail from "./media-thumbnail";

function Groups({ rows, empty }: { rows: Record<string, number>; empty: string }) {
  const pairs = Object.entries(rows).sort((a, b) => b[1] - a[1]);
  return pairs.length ? <div className="groups">{pairs.map(([name, count]) => <div className="topic-row" key={name}><span>{name}</span><strong>{fmt(count)}</strong></div>)}</div> : <p className="muted empty-small">{empty}</p>;
}

function Trend({ overview }: { overview: Overview }) {
  const [metric, setMetric] = useState("views");
  const rows = metric === "followers" ? overview.follower_trend : overview.trend;
  const valid = rows.map((row, index) => ({ x: index, y: row[metric === "followers" ? "value" : metric] })).filter(point => typeof point.y === "number") as Array<{ x: number; y: number }>;
  const max = Math.max(1, ...valid.map(point => point.y));
  const getX = (index: number) => 54 + index * 846 / Math.max(rows.length - 1, 1);
  const getY = (value: number) => 228 - value / max * 195;
  const segments: string[] = [];
  let current = "";
  rows.forEach((row, index) => {
    const value = row[metric === "followers" ? "value" : metric];
    if (typeof value !== "number") { if (current) segments.push(current); current = ""; }
    else current += `${current ? " L" : "M"}${getX(index)},${getY(value)}`;
  });
  if (current) segments.push(current);
  return <section className="panel"><div className="section-head"><div><h2>แนวโน้ม 90 วัน</h2><p>วันที่ขาดข้อมูลเว้นไว้ เพื่อให้อ่านความครบถ้วนได้</p></div><select aria-label="ตัวชี้วัดแนวโน้ม" value={metric} onChange={event => setMetric(event.target.value)}>{["views", "interactions", "followers"].map(name => <option key={name} value={name}>{labels[name]}</option>)}</select></div>
    {valid.length ? <div className="trend-chart"><svg viewBox="0 0 940 278" role="img" aria-label={`แนวโน้ม${labels[metric]} จำนวน ${valid.length} วันที่มีข้อมูล`}><title>แนวโน้ม{labels[metric]} วันที่ไม่มีข้อมูลจะไม่มีเส้นเชื่อม</title>{[0, 0.5, 1].map(fraction => <g key={fraction}><line x1="54" x2="900" y1={getY(max * fraction)} y2={getY(max * fraction)} stroke="#eee8f3" /><text x="42" y={getY(max * fraction) + 4} textAnchor="end">{fmt(max * fraction)}</text></g>)}{segments.map((segment, index) => <path key={index} d={segment} stroke="#8667b1" strokeWidth="3" fill="none" />)}{valid.map(point => <circle key={point.x} cx={getX(point.x)} cy={getY(point.y)} r="3.5" fill="#8667b1"><title>{rows[point.x].date}: {fmt(point.y)}</title></circle>)}<text x="54" y="263">{String(rows[0]?.date ?? "")}</text><text x="900" y="263" textAnchor="end">{String(rows.at(-1)?.date ?? "")}</text></svg><details className="chart-data"><summary>ดูข้อมูลกราฟเป็นตาราง</summary><div className="table-scroll"><table><thead><tr><th>วันที่</th><th>{labels[metric]}</th></tr></thead><tbody>{rows.map((row, index) => <tr key={index}><td>{String(row.date)}</td><td>{fmt(typeof row[metric === "followers" ? "value" : metric] === "number" ? row[metric === "followers" ? "value" : metric] as number : null)}</td></tr>)}</tbody></table></div></details></div> : <div className="chart-empty"><span className="empty-icon">⌁</span><strong>กราฟจะเริ่มจากข้อมูลจริง</strong><p>เชื่อม Meta หรือนำเข้า CSV รายวัน เพื่อเห็นแนวโน้มของช่อง</p></div>}
  </section>;
}

export default function OverviewView({ refresh, notify, onConnect, onImport }: { refresh: number; notify: Notice; onConnect: () => void; onImport: () => void }) {
  const [platform, setPlatform] = useState<Platform>("instagram");
  const [overview, setOverview] = useState<Overview | null>(null);
  const [findings, setFindings] = useState<Findings | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [metric, setMetric] = useState("views");
  const [age, setAge] = useState("0");
  const [kind, setKind] = useState("all");
  const [kinds, setKinds] = useState<string[]>([]);
  const [shown, setShown] = useState(10);
  const [loading, setLoading] = useState(true);
  const [detail, setDetail] = useState<{ title: string; post?: Post; source?: unknown } | null>(null);
  const dialog = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    Promise.all([api<Overview>(`/api/overview?platform=${platform}`), api<Findings>(`/api/findings?platform=${platform}`)])
      .then(([next, result]) => { if (active) { setOverview(next); setFindings(result); } })
      .catch(error => { if (active) notify(error.message, true); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [platform, refresh, notify]);

  useEffect(() => {
    let active = true;
    const query = new URLSearchParams({ platform, metric, age, kind });
    api<{ rows: Post[] }>(`/api/content?${query}`).then(result => { if (active) { setPosts(result.rows); setShown(10); if (kind === "all") setKinds([...new Set(result.rows.map(row => row.media_type))]); } }).catch(error => { if (active) notify(error.message, true); });
    return () => { active = false; };
  }, [platform, metric, age, kind, refresh, notify]);

  useEffect(() => { if (detail && dialog.current && !dialog.current.open) dialog.current.showModal(); }, [detail]);
  const source = useCallback(async (id: string) => { try { setDetail({ title: "หลักฐานจากต้นทาง", source: await api(`/api/source/${encodeURIComponent(id)}`) }); } catch (error) { notify(error instanceof Error ? error.message : "อ่านหลักฐานไม่ได้", true); } }, [notify]);
  const changePlatform = (value: Platform) => { setPlatform(value); setKind("all"); setPosts([]); setOverview(null); };

  return <div className="view">
    <div className="controls"><div className="segmented" aria-label="เลือกแพลตฟอร์ม">{(["instagram", "facebook"] as Platform[]).map(value => <button key={value} className={platform === value ? "active" : ""} aria-pressed={platform === value} onClick={() => changePlatform(value)}>{value === "instagram" ? "Instagram" : "Facebook"}</button>)}</div><span className="muted">{overview ? `${overview.window_start.slice(0, 10)} → ${overview.window_end.slice(0, 10)} · ไม่รวมปลายช่วง` : "30 วันล่าสุด / 30 วันก่อนหน้า"}</span></div>
    {!loading && !overview?.account && <div className="empty-banner"><div><span className="pill">เริ่มต้นจากช่องของเรา</span><h2>รู้จักช่องให้ชัด ก่อนสร้างคลิปใหม่</h2><p>เชื่อมบัญชีเพื่ออ่านโพสต์ Reels และ Insights แล้วค่อยสรุป mood, tone และสไตล์ที่ผู้ชมตอบรับ</p></div><div className="action-stack"><button className="primary" onClick={onConnect}>เชื่อม Facebook + Instagram ↗</button><button className="quiet" onClick={onImport}>มีไฟล์ CSV อยู่แล้ว</button></div></div>}
    {overview && <>
      <div className="account-caption">{overview.account ? `${platform === "instagram" ? "Instagram" : "Facebook"} · ${overview.account.username ? "@" + overview.account.username : overview.account.name}` : "บัญชีแม่หมอกระต่าย · รอการเชื่อมต่อ"}</div>
      <div className="cards">{overview.cards.map(card => {
        const value = card.metric === "followers" ? card.value : card.current?.value;
        const description = card.metric === "followers" ? card.measured_at ? `ข้อมูลถึง ${card.measured_at.slice(0, 10)}` : "รอข้อมูลผู้ติดตาม" : value === null ? `ข้อมูลรายวัน ${card.current?.days ?? 0}/30 วัน · ยังรวมยอดไม่ได้` : `ก่อนหน้า ${fmt(card.previous?.value)}`;
        return <article className="metric-card" key={card.metric}><span className="card-label">{card.label}</span><strong className="card-value">{value === null || value === undefined ? "—" : fmt(value)}</strong><span className="card-detail">{description}</span>{card.change_pct !== null && card.change_pct !== undefined && <span className={`delta ${card.change_pct >= 0 ? "positive" : "negative"}`}>{card.change_pct >= 0 ? "+" : ""}{card.change_pct.toFixed(1)}% เทียบช่วงก่อนหน้า</span>}{card.metric === "followers" && overview.follower_growth_30d !== null && <span className="card-detail">เปลี่ยน {fmt(overview.follower_growth_30d)} ใน 30 วัน</span>}{card.source_id && <button className="source-button" onClick={() => void source(card.source_id!)}>ดูหลักฐาน</button>}</article>;
      })}<article className="metric-card"><span className="card-label">คอนเทนต์ในคลัง</span><strong className="card-value">{fmt(overview.post_count)}</strong><span className="card-detail">จำนวนรายการที่เก็บได้ในบัญชีนี้</span></article></div>
      <Trend overview={overview} />
      <section className="panel"><div className="section-head"><div><h2>คอนเทนต์ที่ควรศึกษาต่อ</h2><p>อันดับใช้ยอดสะสม แสดงอายุโพสต์เพื่อช่วยเทียบอย่างเหมาะสม</p></div><div className="table-controls"><select aria-label="เรียงคอนเทนต์" value={metric} onChange={event => setMetric(event.target.value)}>{["views", "shares", "saves", "comments", "watch_time"].map(value => <option key={value} value={value}>{labels[value]}</option>)}</select><select aria-label="อายุโพสต์" value={age} onChange={event => setAge(event.target.value)}><option value="0">ทุกอายุโพสต์</option>{[7, 30, 90].map(value => <option key={value} value={value}>ไม่เกิน {value} วัน</option>)}</select><select aria-label="รูปแบบคอนเทนต์" value={kind} onChange={event => setKind(event.target.value)}><option value="all">ทุกรูปแบบ</option>{kinds.map(value => <option key={value}>{value}</option>)}</select></div></div>
        <div className="table-scroll"><table><thead><tr><th>คอนเทนต์ / ประโยคเปิด</th><th>รูปแบบ</th><th>อายุโพสต์</th><th>{labels[metric]}{metric !== "watch_time" ? "สะสม" : ""}</th><th>หลักฐาน</th></tr></thead><tbody>{posts.length ? posts.slice(0, shown).map(row => <tr key={row.post_id}><td><div className="post-content-cell"><MediaThumbnail url={row.thumbnail_url || (["IMAGE", "PHOTO"].includes(row.media_type) ? row.media_url : "")} alt={`ภาพจากโพสต์ ${row.hook || row.post_id}`} /><div><span className="post-title">{row.hook || row.post_id}</span><span className="subtext">{row.topic_tags.join(" · ")}</span></div></div></td><td><span className="pill">{row.media_type}</span></td><td>{row.age_days === null ? "ไม่ทราบ" : `${fmt(row.age_days)} วัน`}</td><td>{metric === "watch_time" && row.metrics[metric] ? `${fmt(row.metrics[metric]!.unit === "milliseconds" ? row.metrics[metric]!.value / 1000 : row.metrics[metric]!.value)} วินาที` : fmt(row.ranking_value)}</td><td><button className="source-button" onClick={() => setDetail({ title: "รายละเอียดคอนเทนต์", post: row })}>รายละเอียด ↗</button></td></tr>) : <tr><td colSpan={5}><div className="table-empty">ยังไม่มีคอนเทนต์ในตัวกรองนี้</div></td></tr>}</tbody></table></div><div className="table-summary"><span>แสดง {Math.min(shown, posts.length)} จาก {posts.length} รายการ · ไม่มีข้อมูล = ต้นทางยังไม่ให้ค่านี้</span>{shown < posts.length && <button className="quiet" onClick={() => setShown(count => count + 10)}>ดูเพิ่ม 10 รายการ</button>}</div>
      </section>
      {findings && <div className="two-col"><section className="panel"><h2>หัวข้อคอนเทนต์</h2><Groups rows={findings.content_topics} empty="รอเนื้อหาโพสต์เพื่อเริ่มจัดหมวด" /><p className="footnote">จัดหมวดด้วยคำสำคัญ หนึ่งโพสต์อาจมีหลายหัวข้อ</p></section><section className="panel"><h2>ประเด็นจากคอมเมนต์</h2><Groups rows={findings.comment_themes} empty="ยังไม่มีคอมเมนต์ที่อ่านได้" /><p className="footnote">อ่าน {fmt(findings.comments_analyzed)} คอมเมนต์ · เจ้าของช่องควรตรวจความหมายประกอบ</p></section></div>}
      <details className="panel"><summary>ขอบเขตข้อมูลและข้อจำกัดการอ่าน</summary><div className="coverage">{overview.coverage.length ? overview.coverage.map((row, index) => <div className="coverage-entry" key={index}><strong>{row.status} · {row.endpoint}{row.metric ? ` / ${row.metric}` : ""}</strong><p>{row.detail}</p></div>) : <p className="muted">ยังไม่ได้ตรวจ API หรือยังไม่มีข้อมูลนำเข้า</p>}</div><p className="footnote">รวมยอดเฉพาะช่วงข้อมูลครบตามขอบเขตวัน ไม่รวม reach เป็นคนไม่ซ้ำข้ามแพลตฟอร์ม</p><div className="definitions">{Object.entries(overview.definitions).map(([key, value]) => <p key={key}><strong>{labels[key] || key}:</strong> {value}</p>)}</div></details>
    </>}
    {loading && !overview && <div className="chart-empty">กำลังอ่านข้อมูลช่อง…</div>}
    <dialog ref={dialog} onClose={() => setDetail(null)} className="detail-dialog"><div className="dialog-head"><h2>{detail?.title}</h2><button className="quiet" aria-label="ปิดรายละเอียด" onClick={() => dialog.current?.close()}>×</button></div>{detail?.source !== undefined && <pre className="dialog-code">{JSON.stringify(detail.source, null, 2)}</pre>}{detail?.post && <div><p className="post-copy">{detail.post.text || "ไม่มีคำบรรยาย"}</p><p className="footnote">เผยแพร่ {detail.post.published_at || "ไม่ทราบ"} · อายุ {detail.post.age_days ?? "ไม่ทราบ"} วัน</p>{/^https?:\/\//.test(detail.post.permalink) && <a href={detail.post.permalink} target="_blank" rel="noopener noreferrer">เปิดโพสต์ต้นฉบับ ↗</a>}{Object.entries(detail.post.metrics).filter(([, value]) => value).map(([key, value]) => <div className="source-line" key={key}><span>{labels[key] || key}: {fmt(value!.value)} {value!.unit === "count" ? "" : value!.unit} · {value!.native_metric} · สะสม · เก็บ {value!.observed_at}</span><button className="source-button" onClick={() => void source(value!.source_id)}>ดู snapshot</button></div>)}{detail.post.ranged_metrics.map((value, index) => <div className="source-line" key={index}><span>{labels[value.metric] || value.metric}: {fmt(value.value)} · {value.start_at} → {value.end_at}</span><button className="source-button" onClick={() => void source(value.source_id)}>ดู snapshot</button></div>)}</div>}</dialog>
  </div>;
}
