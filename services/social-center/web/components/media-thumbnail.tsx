"use client";

import { useState } from "react";
import { safeMetaMediaURL } from "@/lib/media";

export default function MediaThumbnail({ url, alt, placeholder = false }: { url?: string; alt: string; placeholder?: boolean }) {
  const source = safeMetaMediaURL(url);
  const [failedURL, setFailedURL] = useState("");
  if (!source || failedURL === source) return placeholder ? <div className="preview-unavailable"><span aria-hidden="true">▧</span><small>เปิดโพสต์ต้นทางเพื่อดูภาพ</small></div> : null;
  return <img src={source} alt={alt} loading="lazy" referrerPolicy="no-referrer" onError={() => setFailedURL(source)} />;
}
