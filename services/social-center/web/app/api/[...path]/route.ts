import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const gets = new Set(["status", "overview", "content", "findings", "connect/pages", "report/latest", "brand"]);
const posts = new Set(["connect/discover", "connect/select", "connect/verify", "disconnect", "sync", "import/preview", "import", "report", "settings/metrics"]);
const safeQuery = new Set(["platform", "metric", "age", "kind"]);
const maxBody = 21 * 1024 * 1024;

function failure(detail: string, status: number) {
  return NextResponse.json({ detail }, { status, headers: { "Cache-Control": "no-store" } });
}

function isLocalHost(host: string | null) {
  return !!host && /^(127\.0\.0\.1|localhost|\[::1\])(?::\d+)?$/.test(host);
}

function cleanError(value: unknown) {
  if (typeof value !== "string" || value.length > 1000) return "ทำรายการไม่สำเร็จ กรุณาตรวจสถานะการเชื่อมบัญชี";
  // Backend already sanitizes errors. This boundary additionally hides token-like text.
  return value.replace(/EAA[A-Za-z0-9_-]{15,}/g, "[ซ่อน token]")
    .replace(/(access_token|token|secret|authorization)\s*[:=]\s*[^\s,;]+/gi, "$1=[ซ่อน]");
}

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const host = request.headers.get("host");
  if (!isLocalHost(host)) return failure("เปิดระบบนี้จากเครื่อง Mac เท่านั้น", 403);
  if (request.method === "POST") {
    const origin = request.headers.get("origin");
    if (request.headers.get("x-maemor-local") !== "1" || origin !== `http://${host}`) {
      return failure("คำขอนี้ไม่ได้มาจากหน้าระบบบนเครื่อง", 403);
    }
  }
  const { path } = await context.params;
  if (!path.length || path.some(segment => !/^[A-Za-z0-9_-]+$/.test(segment))) {
    return failure("ไม่พบรายการที่ขอ", 404);
  }
  const route = path.join("/");
  const media = path.length === 3 && path[0] === "brand" && path[1] === "media";
  const source = path.length === 2 && path[0] === "source" && /^[A-Za-z0-9_-]+$/.test(path[1]);
  if (request.method === "GET" ? !(gets.has(route) || media || source) : !posts.has(route)) {
    return failure("ไม่พบรายการที่ขอ", 404);
  }
  const backend = new URL(process.env.MAEMOR_API_URL || "http://127.0.0.1:8787");
  if (backend.protocol !== "http:" || !["127.0.0.1", "localhost", "[::1]"].includes(backend.hostname) || backend.username || backend.password) {
    return failure("ที่อยู่ API ต้องเป็นบริการบนเครื่องนี้", 503);
  }
  const upstream = new URL(`/api/${path.map(encodeURIComponent).join("/")}`, backend);
  for (const [key, value] of request.nextUrl.searchParams) {
    if (!safeQuery.has(key) || value.length > 100) return failure("ตัวกรองไม่ถูกต้อง", 400);
    upstream.searchParams.append(key, value);
  }
  const headers = new Headers();
  let body: ArrayBuffer | undefined;
  if (request.method === "POST") {
    if (Number(request.headers.get("content-length")) > maxBody) return failure("ไฟล์ต้องไม่เกิน 20 MB", 413);
    body = await request.arrayBuffer();
    if (body.byteLength > maxBody) return failure("ไฟล์ต้องไม่เกิน 20 MB", 413);
    const contentType = request.headers.get("content-type") || "application/json";
    if (!contentType.startsWith("application/json") && !contentType.startsWith("multipart/form-data;")) {
      return failure("รูปแบบคำขอไม่ถูกต้อง", 415);
    }
    headers.set("Content-Type", contentType);
    headers.set("X-MaeMor-Local", "1");
  }
  if (media && request.headers.get("range")) headers.set("Range", request.headers.get("range")!);
  try {
    const response = await fetch(upstream, { method: request.method, body, headers, cache: "no-store", redirect: "error", signal: AbortSignal.timeout(60_000) });
    if (!response.ok && response.status !== 206) {
      const value = await response.json().catch(() => ({}));
      return failure(cleanError(value.detail), response.status);
    }
    const outgoing = new Headers({ "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" });
    for (const key of ["content-type", "content-length", "content-range", "accept-ranges"]) {
      if (response.headers.get(key)) outgoing.set(key, response.headers.get(key)!);
    }
    return new Response(response.body, { status: response.status, headers: outgoing });
  } catch {
    return failure("ติดต่อบริการข้อมูลบน Mac ไม่ได้ ตรวจว่าบริการ API เปิดอยู่ แล้วลองอีกครั้ง", 503);
  }
}

export const GET = proxy;
export const POST = proxy;
