export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.method && options.method !== "GET") headers.set("X-MaeMor-Local", "1");
  const response = await fetch(path, { ...options, headers, cache: "no-store" });
  const result = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(typeof result.detail === "string" ? result.detail : "ทำรายการไม่สำเร็จ");
  return result as T;
}

export function post<T>(path: string, body: unknown = {}) {
  return api<T>(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
}

export const labels: Record<string, string> = { views: "ยอดดู", followers: "ผู้ติดตาม", interactions: "ปฏิสัมพันธ์", shares: "แชร์", saves: "บันทึก", likes: "ถูกใจ", comments: "คอมเมนต์", reactions: "ปฏิกิริยา", watch_time: "เวลารับชมเฉลี่ย" };
export const fmt = (value: number | null | undefined) => value === null || value === undefined ? "ไม่มีข้อมูล" : value.toLocaleString("th-TH", { maximumFractionDigits: 1 });
export const dateText = (value: string | undefined) => value ? new Date(value).toLocaleString("th-TH", { dateStyle: "medium", timeStyle: "short", timeZone: "Asia/Bangkok" }) : "ยังไม่มีข้อมูล";
