'use client';
import {useEffect, useLayoutEffect, useRef, useState, type CSSProperties} from 'react';
import {createPortal} from 'react-dom';
import {cards, placedCards, positions, type Card, type DrawSession} from '../../lib/reading';
import {webArt} from '../../lib/motion-lite';
import {loadReadingMotion, type Motion, type Timeline} from '../../lib/reading-motion';
import {fanArc, FAN_STEP} from './fan';

import {Back, CardVisual} from './CardVisual';
import {useMotionActivity} from './Motion';
export function Face({card}: {card: Card}) {
  // 0 = web-size WebP, 1 = original JPEG, 2 = neither loaded.
  const [attempt, setAttempt] = useState(0);
  const src = card.art && (attempt === 0 ? webArt(card.art) : card.art);
  return src && attempt < 2 ? <img src={src} alt={'ไพ่ '+card.name} onError={()=>setAttempt(a=>a+1)} draggable={false}/> : <div className="ritual-placeholder"><span aria-hidden="true">☾</span><strong>{card.name}</strong><span className="ritual-placeholder-star" aria-hidden="true">✧</span><small>ภาพอยู่ระหว่างจัดทำ</small></div>;
}
const SHUFFLE_CARDS = 24;
const SHUFFLE_PERIOD = 2.4;
// Last on-screen deck box, so the fan can spread out of the spot the deck was gathered in.
let gatheredDeck: DOMRect | null = null;
// One continuous pose per card: the deck splits into two interleaved halves that swing apart and
// riffle back together, with a lag running through the stack. Smooth in t, so there are no
// keyframe stops; t = 0 is the resting stack, so the loop starts from rest.
function shufflePose(i: number, t: number) {
  const u = i / (SHUFFLE_CARDS - 1);
  const side = i % 2 ? 1 : -1;
  const q = Math.PI * 2 * t / SHUFFLE_PERIOD - u * 1.8;
  const open = (1 - Math.cos(Math.max(q, 0))) / 2;
  return {x: side * open * (44 + 32 * u), y: -i * .8 - open * (12 + 24 * u), z: i * 1.2 + open * 14 * u, rotationY: side * open * 34, rotationZ: side * open * (5 + 7 * u), rotationX: 9 * Math.sin(Math.max(q, 0)) * open};
}
// external: the WebGL DeckScene draws and gathers the deck; this button stays the tap target and the anchor it follows.
export function ShuffleDeck({stopping, reduced, external, onStop, onGathered}: {stopping: boolean; reduced: boolean; external: boolean; onStop: ()=>void; onGathered: ()=>void}) {
  const root = useRef<HTMLButtonElement>(null);
  const shadow = useRef<HTMLSpanElement>(null);
  const complete = useRef(onGathered); complete.current = onGathered;
  const [fallback, setFallback] = useState(false);
  useEffect(()=>{
    let cancelled = false;
    let animation: Timeline | undefined;
    const extraAnimations: Timeline[] = [];
    let tick: ((time: number) => void) | undefined;
    let motion: Motion | undefined;
    const deck = root.current;
    const nodes = deck?.querySelectorAll('.ritual-shuffle-card');
    const gathered = ()=>{gatheredDeck = deck?.getBoundingClientRect() || null; complete.current();};
    if (external) return;
    if (reduced) {
      if (nodes) Array.from(nodes).forEach(n => (n as HTMLElement).style.transform = 'none');
      if (deck) deck.style.transform = 'none';
      if (stopping) gathered();
      return;
    }
    loadReadingMotion().then(g => {
      if (cancelled || !nodes || !deck) return;
      motion = g;
      if (stopping) {
        // The ticker was removed with the previous effect, so the rendered pose is kept; gather from it.
        extraAnimations.push(g.to(deck, {rotationY: 0, rotationX: 0, duration: .7, ease: 'power2.inOut'}));
        if (shadow.current) extraAnimations.push(g.to(shadow.current, {scaleX: 1, opacity: 1, duration: .7, ease: 'power2.inOut'}));
        animation = g.to(nodes, {x: 0, y: (i: number)=>-i * .8, z: (i: number)=>i * 1.2, rotationX: 0, rotationY: 0, rotationZ: 0, duration: .7, stagger: {each: .012, from: 'end'}, ease: 'power3.inOut', onComplete: gathered});
      } else {
        const ordered = Array.from(nodes);
        g.set(nodes, {transformPerspective: 950, transformOrigin: '50% 75%'});
        let last: number | undefined, t = 0;
        tick = (time: number) => {
          const box = deck.getBoundingClientRect();
          if (document.hidden || box.bottom < 0 || box.top > innerHeight) {last = undefined; return;}
          if (last !== undefined) t += Math.min(time - last, .1);
          last = time;
          let spread = 0;
          ordered.forEach((node, i) => {const pose = shufflePose(i, t); spread += Math.abs(pose.x); g.set(node, pose);});
          g.set(deck, {rotationY: 11 * Math.sin(Math.PI * 2 * t / 7), rotationX: 6});
          if (shadow.current) g.set(shadow.current, {scaleX: 1 + spread / ordered.length / 70, opacity: 1 - spread / ordered.length / 160});
        };
        g.ticker.add(tick);
      }
    }).catch(()=> {if (!cancelled) {setFallback(true); if (stopping) gathered();}});
    return ()=>{cancelled = true; animation?.kill(); extraAnimations.forEach(a=>a.kill()); if (tick) motion?.ticker.remove(tick);};
  },[stopping,reduced,external]);
  return <div className="ritual-shuffle-stage"><div className="ritual-table-orbit" aria-hidden="true"/><button ref={root} className="ritual-shuffle" onClick={onStop} disabled={stopping} aria-label="แตะสำรับเพื่อหยุดสับไพ่">{external ? <span className="ritual-shuffle-placeholder" aria-hidden="true"><Back/></span> : <><span className="ritual-shuffle-base" aria-hidden="true"/>{Array.from({length:SHUFFLE_CARDS},(_,i)=><span className="ritual-shuffle-card" key={i}><Back/></span>)}</>}</button>{!external && <span ref={shadow} className="ritual-shuffle-shadow" aria-hidden="true"/>}{fallback && <p className="ritual-motion-note">ใช้สำรับแบบนิ่ง · แตะเพื่อเลือกไพ่ได้ตามปกติ</p>}</div>;
}

type Spread = {from: DOMRect; center: number; cards: {i: number; left: number; top: number; width: number; height: number}[]};
// Clones of the visible fan cards travel from the gathered deck, drop onto the middle of the fan and open
// outward into their arc; the real fan stays hidden until they land, so no element changes place visibly.
function SpreadCards({spread, done}: {spread: Spread; done: ()=>void}) {
  const layer = useRef<HTMLDivElement>(null);
  const callback = useRef(done); callback.current = done;
  useEffect(()=>{
    const nodes = Array.from(layer.current?.children || []) as HTMLElement[];
    const {from} = spread;
    const animations = nodes.map((el, n) => {
      const {i, left, top, width, height} = spread.cards[n];
      const arc = fanArc(i);
      const pivot = height * .8; // transform-origin 50% 130% of the real fan card
      const dx = from.left + from.width / 2 - (left + width / 2), dy = from.top + from.height / 2 - (top + height / 2) - i * .25;
      return el.animate([
        {transform: `translate(${dx}px,${dy}px) scale(${from.width / width})`, easing: 'cubic-bezier(.45,0,.25,1)'},
        {transform: `translate(${spread.center - left}px,0px) scale(1)`, offset: .42, easing: 'cubic-bezier(.2,.75,.25,1)'},
        {transform: `translate(0px,${arc.y}px) translateY(${pivot}px) rotate(${arc.r}deg) translateY(${-pivot}px)`},
      ], {duration: 1050, fill: 'both'});
    });
    let live = true;
    Promise.all(animations.map(a=>a.finished)).then(()=>{if (live) callback.current();}, ()=>{});
    return ()=>{live = false; animations.forEach(a=>a.cancel());};
  },[spread]);
  // Portalled: the page section keeps a transform from its entrance animation, which would re-anchor position:fixed.
  return createPortal(<div ref={layer} aria-hidden="true">{spread.cards.map(c=><div key={c.i} className="ritual-spread-card" style={{left:c.left,top:c.top,width:c.width,height:c.height}}><Back/></div>)}</div>, document.body);
}

type Flight = {id: string; from: DOMRect; to: DOMRect; tilt: number};
// Portalled for the same reason as SpreadCards: position:fixed must be relative to the viewport.
function FlyingCard({flight, reduced, done}: {flight: Flight; reduced: boolean; done: ()=>void}) {
  const ref = useRef<HTMLDivElement>(null);
  const callback = useRef(done); callback.current = done;
  useEffect(()=>{
    const el = ref.current;
    if (!el || reduced) {callback.current(); return;}
    const a = el.animate([
      {transform:`translate(0,0) rotate(${flight.tilt}deg)`, opacity:1},
      {transform:`translate(${flight.to.x-flight.from.x}px,${flight.to.y-flight.from.y}px) scale(${flight.to.width/flight.from.width},${flight.to.height/flight.from.height}) rotate(0deg)`, opacity:1},
    ],{duration:flight.tilt ? 550 : 380,easing:'cubic-bezier(.22,.7,.2,1)',fill:'forwards'});
    a.onfinish = ()=>callback.current();
    return ()=>a.cancel();
  },[flight,reduced]);
  return createPortal(<div ref={ref} className="ritual-flight" aria-hidden="true" style={{left:flight.from.x,top:flight.from.y,width:flight.from.width,height:flight.from.height}}><CardVisual still={reduced}/></div>, document.body);
}

// A card picked up from the deck: it follows the pointer until it is dropped on an empty slot or let go.
type Drag = {id: string; pointer: number; width: number; height: number; grabX: number; grabY: number; x: number; y: number; tilt: number; lean: number; time: number};
function DragGhost({drag, ghost, reduced}: {drag: Drag; ghost: React.RefObject<HTMLDivElement | null>; reduced: boolean}) {
  return createPortal(<div ref={ghost} className="ritual-ghost" data-reduced={reduced} aria-hidden="true" style={{width:drag.width,height:drag.height,transform:`translate(${drag.x-drag.grabX}px,${drag.y-drag.grabY}px)`}}><div style={{transform:`rotate(${drag.tilt}deg)`}}><CardVisual still={reduced}/></div></div>, document.body);
}

export function Table({session, reduced, external, onPick, onRemove, onOpen, onReveal, onSpread}: {session: DrawSession; reduced:boolean; external:boolean; onPick:(id:string, slot?:number)=>void; onRemove:(id:string)=>void; onOpen:(slot:number)=>void; onReveal:()=>void; onSpread:()=>void}) {
  const [candidate, setCandidate] = useState<string|null>(null);
  const [grid, setGrid] = useState(false);
  const [flight, setFlight] = useState<Flight|null>(null);
  const [spread, setSpread] = useState<Spread|null>(null);
  const [drag, setDrag] = useState<Drag|null>(null);
  const [target, setTarget] = useState<number|null>(null);
  const wave = useRef(0);
  const root = useRef<HTMLDivElement>(null);
  const motionActive = useMotionActivity(root, !reduced);
  const returnAnimation = useRef<Animation | null>(null);
  const scroller = useRef<HTMLDivElement>(null);
  const ghost = useRef<HTMLDivElement>(null);
  const tap = useRef<{x:number;y:number;scroll:number}|null>(null);
  const press = useRef<{id:string;pointer:number;touch:boolean;x:number;y:number}|null>(null);
  const dragging = useRef<Drag|null>(null);
  const endDrag = useRef<(()=>void)|null>(null);
  const suppressClick = useRef(false);
  const picking = useRef(false);
  const latest = useRef(session); latest.current = session;
  const spreadCallback = useRef(onSpread); spreadCallback.current=onSpread;
  const selecting = session.phase === 'selecting';
  const placed = placedCards(session);
  const full = placed.length === 3;
  const anyOpen = session.opened.some(Boolean);
  const tableOpen = selecting || session.phase === 'spreading';
  useLayoutEffect(()=>{if(scroller.current) scroller.current.scrollLeft=(scroller.current.scrollWidth-scroller.current.clientWidth)/2;},[grid]);
  useLayoutEffect(()=>{
    // Bring the whole fan into view (above the sticky choice bar on phones) while the slots stay on screen,
    // so a card can be dragged from the fan to a slot without scrolling. Runs before the spread is measured.
    if (session.phase !== 'spreading') return;
    const fan = scroller.current?.getBoundingClientRect(), slots = root.current?.querySelector('.ritual-slots')?.getBoundingClientRect();
    const bar = root.current?.querySelector<HTMLElement>('.ritual-choice-bar');
    if (!fan || !slots || !bar) return;
    const floor = innerHeight - (getComputedStyle(bar).position === 'sticky' ? bar.offsetHeight : 0);
    const lift = Math.min(fan.bottom - floor + 8, slots.top - 8);
    if (lift > 0) scrollBy({top: lift, behavior: 'instant'});
  },[session.phase]);
  useLayoutEffect(()=>{
    if (session.phase !== 'spreading' || external) return;
    const view = scroller.current?.getBoundingClientRect();
    const fan = root.current?.querySelector('.ritual-fan')?.getBoundingClientRect();
    const card = root.current?.querySelector<HTMLElement>('.ritual-deck-card');
    if (reduced || !gatheredDeck || !view || !fan || !card) {
      const timer = setTimeout(()=>spreadCallback.current(), reduced ? 0 : 300);
      return ()=>clearTimeout(timer);
    }
    const width = card.offsetWidth, height = card.offsetHeight, cards: Spread['cards'] = [];
    for (let i = 0; i < session.deck.length; i++) {
      const left = fan.left + i * FAN_STEP;
      if (left + width > view.left - 30 && left < view.right + 30) cards.push({i, left, top: fan.top + 10, width, height});
    }
    setSpread({from: gatheredDeck, center: view.left + view.width / 2 - width / 2, cards});
    return ()=>setSpread(null);
  },[session.phase,reduced,session.deck.length,external]);
  function spreadDone() {setSpread(null); spreadCallback.current();}
  // Mouse hover raises a soft wave around the pointer, like lifting cards off the table.
  function liftWave(clientX: number | null) {
    cancelAnimationFrame(wave.current);
    wave.current = requestAnimationFrame(()=>{
      const fan = root.current?.querySelector<HTMLElement>('.ritual-fan');
      if (!fan) return;
      const width = fan.querySelector<HTMLElement>('.ritual-deck-card')?.offsetWidth || 0;
      const at = clientX === null ? -99 : (clientX - fan.getBoundingClientRect().left - width / 2) / FAN_STEP;
      fan.querySelectorAll<HTMLElement>('.ritual-deck-card').forEach((el, i)=>{const d = i - at; el.style.setProperty('--lift', Math.abs(d) < 5 ? (15 * Math.exp(-d * d / 4.5)).toFixed(1) + 'px' : '0px');});
    });
  }
  useEffect(()=>()=>{cancelAnimationFrame(wave.current); endDrag.current?.(); returnAnimation.current?.cancel();},[]);
  useEffect(()=>{
    // Only the placed fronts are warmed; face identities remain hidden in the UI.
    session.slots.forEach(id=>{const card=cards.find(c=>c.id===id);if(card?.art){const image=new Image();image.src=webArt(card.art);}});
  },[session.slots]);
  useEffect(()=>{
    const cancel = () => {
      endDrag.current?.(); dragging.current = null; press.current = null;
      returnAnimation.current?.cancel(); returnAnimation.current = null;
      picking.current = false; setDrag(null); setTarget(null); setFlight(null);
    };
    const key = (event: KeyboardEvent) => {if (event.key === 'Escape') cancel();};
    const visibility = () => {if (document.hidden) cancel();};
    if (reduced) {cancel(); cancelAnimationFrame(wave.current); root.current?.querySelectorAll<HTMLElement>('.ritual-deck-card').forEach(el=>el.style.setProperty('--lift','0px'));}
    addEventListener('resize', cancel); addEventListener('keydown', key);
    document.addEventListener('visibilitychange', visibility);
    return () => {removeEventListener('resize', cancel); removeEventListener('keydown', key); document.removeEventListener('visibilitychange', visibility);};
  },[reduced]);
  const slotCard = (slot: number) => root.current?.querySelector(`[data-slot="${slot}"] .ritual-slot-card`)?.getBoundingClientRect();
  // The empty slot nearest to the dragged card's centre, within a generous margin around each slot.
  function slotAt(x: number, y: number) {
    let best: number | null = null, distance = Infinity;
    latest.current.slots.forEach((id, slot)=>{
      const r = slotCard(slot);
      if (id !== null || !r || x < r.left - r.width * .35 || x > r.right + r.width * .35 || y < r.top - r.height * .4 || y > r.bottom + r.height * .5) return;
      const d = Math.hypot(x - (r.left + r.width / 2), y - (r.top + r.height / 2));
      if (d < distance) {distance = d; best = slot;}
    });
    return best;
  }
  function choose() {
    const slot = session.slots.indexOf(null);
    if (!candidate || !selecting || slot < 0 || picking.current) return;
    const from = root.current?.querySelector(`[data-deck-id="${candidate}"]`)?.getBoundingClientRect();
    const to = slotCard(slot);
    picking.current = true;
    onPick(candidate, slot);
    if (from && to && !reduced) setFlight({id:candidate,from,to,tilt:-7});
    else picking.current = false;
    setCandidate(null);
  }
  function done() {setFlight(null); picking.current=false;}
  function canDrag(id: string) {return selecting && !full && !flight && !picking.current && !dragging.current && !session.slots.includes(id);}
  function startDrag(el: HTMLElement, id: string, pointer: number, x: number, y: number) {
    const from = press.current, box = el.getBoundingClientRect(), width = el.offsetWidth, height = el.offsetHeight;
    const left = box.left + box.width / 2 - width / 2, top = box.top + box.height / 2 - height / 2;
    const picked: Drag = {id, pointer, width, height, grabX: (from?.x ?? x) - left, grabY: (from?.y ?? y) - top, x, y, tilt: grid ? 0 : fanArc(session.deck.indexOf(id)).r, lean: 0, time: performance.now()};
    dragging.current = picked; press.current = null; suppressClick.current = true;
    setDrag(picked); setCandidate(null); liftWave(null);
    try {el.setPointerCapture(pointer);} catch {}
    // Straighten the card as it leaves the fan.
    requestAnimationFrame(()=>{const face = ghost.current?.firstElementChild as HTMLElement | null; if (face) face.style.transform = 'rotate(0deg) scale(1.06)';});
    const move = (event: PointerEvent) => {if (event.pointerId === pointer) follow(event.clientX, event.clientY);};
    const up = (event: PointerEvent) => {if (event.pointerId === pointer) release(event.clientX, event.clientY, true);};
    const cancel = (event: PointerEvent) => {if (event.pointerId === pointer) release(picked.x, picked.y, false);};
    let raf = 0;
    // Near the top edge the page scrolls up, so the slots can be reached from a fan lower on the page.
    const climb = () => {const d = dragging.current; if (!d) return; if (d.y < 70) {scrollBy(0, -(70 - d.y) / 5); follow(d.x, d.y);} raf = requestAnimationFrame(climb);};
    raf = requestAnimationFrame(climb);
    addEventListener('pointermove', move); addEventListener('pointerup', up); addEventListener('pointercancel', cancel);
    endDrag.current = () => {cancelAnimationFrame(raf); removeEventListener('pointermove', move); removeEventListener('pointerup', up); removeEventListener('pointercancel', cancel); endDrag.current = null;};
  }
  function follow(x: number, y: number) {
    const d = dragging.current, el = ghost.current;
    if (!d) return;
    const now = performance.now(), speed = (x - d.x) / Math.max(now - d.time, 8);
    d.lean = reduced ? 0 : d.lean * .7 + Math.max(-9, Math.min(9, speed * 6)) * .3;
    d.x = x; d.y = y; d.time = now;
    if (el) {
      el.style.transform = `translate(${x - d.grabX}px,${y - d.grabY}px)`;
      (el.firstElementChild as HTMLElement | null)?.style.setProperty('transform', `rotate(${d.lean.toFixed(1)}deg) scale(1.06)`);
    }
    setTarget(slotAt(x - d.grabX + d.width / 2, y - d.grabY + d.height / 2));
  }
  function release(x: number, y: number, dropped: boolean) {
    const d = dragging.current;
    endDrag.current?.();
    if (!d) return;
    dragging.current = null;
    setTarget(null);
    const slot = dropped ? slotAt(x - d.grabX + d.width / 2, y - d.grabY + d.height / 2) : null;
    const to = slot === null ? undefined : slotCard(slot);
    if (slot !== null && to) {
      picking.current = true;
      onPick(d.id, slot);
      if (!reduced) setFlight({id: d.id, from: new DOMRect(x - d.grabX, y - d.grabY, d.width, d.height), to, tilt: 0});
      else picking.current = false;
      setDrag(null);
      return;
    }
    // Not over a slot: the card slides back into its place in the deck.
    const home = root.current?.querySelector(`[data-deck-id="${d.id}"]`)?.getBoundingClientRect(), el = ghost.current;
    if (!home || !el || reduced) {setDrag(null); return;}
    picking.current = true;
    const back = el.animate([{transform: `translate(${x - d.grabX}px,${y - d.grabY}px)`}, {transform: `translate(${home.left + home.width / 2 - d.width / 2}px,${home.top + home.height / 2 - d.height / 2}px)`}], {duration: 260, easing: 'cubic-bezier(.3,.7,.3,1)', fill: 'forwards'});
    (el.firstElementChild as HTMLElement | null)?.style.setProperty('transform', `rotate(${d.tilt}deg)`);
    returnAnimation.current = back;
    back.onfinish = () => {returnAnimation.current = null; picking.current = false; setDrag(null);};
  }
  function moveCandidate(key: string) {
    const available = session.deck.filter(id=>!session.slots.includes(id));
    const index = candidate ? available.indexOf(candidate) : -1;
    const target = key === 'Home' ? 0 : key === 'End' ? available.length-1 : Math.max(0,Math.min(available.length-1,index+(key==='ArrowRight'?1:-1)));
    const id = available[target];
    if(id) {setCandidate(id); const button=root.current?.querySelector<HTMLButtonElement>(`[data-deck-id="${id}"]`);button?.focus({preventScroll:true});button?.scrollIntoView({block:'nearest',inline:'center',behavior:'instant'});}
  }
  return <div ref={root} className={'ritual-table '+(session.phase==='spreading'?'is-spreading':'')+(drag?' is-dragging':'')} data-phase={session.phase} data-motion-active={motionActive}>
    <div className="ritual-slots" aria-label="ไพ่ของคุณ อดีต ปัจจุบัน อนาคต">
      {positions.map((position,i)=>{
        const id = session.slots[i]; const card = cards.find(c=>c.id===id); const revealed = session.opened[i];
        const landing = !!flight && flight.id===id;
        return <div className={'ritual-slot'+(drag&&!id?' is-droppable':'')+(target===i?' is-target':'')} key={position} data-slot={i} data-card-id={id || ''}>
          <span className="ritual-position-number">0{i+1}</span>
          <div className={'ritual-slot-card '+(card?'is-filled':'')+(revealed?' is-open':'')} style={{visibility:landing?'hidden':undefined}}>
            {card ? <CardVisual revealed={revealed} floating still={reduced} front={revealed ? <Face key={id} card={card}/> : undefined}/> : <span className={'ritual-slot-empty'+(drag?' is-drop':'')} aria-hidden="true">{drag?'วางที่นี่':'✧'}</span>}
            {card && !revealed && selecting && !landing && <button className="ritual-slot-open" onClick={()=>onOpen(i)} aria-label={'เปิดไพ่ตำแหน่ง'+position}><span>แตะเพื่อเปิด</span></button>}
          </div>
          <p className="ritual-position">{position}</p>
          {revealed && card ? <p className="ritual-card-name">{card.name}</p> : <span className="ritual-slot-note">{i===0?'เรื่องราวที่ผ่านมา':i===1?'สิ่งที่อยู่ตรงหน้า':'แนวโน้มข้างหน้า'}</span>}
          {card && id && !revealed && selecting && <button className="ritual-remove" disabled={!!flight} onClick={()=>{onRemove(id);setCandidate(null);}} aria-label={'นำไพ่ตำแหน่ง'+position+'กลับสำรับ'}>เลือกใหม่ <span aria-hidden="true">↺</span></button>}
        </div>;
      })}
    </div>
    {tableOpen && <>
      <div className="ritual-selection-heading"><p aria-live="polite">{session.phase==='spreading'?'กำลังกางสำรับให้คุณ…':full?'ไพ่ทั้งสามใบพร้อมแล้ว':`เลือกไพ่แล้ว ${placed.length} / 3 ใบ`}</p><span>สำรับเหลือ {78-placed.length} ใบ</span></div>
      <div className="ritual-deck-tools"><span>{grid?'แตะไพ่ แล้วกดเลือกใบนี้':'ลากไพ่ขึ้นไปวางในช่องที่ต้องการ หรือแตะแล้วกดเลือก'}</span><button onClick={()=>setGrid(!grid)} disabled={!!flight || !!drag || !selecting} aria-pressed={grid}>{grid?'กลับมุมมองพัด':'ดูครบทุกใบ'} <span aria-hidden="true">{grid?'⌢':'▦'}</span></button></div>
      <div ref={scroller} className={grid?'ritual-grid-scroll':'ritual-fan-scroll'} aria-label="สำรับไพ่ 78 ใบ" onPointerMove={e=>{if(!reduced&&e.pointerType==='mouse'&&!grid&&selecting&&!dragging.current)liftWave(e.clientX);}} onPointerLeave={()=>{if(!grid)liftWave(null);}} onKeyDown={e=>{if(selecting&&!full&&['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();moveCandidate(e.key);}}}>
        <div className={grid?'ritual-deck-grid':'ritual-fan'+(spread||(external&&session.phase==='spreading')?' is-flying':'')}>
          {session.deck.map((id,i)=>{
            const taken=session.slots.includes(id); const active=candidate===id; const arc=fanArc(i);
            const style={ '--arc-y':`${arc.y}px`, '--arc-r':`${arc.r}deg`, '--card-index':i } as CSSProperties;
            return <button key={id} data-deck-id={id} className={'ritual-deck-card '+(active?'is-candidate':'')+(taken?'is-taken':'')+(drag?.id===id?' is-lifted':'')} style={style} disabled={taken||full||!selecting||!!flight} aria-label={`ไพ่คว่ำใบที่ ${i+1}${taken?' เลือกแล้ว':''}`} aria-pressed={active}
              onPointerDown={e=>{tap.current={x:e.clientX,y:e.clientY,scroll:scroller.current?.scrollLeft||0};suppressClick.current=false;press.current=canDrag(id)&&e.button===0?{id,pointer:e.pointerId,touch:e.pointerType!=='mouse',x:e.clientX,y:e.clientY}:null;}}
              onPointerMove={e=>{
                const p=press.current;
                if(!p||p.pointer!==e.pointerId||dragging.current)return;
                const dx=e.clientX-p.x, dy=e.clientY-p.y;
                // Touch: pulling up (even on a slant toward a side slot) lifts the card, a clearly sideways swipe keeps
                // scrolling the fan. Mouse: any small move.
                const lift=p.touch?(dy<-10&&-dy>Math.abs(dx)*.7)||(Math.abs(dy)>14&&Math.abs(dy)>Math.abs(dx)*1.2):Math.hypot(dx,dy)>6;
                if(lift)startDrag(e.currentTarget,id,e.pointerId,e.clientX,e.clientY);
                else if(p.touch&&Math.abs(dx)>12&&Math.abs(dx)>Math.abs(dy)*1.4)press.current=null;
              }}
              onPointerUp={e=>{press.current=null;const start=tap.current;suppressClick.current=suppressClick.current||(!!start&&(Math.abs(e.clientX-start.x)>9||Math.abs(e.clientY-start.y)>9||Math.abs((scroller.current?.scrollLeft||0)-start.scroll)>9));}}
              onPointerCancel={()=>{press.current=null;suppressClick.current=true;tap.current=null;}}
              onClick={e=>{if(suppressClick.current&&e.detail!==0){suppressClick.current=false;return;}setCandidate(id);}}><CardVisual still={reduced}/>{grid&&<span>{i+1}</span>}</button>;
          })}
        </div>
      </div>
      <div className="ritual-choice-bar"><p aria-live="polite">{full?'แตะไพ่แต่ละใบเพื่อเปิดเอง หรือเปิดพร้อมกัน':candidate?`ไพ่คว่ำใบที่ ${session.deck.indexOf(candidate)+1} · ลากขึ้นไปวาง หรือกดเลือกใบนี้`:'ค่อย ๆ เลือก ไม่ต้องรีบ'}</p>{full?<button className="ritual-primary" disabled={!!flight||!selecting} onClick={onReveal}>{anyOpen?'เปิดใบที่เหลือ':'เปิดไพ่ทั้งสามใบ'} <span aria-hidden="true">✧</span></button>:<button className="ritual-primary" disabled={!candidate||!!flight||!!drag||!selecting} onClick={choose}>เลือกใบนี้ <span aria-hidden="true">↗</span></button>}</div>
    </>}
    {spread && <SpreadCards spread={spread} done={spreadDone}/>}
    {drag && <DragGhost drag={drag} ghost={ghost} reduced={reduced}/>}
    {flight && <FlyingCard flight={flight} reduced={reduced} done={done}/>}
  </div>;
}
