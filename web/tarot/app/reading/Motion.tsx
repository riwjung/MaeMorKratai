'use client';
import {useEffect, useRef, useState, type RefObject} from 'react';
import {prefersStillScene} from '../../lib/motion-lite';

/** Decoration sleeps outside the viewport. Ritual state never depends on visibility. */
export function useMotionActivity(ref: RefObject<HTMLElement | null>, enabled: boolean) {
  const [active, setActive] = useState(false);
  useEffect(() => {
    let intersecting = false;
    const update = () => setActive(enabled && intersecting && !document.hidden);
    // One callback can carry several entries when visibility flips quickly; only the latest is current.
    const observer = new IntersectionObserver((entries) => {intersecting = entries[entries.length - 1].isIntersecting; update();});
    if (ref.current) observer.observe(ref.current);
    document.addEventListener('visibilitychange', update);
    update();
    return () => {observer.disconnect(); document.removeEventListener('visibilitychange', update);};
  }, [ref, enabled]);
  return active;
}

export function AnimatedRabbit({size = 'compact', motion = true, reaction = 0}: {size?: 'portrait' | 'compact'; motion?: boolean; reaction?: number}) {
  const root = useRef<HTMLDivElement>(null);
  const frame = useRef<HTMLIFrameElement>(null);
  // Decided after mount: phones and Safari show the still illustration instead of the live filtered scene,
  // which stalls the page there (and is never even downloaded).
  const [scene, setScene] = useState<boolean | null>(null);
  useEffect(() => setScene(!prefersStillScene()), []);
  const active = useMotionActivity(root, motion && scene === true);
  const [ready, setReady] = useState(false);
  const [failed, setFailed] = useState(false);
  const [scale, setScale] = useState(1);
  const activeRef = useRef(active); activeRef.current = active;
  useEffect(() => {
    const el = root.current;
    if (!el) return;
    const resize = new ResizeObserver(() => setScale(Math.max(el.clientWidth / 1000, el.clientHeight / 1100)));
    resize.observe(el);
    return () => resize.disconnect();
  }, []);
  useEffect(() => {
    if (!scene) return;
    const post = () => frame.current?.contentWindow?.postMessage({type: 'mmkt:portrait-motion', playing: activeRef.current}, location.origin);
    const timeout = setTimeout(() => setFailed(true), 8000);
    const receive = (event: MessageEvent) => {
      if (event.origin !== location.origin || event.source !== frame.current?.contentWindow) return;
      if (event.data?.type === 'mmkt:ready') {clearTimeout(timeout); setReady(true); post();}
      if (event.data?.type === 'mmkt:error') {clearTimeout(timeout); setFailed(true);}
    };
    window.addEventListener('message', receive);
    // A cached iframe can finish before React hydrates and installs this listener.
    frame.current?.contentWindow?.postMessage({type:'mmkt:hello'}, location.origin);
    return () => {clearTimeout(timeout); window.removeEventListener('message', receive);};
  }, [scene]);
  useEffect(() => {
    if (ready) frame.current?.contentWindow?.postMessage({type:'mmkt:portrait-motion', playing:active}, location.origin);
  }, [active, ready]);
  return <div ref={root} className={'ritual-rabbit ritual-rabbit--'+size} data-ready={ready && !failed} data-scene={scene === null ? undefined : scene ? 'live' : 'still'} data-motion-active={active} role="img" aria-label="แม่หมอกระต่ายในหมวกสีม่วง">
    <img className="ritual-rabbit-fallback" src="/scene/assets/character.jpg" alt="" draggable={false}/>
    {scene && !failed && <iframe ref={frame} src="/scene/index.html?presentation=portrait" title="ฉากแม่หมอกระต่ายเคลื่อนไหว" tabIndex={-1} aria-hidden="true" style={{transform:`translate(-50%, -50%) scale(${scale})`}} onError={()=>setFailed(true)} onLoad={()=>frame.current?.contentWindow?.postMessage({type:'mmkt:hello'},location.origin)}/>}
    {reaction > 0 && <span key={reaction} className="ritual-rabbit-reaction" aria-hidden="true"/>}
  </div>;
}
