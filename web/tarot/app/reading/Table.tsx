'use client';
import {useEffect, useRef, useState, type CSSProperties} from 'react';
import {cards, positions, type Card, type DrawSession} from '../../lib/reading';
import {loadReadingMotion, type Timeline} from '../../lib/reading-motion';

export function Back(){return <img src="/cards/card-back.svg" alt="" draggable={false}/>;}
export function Mascot(){return <div className="ritual-mascot"><img src="/scene/assets/character.jpg" alt="แม่หมอกระต่ายในหมวกสีม่วง"/><span aria-hidden="true">✧</span></div>;}
export function Face({card}: {card: Card}) {
  const [failed, setFailed] = useState(false);
  return card.art && !failed ? <img src={card.art} alt={'ไพ่ '+card.name} onError={()=>setFailed(true)} draggable={false}/> : <div className="ritual-placeholder"><span aria-hidden="true">☾</span><strong>{card.name}</strong><span className="ritual-placeholder-star" aria-hidden="true">✧</span><small>ภาพอยู่ระหว่างจัดทำ</small></div>;
}
export function ShuffleDeck({stopping, reduced, onStop, onGathered}: {stopping: boolean; reduced: boolean; onStop: ()=>void; onGathered: ()=>void}) {
  const root = useRef<HTMLButtonElement>(null);
  const complete = useRef(onGathered); complete.current = onGathered;
  const [fallback, setFallback] = useState(false);
  useEffect(()=>{
    let cancelled = false;
    let animation: Timeline | undefined;
    const nodes = root.current?.querySelectorAll('.ritual-shuffle-card');
    if (reduced) {
      if (nodes) Array.from(nodes).forEach(n => (n as HTMLElement).style.transform = 'none');
      if (stopping) complete.current();
      return;
    }
    loadReadingMotion().then(g => {
      if (cancelled || !nodes) return;
      if (stopping) {
        // kill() preserves the rendered pose; gather from that pose instead of resetting.
        animation = g.to(nodes, {x: 0, y: 0, z: 0, rotationX: 0, rotationY: 0, rotationZ: 0, duration: .65, stagger: .014, ease: 'power2.inOut', onComplete: ()=>complete.current()});
      } else {
        const ordered = Array.from(nodes);
        g.set(nodes, {transformPerspective: 950, transformOrigin: '50% 70%'});
        animation = g.timeline({repeat: -1});
        ordered.forEach((node,i) => {
          const side = i % 2 ? 1 : -1;
          const lag = i * .035;
          animation!.to(node, {x: side * (52+i*3), y: -34-i*3.5, z: i*3, rotationY: side*38, rotationZ: side*(12+i*.9), rotationX: 16, duration: .85, ease: 'sine.inOut'}, lag);
          animation!.to(node, {x: -side * (42+i*2), y: -18-i*2.5, z: (15-i)*3, rotationY: -side*27, rotationZ: -side*14, rotationX: -9, duration: .9, ease: 'sine.inOut'}, .95+lag);
          animation!.to(node, {x: 0, y: -i*.65, z: 0, rotationY: 0, rotationZ: 0, rotationX: 0, duration: .75, ease: 'sine.inOut'}, 1.95+lag);
        });
      }
    }).catch(()=> {if (!cancelled) {setFallback(true); if (stopping) complete.current();}});
    return ()=>{cancelled = true; animation?.kill();};
  },[stopping,reduced]);
  return <div className="ritual-shuffle-stage"><div className="ritual-table-orbit" aria-hidden="true"/><button ref={root} className="ritual-shuffle" onClick={onStop} disabled={stopping} aria-label="แตะสำรับเพื่อหยุดสับไพ่">{Array.from({length:16},(_,i)=><span className="ritual-shuffle-card" key={i} style={{zIndex:i}}><Back/></span>)}</button><span className="ritual-shuffle-shadow" aria-hidden="true"/>{fallback && <p className="ritual-motion-note">ใช้สำรับแบบนิ่ง · แตะเพื่อเลือกไพ่ได้ตามปกติ</p>}</div>;
}

type Flight = {id: string; from: DOMRect; to: DOMRect};
function FlyingCard({flight, reduced, done}: {flight: Flight; reduced: boolean; done: ()=>void}) {
  const ref = useRef<HTMLDivElement>(null);
  const callback = useRef(done); callback.current = done;
  useEffect(()=>{
    const el = ref.current;
    if (!el || reduced) {callback.current(); return;}
    const a = el.animate([
      {transform:'translate(0,0) rotate(-7deg)', opacity:1},
      {transform:`translate(${flight.to.x-flight.from.x}px,${flight.to.y-flight.from.y}px) scale(${flight.to.width/flight.from.width},${flight.to.height/flight.from.height}) rotate(0deg)`, opacity:1},
    ],{duration:550,easing:'cubic-bezier(.22,.7,.2,1)',fill:'forwards'});
    a.onfinish = ()=>callback.current();
    return ()=>a.cancel();
  },[flight,reduced]);
  return <div ref={ref} className="ritual-flight" aria-hidden="true" style={{left:flight.from.x,top:flight.from.y,width:flight.from.width,height:flight.from.height}}><Back/></div>;
}

export function Table({session, reduced, onPick, onRemove, onReveal, onSpread}: {session: DrawSession; reduced:boolean; onPick:(id:string)=>void; onRemove:(id:string)=>void; onReveal:()=>void; onSpread:()=>void}) {
  const [candidate, setCandidate] = useState<string|null>(null);
  const [grid, setGrid] = useState(false);
  const [flight, setFlight] = useState<Flight|null>(null);
  const root = useRef<HTMLDivElement>(null);
  const scroller = useRef<HTMLDivElement>(null);
  const tap = useRef<{x:number;y:number;scroll:number}|null>(null);
  const suppressClick = useRef(false);
  const picking = useRef(false);
  const spreadCallback = useRef(onSpread); spreadCallback.current=onSpread;
  const selecting = session.phase === 'selecting';
  const full = session.selected.length === 3;
  const tableOpen = selecting || session.phase === 'spreading';
  useEffect(()=>{
    if (session.phase !== 'spreading') return;
    const timer = setTimeout(()=>spreadCallback.current(), reduced ? 0 : 850);
    return ()=>clearTimeout(timer);
  },[session.phase,reduced]);
  useEffect(()=>{if(scroller.current) scroller.current.scrollLeft=(scroller.current.scrollWidth-scroller.current.clientWidth)/2;},[grid]);
  useEffect(()=>{
    // Only the selected fronts are warmed; face identities remain hidden in the UI.
    session.selected.forEach(id=>{const card=cards.find(c=>c.id===id);if(card?.art){const image=new Image();image.src=card.art;}});
  },[session.selected]);
  function choose() {
    if (!candidate || !selecting || full || picking.current) return;
    const from = root.current?.querySelector(`[data-deck-id="${candidate}"]`)?.getBoundingClientRect();
    const to = root.current?.querySelector(`[data-slot="${session.selected.length}"] .ritual-slot-card`)?.getBoundingClientRect();
    picking.current = true;
    onPick(candidate);
    if (from && to && !reduced) setFlight({id:candidate,from,to});
    else picking.current = false;
    setCandidate(null);
  }
  function done() {setFlight(null); picking.current=false;}
  function moveCandidate(key: string) {
    const available = session.deck.filter(id=>!session.selected.includes(id));
    const index = candidate ? available.indexOf(candidate) : -1;
    const target = key === 'Home' ? 0 : key === 'End' ? available.length-1 : Math.max(0,Math.min(available.length-1,index+(key==='ArrowRight'?1:-1)));
    const id = available[target];
    if(id) {setCandidate(id); const button=root.current?.querySelector<HTMLButtonElement>(`[data-deck-id="${id}"]`);button?.focus({preventScroll:true});button?.scrollIntoView({block:'nearest',inline:'center',behavior:'instant'});}
  }
  return <div ref={root} className={'ritual-table '+(session.phase==='spreading'?'is-spreading':'')} data-phase={session.phase}>
    <div className="ritual-slots" aria-label="ไพ่ของคุณ อดีต ปัจจุบัน อนาคต">
      {positions.map((position,i)=>{
        const id = session.selected[i]; const card = cards.find(c=>c.id===id); const revealed = session.revealed > i;
        return <div className="ritual-slot" key={position} data-slot={i} data-card-id={id || ''}>
          <span className="ritual-position-number">0{i+1}</span>
          <div className={'ritual-slot-card '+(card?'is-filled':'')+(revealed?' is-open':'')} style={{visibility:flight && flight.id===id?'hidden':undefined}}>
            {card ? <div className="ritual-flipper"><div className="ritual-card-back"><Back/></div><div className="ritual-card-front" aria-hidden={!revealed}>{revealed&&<Face key={id} card={card}/>}</div></div> : <span className="ritual-slot-empty" aria-hidden="true">✧</span>}
          </div>
          <p className="ritual-position">{position}</p>
          {revealed && card ? <p className="ritual-card-name">{card.name}</p> : <span className="ritual-slot-note">{i===0?'เรื่องราวที่ผ่านมา':i===1?'สิ่งที่อยู่ตรงหน้า':'แนวโน้มข้างหน้า'}</span>}
          {card && selecting && <button className="ritual-remove" disabled={!!flight} onClick={()=>{onRemove(id);setCandidate(null);}} aria-label={'นำไพ่ตำแหน่ง'+position+'กลับสำรับ'}>เลือกใหม่ <span aria-hidden="true">↺</span></button>}
        </div>;
      })}
    </div>
    {tableOpen && <>
      <div className="ritual-selection-heading"><p aria-live="polite">{session.phase==='spreading'?'กำลังกางสำรับให้คุณ…':full?'ไพ่ทั้งสามใบพร้อมแล้ว':`เลือกไพ่แล้ว ${session.selected.length} / 3 ใบ`}</p><span>สำรับเหลือ {78-session.selected.length} ใบ</span></div>
      <div className="ritual-deck-tools"><span>{grid?'แตะไพ่ แล้วกดเลือกใบนี้':'เลื่อนสำรับ แล้วแตะใบที่รู้สึกใช่'}</span><button onClick={()=>setGrid(!grid)} disabled={!!flight || !selecting} aria-pressed={grid}>{grid?'กลับมุมมองพัด':'ดูครบทุกใบ'} <span aria-hidden="true">{grid?'⌢':'▦'}</span></button></div>
      <div ref={scroller} className={grid?'ritual-grid-scroll':'ritual-fan-scroll'} aria-label="สำรับไพ่ 78 ใบ" onKeyDown={e=>{if(selecting&&!full&&['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();moveCandidate(e.key);}}}>
        <div className={grid?'ritual-deck-grid':'ritual-fan'}>
          {session.deck.map((id,i)=>{
            const taken=session.selected.includes(id); const active=candidate===id; const t=(i-38.5)/38.5;
            const style={ '--arc-y':`${t*t*40}px`, '--arc-r':`${t*13}deg`, '--card-index':i } as CSSProperties;
            return <button key={id} data-deck-id={id} className={'ritual-deck-card '+(active?'is-candidate':'')+(taken?'is-taken':'')} style={style} disabled={taken||full||!selecting||!!flight} aria-label={`ไพ่คว่ำใบที่ ${i+1}${taken?' เลือกแล้ว':''}`} aria-pressed={active} onPointerDown={e=>{tap.current={x:e.clientX,y:e.clientY,scroll:scroller.current?.scrollLeft||0};suppressClick.current=false;}} onPointerUp={e=>{const start=tap.current;suppressClick.current=!!start&&(Math.abs(e.clientX-start.x)>9||Math.abs(e.clientY-start.y)>9||Math.abs((scroller.current?.scrollLeft||0)-start.scroll)>9);}} onPointerCancel={()=>{suppressClick.current=true;tap.current=null;}} onClick={e=>{if(suppressClick.current&&e.detail!==0){suppressClick.current=false;return;}setCandidate(id);}}><Back/>{grid&&<span>{i+1}</span>}</button>;
          })}
        </div>
      </div>
      <div className="ritual-choice-bar"><p aria-live="polite">{full?'พร้อมฟังเรื่องราวของไพ่ทั้งสามใบ':candidate?`ไพ่คว่ำใบที่ ${session.deck.indexOf(candidate)+1} · ยังไม่ได้เปิด`:'ค่อย ๆ เลือก ไม่ต้องรีบ'}</p>{full?<button className="ritual-primary" disabled={!!flight||!selecting} onClick={onReveal}>เปิดไพ่ทั้งสามใบ <span aria-hidden="true">✧</span></button>:<button className="ritual-primary" disabled={!candidate||!!flight||!selecting} onClick={choose}>เลือกใบนี้ <span aria-hidden="true">↗</span></button>}</div>
    </>}
    {flight && <FlyingCard flight={flight} reduced={reduced} done={done}/>}
  </div>;
}
