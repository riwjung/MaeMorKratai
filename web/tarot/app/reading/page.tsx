'use client';
import Link from 'next/link';
import {useEffect, useMemo, useReducer, useRef, useState} from 'react';
import {categories, contexts, suggestions, situations, createReading, initialSession, sessionReducer, shuffleDeck, type Category, type ReadingRequest} from '../../lib/reading';
import {Back, Mascot, ShuffleDeck, Table} from './Table';
import './reading.css';

export default function ReadingPage() {
  const [session, dispatch] = useReducer(sessionReducer, initialSession);
  const [category, setCategory] = useState<Category>('love');
  const [situation, setSituation] = useState<string>(contexts[0]);
  const [question, setQuestion] = useState('');
  const [reduced, setReduced] = useState(false);
  const [error, setError] = useState('');
  const title = useRef<HTMLHeadingElement>(null);
  const stage = session.phase;
  const setup = stage==='topic' || stage==='question';
  const shuffling = stage==='shuffling' || stage==='gathering';
  const categoryLabel = categories.find(c=>c.id===category)!.label;
  const request: ReadingRequest = useMemo(()=>({category,situation,question:question.trim(),spread:'past-present-future'}),[category,situation,question]);
  const result = useMemo(()=>session.unlocked?createReading(request,session.selected):null,[session.unlocked,request,session.selected]);
  useEffect(()=>{
    const media=matchMedia('(prefers-reduced-motion: reduce)');
    const update=()=>setReduced(media.matches);update();media.addEventListener('change',update);
    return ()=>media.removeEventListener('change',update);
  },[]);
  useEffect(()=>{
    title.current?.focus({preventScroll:true});
    if (['topic','question','shuffling','reading'].includes(stage)) window.scrollTo({top:0,behavior:'instant'});
  },[stage]);
  useEffect(()=>{
    if(stage!=='revealing') return;
    const timer=setTimeout(()=>dispatch({type:'NEXT_REVEAL'}),reduced?80:850);
    return ()=>clearTimeout(timer);
  },[stage,session.revealed,reduced]);
  function changeCategory(next:Category) {
    setCategory(next);setSituation(situations[next][0]);
    // Preserve a personal question; discard a suggestion belonging to the previous category.
    if(suggestions[category].includes(question))setQuestion('');
  }
  function start() {
    try {dispatch({type:'START',deck:shuffleDeck()});setError('');}
    catch {setError('เตรียมสำรับไม่สำเร็จ กรุณาลองอีกครั้งในเบราว์เซอร์ที่รองรับ');}
  }
  function reset() {dispatch({type:'RESET'});setQuestion('');setError('');}
  const step=setup?1:shuffling?2:['spreading','selecting'].includes(stage)?3:4;
  const heading=stage==='topic'?'วันนี้มีเรื่องอะไร\nอยู่ในใจคุณ?':stage==='question'?'เล่าให้กระต่ายฟัง\nอีกสักนิด':stage==='shuffling'?'กระต่ายกำลังสับไพ่ให้คุณ':stage==='gathering'?'เก็บคำถามไว้ในใจสักครู่':stage==='spreading'?'ไพ่ของคุณกำลังเรียงตัว':stage==='selecting'?'ให้ความรู้สึกพาคุณเลือก':stage==='revealing'?'ค่อย ๆ เปิดเรื่องราวของคุณ':stage==='locked'?'ไพ่ทั้งสามใบของคุณ': 'เรื่องราวจากไพ่ของคุณ';
  return <main className="ritual" data-phase={stage} data-reduced={reduced}>
    <header className="ritual-header"><Link className="ritual-home" href="/" aria-label="กลับหน้าแรกแม่หมอกระต่าย"><span aria-hidden="true">←</span><span>MaeMorKratai<small>ห้องไพ่ใต้แสงจันทร์</small></span></Link><span className="ritual-edition">THREE CARDS, A LITTLE CLARITY <span aria-hidden="true">✧</span></span></header>
    <div className="ritual-progress" aria-label={`ขั้นตอนที่ ${step} จาก 4`}>
      {['ตั้งคำถาม','สับไพ่','เลือก 3 ใบ','เปิดเรื่องราว'].map((label,i)=><span key={label} aria-current={step===i+1?'step':undefined} className={step>=i+1?'is-active':''}><b>{String(i+1).padStart(2,'0')}</b>{label}</span>)}
    </div>
    {setup ? <section className={'ritual-setup '+(stage==='question'?'is-question':'')}>
      <div className="ritual-conversation">
        {stage==='question' && <button className="ritual-back" onClick={()=>dispatch({type:'TOPIC'})}>← กลับไปเลือกหมวด</button>}
        <p className="ritual-eyebrow">A QUIET MOMENT, JUST FOR YOU</p>
        <h1 ref={title} tabIndex={-1}>{heading}</h1>
        <p className="ritual-intro">{stage==='topic'?'พักความวุ่นวายไว้ข้างนอก แล้วค่อย ๆ เลือกเรื่องที่อยากมองให้ชัดขึ้น':'ไม่ต้องมีคำถามที่สมบูรณ์แบบ แค่เริ่มจากสิ่งที่คุณรู้สึกตอนนี้'}</p>
        {stage==='topic' ? <>
          <div className="ritual-categories" role="group" aria-label="เลือกหมวดคำถาม">{categories.map(c=><button key={c.id} className={category===c.id?'is-selected':''} aria-pressed={category===c.id} onClick={()=>changeCategory(c.id)}><span className="ritual-topic-icon" aria-hidden="true">{c.icon}</span><span><strong>{c.label}</strong><small>{c.hint}</small></span><span className="ritual-topic-check" aria-hidden="true">{category===c.id?'✓':'↗'}</span></button>)}</div>
          <label className="ritual-label" htmlFor="reading-question">หรือเล่าเรื่องที่อยู่ในใจ <span>ไม่บังคับ</span></label>
          <textarea id="reading-question" rows={2} maxLength={600} value={question} onChange={e=>setQuestion(e.target.value)} placeholder="เล่าเรื่องที่อยู่ในใจ…"/>
          {category!=='love' && <p className="ritual-demo-note">ตัวอย่างประสบการณ์ · หมวดนี้ยังรอความรู้จากแม่หมอกระต่าย</p>}
          <button className="ritual-primary ritual-continue" onClick={()=>dispatch({type:'QUESTION'})}>ไปต่อ · {categoryLabel} <span aria-hidden="true">→</span></button>
        </> : <>
          <p className="ritual-category-badge">{categoryLabel}{category!=='love'?' · ตัวอย่างประสบการณ์':''}</p>
          <fieldset className="ritual-situations"><legend>{category==='love'?'ตอนนี้หัวใจของคุณอยู่ตรงไหน?':'ตอนนี้คุณอยากมองเรื่องไหน?'}</legend><div>{situations[category].map(s=><button key={s} type="button" aria-pressed={situation===s} className={situation===s?'is-selected':''} onClick={()=>setSituation(s)}>{s}</button>)}</div></fieldset>
          <label className="ritual-label" htmlFor="detail-question">คำถามของคุณ <span>เว้นว่างแล้วตั้งคำถามในใจได้</span></label>
          <textarea id="detail-question" rows={2} maxLength={600} value={question} onChange={e=>setQuestion(e.target.value)} placeholder="เล่าเรื่องที่อยู่ในใจ…"/>
          <div className="ritual-suggestions"><p>หรือเริ่มจากคำถามนี้</p>{suggestions[category].map(q=><button key={q} aria-pressed={question===q} onClick={()=>setQuestion(q)}>{q}<span aria-hidden="true">↗</span></button>)}</div>
          <button className="ritual-primary ritual-continue" onClick={start}>พร้อมแล้ว ให้กระต่ายสับไพ่ <span aria-hidden="true">✧</span></button>
          {error && <p role="alert" className="ritual-demo-note">{error}</p>}
        </>}
        <p className="ritual-private">ไม่ต้องกรอกชื่อหรือวันเกิด · คำถามอยู่เฉพาะในหน้านี้</p>
      </div>
      <aside className="ritual-welcome-art" aria-label="โลกของแม่หมอกระต่าย"><span className="ritual-art-top">THE MOONLIT ROOM</span><div className="ritual-arch"><img src="/scene/assets/character.jpg" alt="แม่หมอกระต่ายรออยู่ใต้แสงจันทร์"/></div><span className="ritual-art-star" aria-hidden="true">✧</span><div className="ritual-welcome-cards" aria-hidden="true"><Back/><Back/><Back/></div><p>ไพ่สามใบ เรื่องราวหนึ่งเรื่อง</p><small>อดีต · ปัจจุบัน · อนาคต</small></aside>
    </section> : <section className="ritual-experience">
      <Mascot/>
      <p className="ritual-category-badge">{categoryLabel} <span>·</span> {situation}</p>
      <h1 ref={title} tabIndex={-1}>{heading}</h1>
      <p className="ritual-question">{request.question?`“${request.question}”`:'เก็บคำถามไว้ในใจ แล้วเริ่มเมื่อคุณพร้อม'}</p>
      {shuffling ? <>
        <ShuffleDeck stopping={stage==='gathering'} reduced={reduced} onStop={()=>dispatch({type:'STOP'})} onGathered={()=>dispatch({type:'GATHERED'})}/>
        <p className="ritual-shuffle-hint">{stage==='shuffling'?'แตะสำรับเมื่อคุณพร้อม':'กำลังรวมสำรับ แล้วกางไพ่ให้คุณ…'}</p>
        <button className="ritual-primary ritual-stop" disabled={stage==='gathering'} onClick={()=>dispatch({type:'STOP'})}>หยุดสับไพ่ <span aria-hidden="true">✧</span></button>
        {stage==='shuffling'&&<button className="ritual-back" onClick={()=>dispatch({type:'EDIT'})}>← กลับไปแก้คำถาม</button>}
      </> : <>
        <Table session={session} reduced={reduced} onPick={id=>dispatch({type:'PICK',id})} onRemove={id=>dispatch({type:'REMOVE',id})} onReveal={()=>dispatch({type:'REVEAL'})} onSpread={()=>dispatch({type:'SPREAD'})}/>
        {stage==='selecting' && <button className="ritual-back ritual-edit" onClick={()=>dispatch({type:'EDIT'})}>← แก้คำถามและเริ่มสำรับใหม่</button>}
        {stage==='revealing' && <p className="ritual-reveal-status" role="status">เปิดไพ่แล้ว {session.revealed} / 3 ใบ</p>}
        {stage==='locked' && <div className="ritual-unlock"><span className="ritual-unlock-star" aria-hidden="true">✧</span><p className="ritual-eyebrow">YOUR STORY IS READY TO UNFOLD</p><h2>สามช่วงเวลา เชื่อมเป็นเรื่องของคุณ</h2><p>มองความหมายรายใบ แล้วค่อย ๆ อ่านภาพรวมไปด้วยกัน</p><button className="ritual-primary" onClick={()=>dispatch({type:'UNLOCK'})}>ปลดล็อกคำอ่านฉบับเต็ม <span aria-hidden="true">→</span></button><small>ปลดล็อกแบบสาธิต · ไม่มีการชำระเงินจริง</small></div>}
        {result && <section className="ritual-result" aria-label="คำอ่านฉบับเต็ม">
          <p className="ritual-demo-banner">ร่างทดลอง · {category==='love'?'ความหมายรายใบจากคลังเดิมยังรอทบทวน ส่วนการเชื่อมสามช่วงเวลาเป็นตัวอย่าง':'หมวดนี้ยังไม่มีคำอ่านของเจ้าของ แสดงตัวอย่างหน้าผลลัพธ์เท่านั้น'}</p>
          <div className="ritual-reading-entries">{result.entries.map((entry,i)=><article key={entry.id} data-reading-id={entry.id}><span className="ritual-reading-number">0{i+1} / {entry.position}</span><h2>{entry.name}</h2><p>{entry.text}</p>{entry.source&&<details><summary>ที่มาของความหมาย</summary><p>แชทที่เจ้าของให้ · ข้อความ {entry.source.message} · บรรทัด {entry.source.line}<br/>รอเจ้าของทบทวนก่อนเปิดบริการจริง</p></details>}</article>)}</div>
          <article className="ritual-summary"><p className="ritual-eyebrow">THE THREAD BETWEEN YOUR CARDS</p><h2>เมื่อมองไพ่ทั้งสามใบด้วยกัน</h2><p data-testid="reading-summary">{result.summary}</p><div className="ritual-reflection"><span aria-hidden="true">☾</span><div><h3>คำถามเล็ก ๆ ฝากไว้กับคุณ</h3><p>{result.reflection}</p></div></div></article>
          <p className="ritual-result-note">คำถามที่พิมพ์ใช้ประกอบหน้าจอ ต้นแบบยังไม่ได้ตีความข้อความอิสระด้วย AI · ไพ่ชวนทบทวนใจ ไม่ยืนยันอนาคต</p>
          <details className="ritual-knowledge"><summary>เกี่ยวกับคำอ่านชุดนี้</summary><p>รุ่นความรู้ {result.knowledgeVersion} · ไพ่ตั้งตรง · ไม่มีการเก็บประวัติ · การอ่านไพ่ร่วมกันยังรอวิธีตีความจากเจ้าของ</p></details>
        </section>}
        {['locked','reading'].includes(stage) && <button className="ritual-back ritual-new" onClick={reset}>ตั้งคำถามใหม่ แล้วเริ่มอีกครั้ง ↗</button>}
      </>}
    </section>}
    <footer className="ritual-footer"><span>MAEMORKRATAI <span aria-hidden="true">☾</span></span><span>พื้นที่เล็ก ๆ สำหรับฟังใจตัวเอง</span><span>สำรับ 78 ใบ · ประสบการณ์ทดลอง</span></footer>
  </main>;
}
