const previewHosts = ["fbcdn.net", "cdninstagram.com", "fbsbx.com"];

/** Only load public, token-free HTTPS media previews from Meta-owned CDNs. */
export function safeMetaMediaURL(value: string | null | undefined) {
  if (!value) return "";
  try {
    const url = new URL(value);
    const allowedHost = previewHosts.some(host => url.hostname === host || url.hostname.endsWith(`.${host}`));
    if (url.protocol !== "https:" || !allowedHost || url.username || url.password || (url.port && url.port !== "443")) return "";
    for (const key of url.searchParams.keys()) if (["access_token", "token"].includes(key.toLowerCase())) return "";
    return url.href;
  } catch { return ""; }
}

export function safePermalink(value: string) {
  try {
    const url = new URL(value);
    if (!["http:", "https:"].includes(url.protocol) || url.username || url.password) return "";
    for (const key of url.searchParams.keys()) if (["access_token", "token"].includes(key.toLowerCase())) return "";
    return url.href;
  } catch { return ""; }
}
