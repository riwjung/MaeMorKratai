export type Timeline = {to: (target: unknown, vars: Record<string, unknown>, position?: string | number) => Timeline; kill: () => void};
export type Motion = {
  set: (target: unknown, vars: Record<string, unknown>) => void;
  to: (target: unknown, vars: Record<string, unknown>) => Timeline;
  timeline: (options?: Record<string, unknown>) => Timeline;
};
let loading: Promise<Motion> | undefined;
export function loadReadingMotion(): Promise<Motion> {
  const existing = (window as unknown as {gsap?: Motion}).gsap;
  if (existing) return Promise.resolve(existing);
  if (!loading) loading = new Promise((resolve, reject) => {
    const script = document.createElement('script');
    const timer = setTimeout(() => {loading = undefined; script.remove(); reject(new Error('motion timeout'));}, 6000);
    script.src = '/scene/assets/gsap.min.js';
    script.onload = () => {clearTimeout(timer); resolve((window as unknown as {gsap: Motion}).gsap);};
    script.onerror = () => {clearTimeout(timer); loading = undefined; script.remove(); reject(new Error('motion unavailable'));};
    document.head.append(script);
  });
  return loading;
}
