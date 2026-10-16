'use client';
import {useEffect,useRef,useState} from 'react';
import {createPortal} from 'react-dom';

export type Anchor={x:number;y:number;width:number;height:number};
type Timeline={to:(target:unknown,vars:Record<string,unknown>,position?:number|string)=>Timeline;set:(target:unknown,vars:Record<string,unknown>,position?:number|string)=>Timeline;kill:()=>void};
type Motion={set:(target:unknown,vars:Record<string,unknown>)=>void;timeline:(options?:Record<string,unknown>)=>Timeline};
let loading:Promise<Motion>|undefined;
function loadMotion(){
 if(!loading)loading=new Promise((resolve,reject)=>{
  const script=document.createElement('script');script.src='/scene/assets/gsap.min.js';
  script.onload=()=>resolve((window as unknown as {gsap:Motion}).gsap);
  script.onerror=()=>{loading=undefined;script.remove();reject(new Error('motion unavailable'));};document.head.appendChild(script);
 });return loading;
}
export function CardBack(){return <img className="shared-card-back" src="/cards/card-back.svg" alt="" aria-hidden="true" draggable={false}/>}
export default function CardReveal({card,meaning,context,reduced,getOrigin,onClose,onDetails}:{card:{id:string;name:string;keyword:string};meaning:string;context:string;reduced:boolean;getOrigin:()=>Anchor;onClose:()=>void;onDetails:()=>void}){
 const root=useRef<HTMLDivElement>(null),panel=useRef<HTMLElement>(null),shell=useRef<HTMLDivElement>(null),flip=useRef<HTMLDivElement>(null),veil=useRef<HTMLDivElement>(null),halo=useRef<HTMLDivElement>(null),copy=useRef<HTMLDivElement>(null);
 const closeButton=useRef<HTMLButtonElement>(null),timeline=useRef<Timeline|null>(null),motion=useRef<Motion|null>(null),closing=useRef(false);
 const closeCompletion=useRef<(()=>void)|null>(null);
 const reducedRef=useRef(reduced);reducedRef.current=reduced;
 const [stage,setStage]=useState('opening');const closeAction=useRef<(details?:boolean)=>void>(()=>{});
 closeAction.current=(details=false)=>{
  if(closing.current)return;closing.current=true;setStage('closing');timeline.current?.kill();
  const finish=()=>{if(!closeCompletion.current)return;closeCompletion.current=null;onClose();if(details)requestAnimationFrame(onDetails);};
  closeCompletion.current=finish;
  if(!motion.current||!shell.current||reduced){finish();return;}
  const target=getOrigin(),element=shell.current,parent=element.parentElement!.getBoundingClientRect();
  const width=element.offsetWidth;
  const dx=target.x+target.width/2-(parent.x+element.offsetLeft+width/2),dy=target.y+target.height/2-(parent.y+element.offsetTop+element.offsetHeight/2);
  timeline.current=motion.current.timeline({onComplete:finish});
  timeline.current.to([copy.current,halo.current,root.current?.querySelector('.reveal-stars')],{opacity:0,duration:.18},0)
   .to(flip.current,{rotationY:180,duration:.42,ease:'sine.inOut'},0)
   .to(shell.current,{x:dx,y:dy,scale:Math.max(.06,target.width/width),rotation:0,duration:.65,ease:'power3.inOut'},.08)
   .to(veil.current,{opacity:0,duration:.4},.22);
 };
 useEffect(()=>{
  const previous=document.activeElement as HTMLElement|null;const oldOverflow=document.body.style.overflow;
  const main=document.querySelector('main');const wasInert=main?.inert??false;if(main)main.inert=true;document.body.style.overflow='hidden';closeButton.current?.focus();
  let cancelled=false;
  const keyboard=(e:KeyboardEvent)=>{if(e.key==='Escape'){e.preventDefault();closeAction.current();}if(e.key==='Tab'){
   const nodes=Array.from(panel.current?.querySelectorAll<HTMLElement>('button:not(:disabled),a[href]')??[]);const first=nodes[0],last=nodes[nodes.length-1];
   if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus();}
  }};window.addEventListener('keydown',keyboard);
  loadMotion().then(gsap=>{
   if(cancelled||closing.current||!shell.current)return;motion.current=gsap;
   if(reducedRef.current){setStage('open');return;}
   const dest=shell.current.getBoundingClientRect(),origin=getOrigin();
   gsap.set(shell.current,{visibility:'visible',x:origin.x+origin.width/2-(dest.x+dest.width/2),y:origin.y+origin.height/2-(dest.y+dest.height/2),scale:Math.max(.06,origin.width/dest.width),rotation:-8});
   gsap.set([copy.current,halo.current,veil.current],{opacity:0});gsap.set(halo.current,{scale:.5});gsap.set(flip.current,{rotationY:-180});
   const stars=root.current?.querySelectorAll('.reveal-star');gsap.set(stars,{opacity:0,scale:0});
   timeline.current=gsap.timeline({onComplete:()=>setStage('open')});
   timeline.current.to(veil.current,{opacity:1,duration:.35},0)
    .to(shell.current,{x:0,y:0,scale:1,rotation:0,duration:.9,ease:'power3.inOut'},0)
    .to(flip.current,{rotationY:0,duration:.7,ease:'sine.inOut'},.12)
    .to(halo.current,{opacity:1,scale:1,duration:.75,ease:'sine.out'},.24)
    .to(stars,{opacity:1,scale:1,duration:.65,stagger:.025,ease:'back.out(1.5)'},.38)
    .to(copy.current,{opacity:1,duration:.4},.65);
  }).catch(()=>{if(!cancelled)setStage('open');});
  return()=>{cancelled=true;timeline.current?.kill();window.removeEventListener('keydown',keyboard);document.body.style.overflow=oldOverflow;if(main)main.inert=wasInert;if(previous?.isConnected)previous.focus({preventScroll:true});};
 // Each mount is one reveal. Reopening mounts a new instance; resizing reads the live return anchor.
 // eslint-disable-next-line react-hooks/exhaustive-deps
 },[]);
 useEffect(()=>{
  if(!reduced)return;
  timeline.current?.kill();
  if(closing.current){closeCompletion.current?.();return;}
  const g=motion.current;
  g?.set(shell.current,{x:0,y:0,scale:1,rotation:0,visibility:'visible'});g?.set(flip.current,{rotationY:0});
  g?.set([copy.current,halo.current,veil.current,root.current?.querySelector('.reveal-stars')],{opacity:1});
  g?.set(root.current?.querySelectorAll('.reveal-star'),{opacity:1,scale:1});g?.set(halo.current,{scale:1});setStage('open');
 // Updating the OS preference during a reveal stops movement immediately.
 // eslint-disable-next-line react-hooks/exhaustive-deps
 },[reduced]);
 return createPortal(<div ref={root} className="reveal-layer" data-state={stage} data-card-id={card.id}>
  <div ref={veil} className="reveal-veil" onClick={()=>closeAction.current()} aria-hidden="true"/>
  <section ref={panel} className="reveal-panel" role="dialog" aria-modal="true" aria-labelledby="reveal-title" aria-describedby="reveal-meaning">
   <button ref={closeButton} className="reveal-close" aria-label="ปิดไพ่และเก็บกลับ" onClick={()=>closeAction.current()}>×</button>
   <div className="reveal-art-stage"><div ref={halo} className="reveal-halo" aria-hidden="true"/>
    <div className="reveal-stars" aria-hidden="true">{Array.from({length:16},(_,i)=>{const a=i*Math.PI/8;return <span className={'reveal-star star-color-'+i%3} key={i} style={{left:`${50+Math.cos(a)*(i%2?49:41)}%`,top:`${50+Math.sin(a)*(i%2?47:43)}%`,fontSize:12+(i%4)*5,transform:`rotate(${i*17}deg)`}}>{i%3===0?'·':i%2?'✧':'✦'}</span>;})}</div>
    <div ref={shell} className="reveal-card-shell"><div ref={flip} className="reveal-flipper"><div className="reveal-face reveal-front"><img src={'/cards/'+card.id+'.jpeg'} alt={'ไพ่ '+card.name} draggable={false}/></div><div className="reveal-face reveal-back"><CardBack/></div></div></div>
   </div>
   <div ref={copy} className="reveal-copy"><p className="reveal-kicker">ไพ่ที่เลือกให้คุณ · {context}</p><h2 id="reveal-title">{card.name}</h2><p id="reveal-meaning" className="reveal-meaning">{meaning}</p><button className="reveal-details" onClick={()=>closeAction.current(true)}>อ่านความหมายทั้งหมดด้านล่าง <span aria-hidden="true">↓</span></button><p className="reveal-hint">ปิดแล้วแตะไพ่ เพื่อเปิดดูใบเดิมได้อีกครั้ง</p></div>
  </section>
 </div>,document.body);
}
