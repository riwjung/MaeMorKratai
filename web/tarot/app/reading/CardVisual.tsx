'use client';
import {useRef, type ReactNode} from 'react';
import {useMotionActivity} from './Motion';
export function Back() {return <img src="/cards/card-back.webp" alt="" draggable={false}/>;}

/** Placement, float and flip each own a transform; drag/GSAP only own the parent. */
export function CardVisual({revealed = false, floating = false, front, still = false}: {revealed?: boolean; floating?: boolean; front?: ReactNode; still?: boolean}) {
  return <div className="ritual-card-visual" data-open={revealed} data-float={floating && !revealed} data-still={still}>
    <div className="ritual-card-bob"><div className="ritual-card-turn ritual-flipper">
      <div className="ritual-card-back" aria-hidden="true"><Back/></div>
      <div className="ritual-card-front" aria-hidden={!revealed}>{front || <Back/>}</div>
      <i className="ritual-card-edge edge-left" aria-hidden="true"/><i className="ritual-card-edge edge-right" aria-hidden="true"/>
      <i className="ritual-card-edge edge-top" aria-hidden="true"/><i className="ritual-card-edge edge-bottom" aria-hidden="true"/>
    </div></div>
  </div>;
}
export function WelcomeCards({motion}: {motion: boolean}) {
  const root = useRef<HTMLDivElement>(null);
  const active = useMotionActivity(root, motion);
  const reset = () => {root.current?.style.setProperty('--lean-x','0deg');root.current?.style.setProperty('--lean-y','0deg');};
  return <div ref={root} className="ritual-welcome-cards" aria-hidden="true" data-motion-active={active}
    onPointerMove={event=>{
      if (!active || event.pointerType !== 'mouse' || !matchMedia('(hover: hover) and (pointer: fine)').matches) return;
      const box=event.currentTarget.getBoundingClientRect();
      const clamp=(n:number)=>Math.max(-5,Math.min(5,n));
      event.currentTarget.style.setProperty('--lean-x',`${clamp(-(event.clientY-box.top-box.height/2)/box.height*10)}deg`);
      event.currentTarget.style.setProperty('--lean-y',`${clamp((event.clientX-box.left-box.width/2)/box.width*10)}deg`);
    }} onPointerLeave={reset}>
    {[0,1,2].map(i=><div className="ritual-welcome-card" key={i}><div className="ritual-card-lean"><CardVisual floating still={!motion}/></div></div>)}
  </div>;
}
