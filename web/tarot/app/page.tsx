'use client';
import Link from 'next/link';
import {useCallback,useEffect,useRef,useState} from 'react';
import CardReveal,{CardBack,type Anchor} from './CardReveal';
import {prefersStillScene} from '../lib/motion-lite';
import cardsData from '../lib/cards.json';
type Card=typeof cardsData[number];
const contexts=['คนโสด','แอบชอบ','คุยกัน','ซับซ้อน','มีแฟน','เลิกกัน'] as const;
type Context=typeof contexts[number];
const source='https://chatgpt.com/share/6ad07301-7314-83ec-bfe4-3793e13fa8b3';
function randomIndex(n:number){const a=new Uint32Array(1);const ceiling=Math.floor(4294967296/n)*n;do{crypto.getRandomValues(a);}while(a[0]>=ceiling);return a[0]%n;}
type DrawVideo={ref:React.RefObject<HTMLVideoElement|null>;on:boolean;onEnded:()=>void};
function Scene({onReady,onReveal,onError,frameRef,cardAnchor,onReopen,drawVideo}:{onReady:()=>void;onReveal:(id:string,anchor?:Anchor)=>void;onError:(s:string)=>void;frameRef:React.RefObject<HTMLIFrameElement|null>;cardAnchor:Anchor|null;onReopen:()=>void;drawVideo:DrawVideo|null}){
 const box=useRef<HTMLDivElement>(null);
 useEffect(()=>{
  const element=box.current;
  // The iframe takes the display size and the scene fits itself inside (?fit=1), so it paints at display resolution.
  const scale=()=>{if(element&&frameRef.current){const w=element.clientWidth;frameRef.current.style.width=w+'px';frameRef.current.style.height=(w*1920/1080)+'px';}};
  const observer=new ResizeObserver(scale);if(element)observer.observe(element);scale();
  const listen=(e:MessageEvent)=>{
   if(e.source!==frameRef.current?.contentWindow||e.origin!==location.origin)return;
   if(e.data?.type==='mmkt:ready')onReady();
   if(e.data?.type==='mmkt:revealed')onReveal(e.data.cardId,e.data.anchor);
   if(e.data?.type==='mmkt:error')onError(e.data.message);
  };window.addEventListener('message',listen);
  frameRef.current?.contentWindow?.postMessage({type:'mmkt:hello'},location.origin);
  return()=>{observer.disconnect();window.removeEventListener('message',listen);};
 },[frameRef,onReady,onReveal,onError]);
 return <div ref={box} className="room-window"><iframe ref={frameRef} src="/scene/index.html?fit=1" title="แม่หมอกระต่ายในห้องปรุงยา สับและเปิดไพ่ให้คุณ" scrolling="no"/>{drawVideo&&<video ref={drawVideo.ref} className={'draw-video'+(drawVideo.on?' is-playing':'')} src="/scene/draw-shuffle.mp4" muted playsInline preload="auto" aria-hidden="true" onEnded={drawVideo.onEnded} onError={drawVideo.onEnded}/>}{cardAnchor&&<button className="hand-card-toggle" aria-label="แตะไพ่ในมือแม่หมอเพื่อเปิดดูอีกครั้ง" onClick={onReopen} style={{left:(cardAnchor.x/1080*100)+'%',top:(cardAnchor.y/1500*100)+'%',width:(cardAnchor.width/1080*100)+'%',height:(cardAnchor.height/1500*100)+'%'}}/>}</div>;
}
export default function Home(){
 const frameRef=useRef<HTMLIFrameElement>(null);
 const active=useRef<Card|null>(null);
 const sourceAnchor=useRef<Anchor|null>(null),resultButton=useRef<HTMLButtonElement>(null);
 const [showReveal,setShowReveal]=useState(false);
 const [ready,setReady]=useState(false),[phase,setPhase]=useState<'idle'|'dealing'|'revealed'>('idle');
 const [context,setContext]=useState<Context>('คนโสด'),[selected,setSelected]=useState<Card|null>(null);
 const [error,setError]=useState(''),[detail,setDetail]=useState<Card|null>(null);
 const [reduced,setReduced]=useState(false),[detailPlaying,setDetailPlaying]=useState(true);
 
 const timer=useRef<ReturnType<typeof setTimeout>|null>(null);
 // Phones and Safari keep the filtered scene still (it runs at a few fps there when animated). For a draw they play
 // the baked shuffle-and-raise video (scripts/build_draw_video.py) while the scene prepares the card; the reveal
 // waits for the video to end and opens from the raised card. The last frame stays up until the dialog closes.
 const [stillScene,setStillScene]=useState(false),[videoOn,setVideoOn]=useState(false);
 const drawVideo=useRef<HTMLVideoElement>(null),videoPlaying=useRef(false),pendingReveal=useRef<[string,Anchor|undefined]|null>(null);
 useEffect(()=>setStillScene(prefersStillScene()),[]);
 useEffect(()=>{const m=matchMedia('(prefers-reduced-motion: reduce)');setReduced(m.matches);const change=()=>setReduced(m.matches);m.addEventListener('change',change);return()=>{m.removeEventListener('change',change);if(timer.current)clearTimeout(timer.current);};},[]);
 const reveal=useCallback((id:string,anchor?:Anchor)=>{if(videoPlaying.current){pendingReveal.current=[id,anchor];return;}if(active.current?.id!==id)return;if(timer.current)clearTimeout(timer.current);if(anchor)sourceAnchor.current=anchor;setSelected(active.current);setPhase('revealed');setShowReveal(true);frameRef.current?.contentWindow?.postMessage({type:'mmkt:card-visibility',visible:false},location.origin);},[]);
 const sceneReady=useCallback(()=>setReady(true),[]);
 function getOrigin():Anchor{
  const frame=frameRef.current?.getBoundingClientRect(),a=sourceAnchor.current;
  if(frame&&a){const scale=frame.width/1080;const result={x:frame.x+a.x*scale,y:frame.y+a.y*scale,width:a.width*scale,height:a.height*scale};if(result.y+result.height>0&&result.y<innerHeight)return result;}
  const button=resultButton.current?.getBoundingClientRect();if(button&&button.y>=0&&button.y<innerHeight)return {x:button.x,y:button.y,width:button.width,height:button.height};
  return {x:innerWidth*.72,y:Math.min(innerHeight-100,innerHeight*.65),width:42,height:68};
 }
 function reopen(){if(!selected||showReveal||phase==='dealing')return;frameRef.current?.contentWindow?.postMessage({type:'mmkt:show',cardId:selected.id},location.origin);}
 function finishVideo(){if(!videoPlaying.current)return;videoPlaying.current=false;const pending=pendingReveal.current;pendingReveal.current=null;if(pending)reveal(pending[0],pending[1]);}
 function closeReveal(){setShowReveal(false);setVideoOn(false);frameRef.current?.contentWindow?.postMessage({type:'mmkt:stow',cardId:active.current?.id},location.origin);}
 function detailsBelow(){document.getElementById('reading-details')?.scrollIntoView({behavior:reduced?'instant':'smooth',block:'start'});}
 const failure=useCallback((s:string)=>{if(timer.current)clearTimeout(timer.current);videoPlaying.current=false;pendingReveal.current=null;setVideoOn(false);setError(s);setPhase('idle');},[]);
 function draw(){
  if(!ready||phase==='dealing'||showReveal)return;
  setError('');setSelected(null);setPhase('dealing');
  const card=cardsData[randomIndex(cardsData.length)];active.current=card;
  const video=stillScene&&!reduced?drawVideo.current:null;
  if(video){videoPlaying.current=true;pendingReveal.current=null;setVideoOn(true);video.currentTime=0;video.play().catch(finishVideo);}
  frameRef.current?.contentWindow?.postMessage({type:'mmkt:draw',cardId:card.id,reducedMotion:reduced},location.origin);
  timer.current=setTimeout(()=>failure('แอนิเมชันยังไม่ตอบกลับ กรุณาลองใหม่อีกครั้ง'),18000);
 }
 useEffect(()=>{
  if(!detail)return;
  const original=document.body.style.overflow;const previousFocus=document.activeElement as HTMLElement|null;document.body.style.overflow='hidden';
  const background=Array.from(document.querySelector('main')?.children??[]).filter(el=>!el.classList.contains('modal-backdrop')) as HTMLElement[];background.forEach(el=>el.inert=true);
  const esc=(e:KeyboardEvent)=>{
   if(e.key==='Escape')setDetail(null);
   if(e.key==='Tab'){const all=Array.from(document.querySelectorAll<HTMLElement>('.card-modal button,.card-modal a[href]'));const first=all[0],last=all[all.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus();}}
  };
  window.addEventListener('keydown',esc);
  return()=>{document.body.style.overflow=original;background.forEach(el=>el.inert=false);window.removeEventListener('keydown',esc);previousFocus?.focus({preventScroll:true});};
 },[detail]);
 return <main>
  <header className="site-header"><a href="#" className="brand"><span className="brand-mark" aria-hidden="true">☾</span><span>MaeMorKratai<small>แม่หมอกระต่าย</small></span></a><nav aria-label="เมนูหลัก"><Link href="/reading/">เปิดไพ่ 3 ใบ →</Link><a href="#reading">เปิดไพ่</a><a href="#collection">สำรับของเรา</a><a href="#about">เรื่องราวของไพ่</a></nav><span className="edition">HALLOWEEN · 2026</span></header>
  <section className="welcome" id="reading" aria-labelledby="intro-title">
   <div className="intro"><p className="eyebrow"><span/> A LITTLE MAGIC, A MOMENT FOR YOU</p>
    <h1 id="intro-title">พักใจสักนิด<br/>แล้วให้ไพ่<br/><em>เล่าเรื่องของคุณ</em></h1>
    <p className="intro-copy">ในคืนที่มีคำถามอยู่ในใจ<br/>แม่หมอกระต่ายจะเปิดไพ่หนึ่งใบให้คุณ<br/>ค่อย ๆ ฟัง แล้วเลือกสิ่งที่อ่อนโยนกับหัวใจ</p>
    <div className="reading-form"><label htmlFor="context">วันนี้อยากมองความรักในมุมไหน</label><select id="context" value={context} disabled={phase==='dealing'} onChange={e=>setContext(e.target.value as Context)}>{contexts.map(s=><option key={s}>{s}</option>)}</select>
    <button className="draw-button" onClick={draw} disabled={!ready||phase==='dealing'}><span aria-hidden="true">✦</span>{!ready?'กำลังเปิดห้องไพ่…':phase==='dealing'?'แม่หมอกำลังสับไพ่…':phase==='revealed'?'ตั้งคำถามใหม่ แล้วเปิดอีกใบ':'ตั้งจิต แล้วเปิดไพ่'}<span aria-hidden="true">↗</span></button>
    <Link className="three-card-entry" href="/reading/"><span>อยากเลือกไพ่ด้วยตัวเอง?</span><strong>เปิดไพ่ 3 ใบ <span aria-hidden="true">→</span></strong></Link><p className="quiet">สำรับทดลอง 5 ใบ · ไม่ต้องกรอกชื่อหรือวันเกิด</p>
    {error&&<p role="alert" className="error">{error}</p>}</div>
    <div className="status" role="status" aria-live="polite">{phase==='dealing'?'ตั้งคำถามไว้ในใจ แม่หมอกำลังเลือกไพ่ให้คุณ':phase==='revealed'?'ไพ่ของคุณเปิดแล้ว อ่านความหมายได้ด้านล่าง':'หายใจลึก ๆ แล้วเริ่มเมื่อคุณพร้อม'}</div>
   </div>
   <div className="stage"><div className="stage-top"><span>THE MOONLIT ROOM</span><span>✧</span></div><Scene cardAnchor={selected&&!showReveal&&!videoOn?sourceAnchor.current:null} onReopen={reopen} frameRef={frameRef} onReady={sceneReady} onReveal={reveal} onError={failure} drawVideo={stillScene&&!reduced?{ref:drawVideo,on:videoOn,onEnded:finishVideo}:null}/><div className="stage-bottom"><span>MAEMORKRATAI</span><small>ห้องไพ่ใต้แสงจันทร์</small>{selected&&<button className="stage-reopen" onClick={reopen} disabled={showReveal} aria-label="เปิดไพ่ใบเดิมจากมือแม่หมอ"><span aria-hidden="true">✦</span> ดูไพ่ของคุณอีกครั้ง</button>}</div><span className="orbit orbit-one" aria-hidden="true">✦</span><span className="orbit orbit-two" aria-hidden="true">✧</span></div>
  </section>
  {selected&&<section id="reading-details" className="reading-result" aria-labelledby="result-title" data-card-id={selected.id}>
   <div className="result-art"><button ref={resultButton} className="result-card-toggle" onClick={reopen} aria-label={'เปิดดูไพ่ '+selected.name+' อีกครั้ง'} aria-expanded={showReveal}><CardBack/><span className="toggle-card-label">แตะเพื่อเปิดไพ่ใบเดิม ✦</span></button><p className="saved-card-note">ไพ่ของคุณยังอยู่ตรงนี้</p></div>
   <div className="result-copy"><p className="eyebrow">YOUR CARD · {context}</p><h2 id="result-title">{selected.name}</h2><p className="keyword">{selected.keyword}</p><div className="fine-line"/><p className="meaning">{selected.meanings[context]}</p><div className="reading-full"><h3>ความหมายในแต่ละสถานะ</h3><dl>{contexts.map(s=><div key={s} className={s===context?'current-context':''}><dt>{s}{s===context&&<span> · ที่คุณเลือก</span>}</dt><dd>{selected.meanings[s]}</dd></div>)}</dl></div><p className="gentle">ลองใช้ไพ่ใบนี้เป็นจุดเริ่มต้นทบทวนความรู้สึกของคุณ คำตอบยังขึ้นอยู่กับการเลือกและการกระทำในชีวิตจริง</p><a className="text-link" href={source} target="_blank" rel="noreferrer">อ่านแหล่งความหมายไพ่ ↗</a></div>
  </section>}
  <section className="collection" id="collection"><div className="section-heading"><div><p className="eyebrow">THE FIRST FIVE</p><h2>ห้าใบแรกจากโลกของแม่หมอกระต่าย</h2></div><p>ตัวละครที่คุ้นเคย ในเรื่องราวที่ต่างกัน<br/>แตะไพ่เพื่อชมภาพและอ่านความหมาย</p></div><div className="card-grid">{cardsData.map((card,i)=><button className="gallery-card" key={card.id} onClick={()=>{setDetail(card);setDetailPlaying(!reduced);}} aria-label={'ดูไพ่ '+card.name}><span className="card-number">0{i+1}</span><img src={'/cards/'+card.id+'.jpeg'} alt="" loading="lazy"/><span className="card-caption">{card.name}<small>{card.keyword}</small></span></button>)}</div></section>
  <section className="about" id="about"><span className="big-moon" aria-hidden="true">☾</span><div><p className="eyebrow">A DECK, WITH A LITTLE HEART</p><h2>ไพ่หนึ่งใบ อาจชวนให้เห็น<br/>หัวใจตัวเองอีกมุม</h2><p>เราเริ่มจากคลังความหมายไพ่ 78 ใบ และทดลองวาด 5 ใบแรกในโลกสีม่วงนุ่ม ๆ ของแม่หมอกระต่าย แต่ละใบอ่านได้ต่างกันตามสถานะความรักของคุณ</p><p className="subtle">ไพ่ใช้เพื่อความบันเทิงและการทบทวนใจ ไม่ใช่คำยืนยันอนาคต ข้อความต้นฉบับยังอยู่ในขั้นทบทวนก่อนเปิดบริการจริง</p><a className="text-link" href={source} target="_blank" rel="noreferrer">คลังความหมายต้นทาง ↗</a></div></section>
  <footer><span>MaeMorKratai <small>แม่หมอกระต่าย</small></span><span>ห้องไพ่ทดลอง · 2026</span><a href="#reading">กลับไปเปิดไพ่ ↑</a></footer>
  {detail&&<div className="modal-backdrop" onClick={()=>setDetail(null)}><section role="dialog" aria-modal="true" aria-labelledby="detail-title" className="card-modal" onClick={e=>e.stopPropagation()}><button className="close" onClick={()=>setDetail(null)} autoFocus aria-label="ปิดรายละเอียดไพ่">×</button><div className={'animated-card generated-card '+(detailPlaying?'card-breathing':'')}><img src={'/cards/'+detail.id+'.jpeg'} alt={'ไพ่ '+detail.name+' ภาพจากสำรับแม่หมอกระต่าย'}/><button className="motion-toggle" onClick={()=>setDetailPlaying(!detailPlaying)}>{detailPlaying?'หยุดภาพเคลื่อนไหว':'เล่นภาพเคลื่อนไหว'}</button></div><div className="card-info"><p className="eyebrow">MAEMORKRATAI · PILOT DECK</p><h2 id="detail-title">{detail.name}</h2><p className="keyword">{detail.keyword}</p><dl>{contexts.map(s=><div key={s}><dt>{s}</dt><dd>{detail.meanings[s]}</dd></div>)}</dl><a className="text-link" href={source} target="_blank" rel="noreferrer">ความหมายจากแชทอ้างอิง ↗</a></div></section></div>}
  {selected&&showReveal&&<CardReveal card={selected} meaning={selected.meanings[context]} context={context} reduced={reduced} getOrigin={getOrigin} onClose={closeReveal} onDetails={detailsBelow}/>}
 </main>;
}
