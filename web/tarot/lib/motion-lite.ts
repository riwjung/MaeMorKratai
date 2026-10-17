// Devices where the filtered SVG scenes (home room, mascot) must stay still: the Safari engine (every iOS
// browser) and touch-first devices re-render them on every animation frame. Mirrors public/scene/controller.js.
export function prefersStillScene(): boolean {
  if (typeof window === 'undefined') return false;
  const ua = navigator.userAgent;
  const webkitEngine = /iP(hone|ad|od)/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1) || (/Safari\//.test(ua) && !/Chrome|Chromium|CriOS|Edg|OPR|Firefox|FxiOS/.test(ua));
  return webkitEngine || matchMedia('(pointer: coarse)').matches;
}

// Card faces are shown at about 150 px; a 600 px WebP is a few percent of the 1.9 MB original, which stays
// the fallback. Built by scripts/make_web_cards.py.
export const webArt = (art: string) => art.replace(/^\/cards\/([\w-]+)\.jpe?g$/, '/cards/web/$1.webp');
