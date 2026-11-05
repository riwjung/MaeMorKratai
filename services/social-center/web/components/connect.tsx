"use client";

import { useEffect, useState } from "react";
import { api, dateText, post } from "@/lib/api";
import type { Discovery, Status } from "@/lib/types";
import type { Notice } from "./dashboard";

const metricGroups = [
  ["facebook_account_metrics", "Facebook · ภาพรวม"],
  ["facebook_post_metrics", "Facebook · โพสต์"],
  ["instagram_account_metrics", "Instagram · ภาพรวม"],
  ["instagram_post_metrics", "Instagram · โพสต์ / Reels"],
] as const;
const permissionNames = ["pages_show_list", "pages_read_engagement", "read_insights", "instagram_basic", "instagram_manage_insights"];

function record(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === "object" && !Array.isArray(value);
}

function stringValue(value: unknown, fallback: string) {
  return typeof value === "string" && value.length <= 1000 ? value : fallback;
}

const capabilityLabels: Record<string, string> = {
  identity: "ตัวตนบัญชี", content: "โพสต์และ Reels", comments: "คอมเมนต์", insights: "Insights",
};
const resultStatusLabels: Record<string, string> = {
  available: "อ่านได้", empty: "อ่านได้ · ยังไม่มีข้อมูล", not_tested: "ยังไม่ได้ตรวจ",
  permission: "สิทธิ์ยังไม่ครบ", expired: "Token หมดอายุ", rate_limit: "รอแล้วลองใหม่",
  unsupported: "รายการนี้ยังไม่รองรับ", network: "ติดต่อ Meta ไม่ได้", budget: "ครบจำนวนการตรวจรอบนี้",
  response: "ต้องตรวจเพิ่มเติม", mismatch: "บัญชีไม่ตรงกัน", failed: "ยังตรวจไม่ผ่าน",
  verified: "เชื่อมบัญชีสำเร็จ", verified_with_limits: "เชื่อมแล้ว · มีข้อจำกัด", reconnect: "ต้องเชื่อมใหม่",
};

function VerificationResult({ value }: { value: unknown }) {
  if (!record(value)) return <p className="footnote">ยังอ่านผลตรวจไม่ได้ กรุณาตรวจ API อีกครั้ง</p>;
  const state = stringValue(value.status, "unknown");
  const checks = Array.isArray(value.checks) ? value.checks.filter(record) : [];
  const verifiedAt = typeof value.verified_at === "string" && Number.isFinite(Date.parse(value.verified_at)) ? value.verified_at : undefined;
  return <div className="verification-results" aria-live="polite">
    <div className="verification-summary"><span className={`badge ${["verified", "verified_with_limits"].includes(state) ? "ready" : ""}`}>{resultStatusLabels[state] || "ต้องตรวจเพิ่มเติม"}</span><p>{stringValue(value.message, "ตรวจรายการด้านล่างก่อนเริ่มซิงก์ข้อมูล")}</p>{verifiedAt && <small>ยืนยันล่าสุด {dateText(verifiedAt)}</small>}</div>
    {checks.length > 0 && <div className="verification-checks">{checks.map((check, index) => {
      const platform = stringValue(check.platform, "unknown");
      const capability = stringValue(check.capability, "unknown");
      const status = stringValue(check.status, "unknown");
      const available = ["available", "empty"].includes(status);
      return <div className="verification-row" key={index}><div><small>{platform === "facebook" ? "Facebook" : platform === "instagram" ? "Instagram" : "บัญชีช่อง"}</small><strong>{capabilityLabels[capability] || "รายการเพิ่มเติม"}</strong></div><span className={`verification-status ${available ? "success" : "limited"}`}>{resultStatusLabels[status] || "ต้องตรวจเพิ่มเติม"}</span><p>{stringValue(check.detail, "ตรวจการตั้งค่าบัญชีและสิทธิ์ใน Meta")}</p></div>;
    })}</div>}
  </div>;
}

export default function ConnectView({ status, notify, changed }: { status: Status | null; notify: Notice; changed: () => Promise<void> }) {
  const [version, setVersion] = useState("");
  const [discovery, setDiscovery] = useState<Discovery | null>(null);
  const [busy, setBusy] = useState("");
  const [facebookOnly, setFacebookOnly] = useState(false);
  const [metrics, setMetrics] = useState<Record<string, string>>({});
  const [verification, setVerification] = useState<unknown>(null);
  useEffect(() => {
    if (!status) return;
    setVersion(value => value || status.settings.api_version || "");
    setMetrics(Object.fromEntries(metricGroups.map(([key]) => [key, Array.isArray(status.settings[key]) ? (status.settings[key] as string[]).join(", ") : ""])));
  }, [status?.settings.api_version]); // Keep user edits while polling connection status.

  const run = async (name: string, task: () => Promise<void>) => {
    setBusy(name);
    try { await task(); } catch (error) { notify(error instanceof Error ? error.message : "ทำรายการไม่สำเร็จ", true); }
    finally { setBusy(""); }
  };

  const submitToken = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const input = event.currentTarget.elements.namedItem("token") as HTMLInputElement;
    let token = input.value;
    input.value = "";
    void run("discover", async () => {
      try {
        const result = await post<Discovery>("/api/connect/discover", { token, api_version: version });
        setDiscovery(result); setVerification(null);
        notify("Meta รับ token แล้วและเก็บใน Keychain เลือกเพจของแม่หมอกระต่ายด้านล่าง");
        await changed();
      } finally { token = ""; }
    });
  };

  return <div className="view">
    <section className="connection-hero"><div><span className="pill">เริ่มต้น · ยังไม่มี Meta App</span><h2>เชื่อมช่องของคุณทีละขั้น</h2><p>เริ่มที่บัญชีเจ้าของเพจ แล้วกลับมาวาง User Access Token บนหน้านี้<br />เมื่อเลือกเพจแล้ว ระบบจะทดสอบ API ก่อนแสดงว่าเชื่อมสำเร็จ</p></div><div className="connection-state"><span className={`badge ${status?.connected ? "ready" : ""}`}>{status?.connected ? "✓ ตรวจการเชื่อมต่อแล้ว" : status?.configured ? "เลือกบัญชีแล้ว · รอตรวจ" : "ยังไม่เชื่อมบัญชี"}</span><p>{status?.connection?.message || "ต้องสร้าง Meta App และให้สิทธิ์บัญชีเจ้าของก่อน"}</p>{status?.connection?.verified_at && <small>ตรวจล่าสุด {dateText(status.connection.verified_at)}</small>}</div></section>
    <div className="connect-layout"><div>
      <section className="panel"><div className="section-head"><div><span className="eyebrow">เตรียมบัญชี · ทำใน Meta</span><h2>1–4. จากบัญชีช่องถึง User Token</h2></div><span className="pill">ทำครั้งแรก</span></div>
        <ol className="setup-steps">
          <li><span className="step-number">1</span><div><h3>ตรวจสิทธิ์ Facebook และบัญชี Instagram</h3><p>ใช้ Facebook ของคุณหรือแฟนที่มีสิทธิ์จัดการเพจและดู Insights ตรวจ <strong>Page access</strong> ในการตั้งค่าเพจ หากยังไม่มีสิทธิ์ให้เจ้าของเพิ่มบัญชีก่อน</p><p>ใน Instagram → การตั้งค่า → ประเภทบัญชีและเครื่องมือ เปลี่ยน <strong>@maemorkratai</strong> เป็น <strong>Business หรือ Creator</strong> แล้วเชื่อมกับเพจแม่หมอกระต่ายผ่าน Meta Business Suite / Linked accounts</p><a href="https://business.facebook.com/" target="_blank" rel="noopener noreferrer">เปิด Meta Business Suite ↗</a></div></li>
          <li><span className="step-number">2</span><div><h3>สร้าง Meta App ของโครงการ</h3><p>เปิด Meta for Developers → <strong>My Apps → Create App</strong> ตั้งชื่อ “MaeMorKratai Social Insights” และเลือก use case ที่รองรับ Facebook Login และ Instagram API สำหรับ Professional accounts ตามตัวเลือกที่บัญชีแสดง</p><p>เพิ่มบัญชีเจ้าของที่ใช้ทดสอบใน <strong>App roles</strong> และกดยอมรับคำเชิญ ใช้แอปในโหมดพัฒนากับบัญชีที่มีบทบาทก่อน หาก Meta ขอ App Review / Advanced Access / ยืนยันธุรกิจ ให้ทำตามข้อกำหนดที่แสดง</p><a href="https://developers.facebook.com/apps/" target="_blank" rel="noopener noreferrer">สร้าง Meta App ↗</a></div></li>
          <li><span className="step-number">3</span><div><h3>เปิด Graph API Explorer และเลือก App</h3><p>เลือก App ที่เพิ่งสร้าง เลือก <strong>API version ที่ Meta แสดง</strong> แล้วเลือกสร้าง <strong>User Access Token</strong> ด้วย Facebook ของเจ้าของเพจ</p><p>ให้สิทธิ์อ่านที่จำเป็นและเลือกเพจแม่หมอกระต่ายในหน้าขออนุญาต:</p><div className="permission-chips">{permissionNames.map(name => <code key={name}>{name}</code>)}</div><p className="footnote">คอมเมนต์ให้ตรวจ <code>instagram_manage_comments</code> และ <code>pages_read_user_content</code> ตาม endpoint/สิทธิ์ที่ Meta อนุญาต แม้ชื่อบางสิทธิ์มีคำว่า manage ระบบนี้เรียกเฉพาะการอ่านข้อมูล</p><a href="https://developers.facebook.com/tools/explorer/" target="_blank" rel="noopener noreferrer">เปิด Graph API Explorer ↗</a></div></li>
          <li><span className="step-number">4</span><div><h3>วาง token ในหน้าเว็บนี้ แล้วค้นหาเพจ</h3><p>คัดลอก token และ API version มากรอกในฟอร์มด้านข้าง ระบบจะตรวจ Meta และเก็บ token ใน <strong>macOS Keychain</strong> ช่อง token จะถูกล้างทันทีที่ส่ง</p><p>ไม่ต้องส่ง token ผ่านแชต ไม่ต้องเก็บใน Obsidian หาก Mac ขอสิทธิ์ Keychain ให้ตรวจว่าเป็นบริการของโครงการนี้</p></div></li>
        </ol>
      </section>
      <details className="panel"><summary>ถ้าไม่พบเพจ / IG / สิทธิ์ที่ต้องการ</summary><ul className="help-list"><li>ไม่พบเพจ: ตรวจบัญชี Facebook ที่ใช้ สถานะคำเชิญ App roles และ <code>pages_show_list</code> แล้วสร้าง token ใหม่โดยเลือกเพจให้ถูกต้อง</li><li>ไม่พบ Instagram: ตรวจว่าเป็น Professional account และเชื่อมกับเพจที่เลือก เส้นทางนี้ใช้ Facebook Login</li><li>Insights อ่านไม่ได้: ตรวจสิทธิ์ดูข้อมูลของเพจและ <code>read_insights</code> / <code>instagram_manage_insights</code> ดูผลตรวจ API ประกอบ</li><li>Token หมดอายุ: สร้าง User Token ใหม่แล้วส่งผ่านฟอร์ม ระบบจะเปลี่ยนค่าใน Keychain</li><li>อยู่ระหว่าง App Review: นำเข้า CSV จาก Meta Business Suite เพื่อเริ่มดูข้อมูลก่อน</li></ul><a href="https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api" target="_blank" rel="noopener noreferrer">เอกสาร Instagram API ของ Meta ↗</a></details>
    </div><div>
      <section className="panel sticky-panel"><span className="eyebrow">กลับมาทำในเว็บนี้</span><h2>4. ตรวจ token และค้นหาเพจ</h2><form onSubmit={submitToken} autoComplete="off"><label>API version จาก Meta App Dashboard<input name="api_version" value={version} onChange={event => setVersion(event.target.value)} placeholder="vXX.X" pattern="v[0-9]{2}\.[0-9]+" required autoComplete="off" /></label><label>User Access Token<input name="token" type="password" minLength={10} maxLength={8192} required autoComplete="off" spellCheck={false} autoCapitalize="none" data-1p-ignore="true" data-lpignore="true" /></label><p className="footnote">เก็บ token ใน Keychain เท่านั้น · ช่องนี้จะล้างหลังส่ง</p><button className="primary full-width" type="submit" disabled={!!busy}>{busy === "discover" ? "กำลังตรวจ Meta…" : "ตรวจบัญชีและเก็บใน Keychain"}</button></form><button className="quiet full-width" disabled={!!busy || !status?.settings.api_version} onClick={() => void run("pages", async () => { setDiscovery(await api<Discovery>("/api/connect/pages")); })}>ค้นหาเพจจาก token ที่เก็บไว้</button>
        {discovery && <div className="discovery"><h3>5. เลือกเพจของแม่หมอกระต่าย</h3><p className="permission-list">สิทธิ์ที่ Meta ให้: {discovery.permissions.join(", ") || "ยังไม่พบ"}</p>{discovery.pages.length ? discovery.pages.map(page => <div className="page-choice" key={page.id}><strong>{page.name}</strong><p>Page ID: {page.id}</p><p>IG: {page.ig_username ? `@${page.ig_username}` : page.ig_status || "ยังไม่พบ IG ที่เชื่อม"}</p><p>สิทธิ์เพจ: {page.tasks.join(", ") || "ยังไม่พบ"}</p><button className="secondary" disabled={!!busy} onClick={() => void run(`select-${page.id}`, async () => { await post("/api/connect/select", { page_id: page.id, allow_facebook_only: facebookOnly }); setVerification(null); notify("เลือกบัญชีแล้ว กดตรวจ API เพื่อยืนยันข้อมูลที่เข้าถึงได้"); await changed(); })}>ใช้เพจนี้</button></div>) : <p className="muted">ยังไม่พบเพจ ตรวจสิทธิ์และ App roles แล้วลองใหม่</p>}<label className="checkbox"><input type="checkbox" checked={facebookOnly} onChange={event => setFacebookOnly(event.target.checked)} />เริ่มเฉพาะ Facebook หากยังไม่เชื่อม IG</label></div>}
      </section>
      <section className="panel"><h2>6. ตรวจ API แล้วซิงก์ครั้งแรก</h2><p>ตรวจบัญชีที่เลือกและสิทธิ์อ่านข้อมูลจริง เมื่อผ่านแล้วกด “ซิงก์ข้อมูล” ด้านบนเพื่อเก็บโพสต์และสรุปผล</p>{status?.settings.page_name && <p className="selected-account"><strong>{status.settings.page_name}</strong><br />{status.settings.ig_username ? `Instagram @${status.settings.ig_username}` : "Facebook เท่านั้น"}</p>}<button className="secondary full-width" disabled={!status?.configured || !!busy} onClick={() => void run("verify", async () => { const result = await post("/api/connect/verify"); setVerification(result); await changed(); notify("ตรวจ API แล้ว ดูผลและข้อจำกัดด้านล่าง"); })}>{busy === "verify" ? "กำลังตรวจ API…" : "ตรวจการเชื่อมต่อและสิทธิ์อ่าน"}</button>{verification !== null && <VerificationResult value={verification} />}<button className="quiet full-width" disabled={!!busy || !status?.settings.api_version} onClick={() => void run("disconnect", async () => { const result = await post<{ message: string }>("/api/disconnect"); setDiscovery(null); setVerification(null); notify(result.message); await changed(); })}>ลบ token และยกเลิกการเชื่อม</button></section>
    </div></div>
    <details className="panel"><summary>ตั้งค่าตัวชี้วัดสำหรับตรวจ API</summary><p className="footnote">รายการนี้ใช้ลองอ่าน API แต่ละบัญชีอาจรองรับต่างกัน metric ที่ใช้ไม่ได้จะรายงานตามจริง</p><form onSubmit={event => { event.preventDefault(); void run("metrics", async () => { await post("/api/settings/metrics", Object.fromEntries(metricGroups.map(([key]) => [key, (metrics[key] || "").split(",").map(value => value.trim()).filter(Boolean)]))); notify("บันทึกรายการ metric แล้ว ระบบจะตรวจใหม่เมื่อซิงก์"); await changed(); }); }}><div className="two-col">{metricGroups.map(([key, label]) => <label key={key}>{label}<input name={key} value={metrics[key] || ""} onChange={event => setMetrics(values => ({ ...values, [key]: event.target.value }))} /></label>)}</div><button className="secondary" disabled={!!busy || !!status?.sync_running}>บันทึกรายการ</button></form></details>
  </div>;
}
