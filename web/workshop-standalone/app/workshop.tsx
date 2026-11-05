'use client';
import {useCallback,useEffect,useRef,useState} from 'react';
import {ArrowLeft,ArrowRight,Check,CheckCircle2,ChevronDown,Download,LockKeyhole,Mic,RefreshCw,Sparkles,Volume2} from 'lucide-react';
import Recorder,{type Take} from './recorder';
import type {Member} from '../lib/auth';
import {browserClient} from '../lib/supabase-browser';
import {emptyAnswers,type Answers,type Snapshot} from '../lib/domain';
import {categories,categoryLabel} from '../lib/categories';
type Item={id:string;number:number;title:string;category:string;situation:string;stage:string;revision:number};
type Card={id:string;name:string;art:string|null;position:string};
type Recording={id:string;stage:string;duration:number;created_at:string};
type Detail=Item&{question:string;context:string;horizon:string;cards:Card[];snapshot:Snapshot;recordings:Recording[]};
async function api<T>(path='',init?:RequestInit):Promise<T>{const r=await fetch('/api/workshop/'+path,{...init,cache:'no-store'});if(!r.ok){let message='เชื่อมต่อไม่สำเร็จ กรุณาลองใหม่';try{message=((await r.json()) as {error?:string}).error||message}catch{}throw new Error(message)}return r.json()}
const stageLabel=(s:string)=>s==='review'?'ส่งทบทวนแล้ว':s==='followup'?'รออ่านใบขยาย':'อ่าน 3 ใบ';
export default function Workshop({member}:{member:Member}){
 const [reader,setReader]=useState(member.user_id),[members,setMembers]=useState<Member[]>([]),[withdrawals,setWithdrawals]=useState(0);
 const readOnly=reader!==member.user_id,requestRef=useRef<{signature:string;id:string}|null>(null);
 const scoped=useCallback(<T,>(path='')=>api<T>(path+(path.includes('?')?'&':'?')+'reader='+reader),[reader]);
 useEffect(()=>{if(member.role==='owner')void api<{members:Member[];withdrawals:unknown[]}>('members').then(r=>{setMembers(r.members);setWithdrawals(r.withdrawals.length)}).catch(()=>{})},[member.role]);
 async function exportData(){setBusy(true);setError('');try{const data:Record<string,unknown[]>={};for(const table of ['readings','responses','recordings']){data[table]=[];let offset:number|null=0;while(offset!==null){const page:{data:unknown[];next:number|null}=await scoped('export?table='+table+'&offset='+offset);data[table].push(...page.data);offset=page.next;}}const blob=new Blob([JSON.stringify({format:'maemorkratai-workshop-v2',reader,exportedAt:new Date().toISOString(),audio:'Download recordings separately or use the full backup script',...data},null,2)],{type:'application/json'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='workshop-'+reader+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}catch(e){setError((e as Error).message)}finally{setBusy(false)}}
 async function withdraw(){if(prompt('คำขอนี้จะระงับการเข้าถึงคำอ่านของคุณทันที และแจ้งเจ้าของให้ลบข้อมูลและเสียง พิมพ์ ถอน เพื่อยืนยัน')!=='ถอน')return;setBusy(true);try{await api('withdraw',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({confirm:'WITHDRAW'})});location.href='/login'}catch(e){setError((e as Error).message);setBusy(false)}}
 const [items,setItems]=useState<Item[]>([]),[detail,setDetail]=useState<Detail|null>(null),[selected,setSelected]=useState('case-01'),[answers,setAnswers]=useState<Answers>(emptyAnswers),[take,setTake]=useState<Take|null>(null),[consent,setConsent]=useState(false),[dirty,setDirty]=useState(false),[recording,setRecording]=useState(false),[busy,setBusy]=useState(false),[loading,setLoading]=useState(true),[error,setError]=useState(''),[notice,setNotice]=useState(''),[menu,setMenu]=useState(false),[category,setCategory]=useState('all');
 const refresh=useCallback(async()=>{const r=await scoped<{cases:Item[]}>();setItems(r.cases);return r.cases},[scoped]);
 const load=useCallback(async(id:string)=>{setLoading(true);setError('');try{const d=await scoped<Detail>('cases/'+id);setDetail(d);setAnswers(d.snapshot.stage==='baseline'?d.snapshot.baseline:d.snapshot.followup);setTake(null);setDirty(false);setRecording(false);setSelected(id);return true}catch(e){setError((e as Error).message);return false}finally{setLoading(false)}},[scoped]);
 useEffect(()=>{
  let cancelled=false;
  setLoading(true);
  void refresh().then(async list=>{
   if(cancelled)return;
   const params=new URLSearchParams(window.location.search),requested=params.get('category');
   const next=categories.some(c=>c.id===requested)?requested!:'all';
   const matching=list.filter(c=>next==='all'||c.category===next);
   const target=matching.find(c=>c.id===params.get('case'))||matching[0];
   setCategory(next);
   if(target)await load(target.id);else setLoading(false);
  }).catch(e=>{if(!cancelled){setError(e.message);setLoading(false)}});
  return()=>{cancelled=true};
 },[refresh,load]);
 useEffect(()=>{
  if(loading||!detail||detail.id!==selected)return;
  const url=new URL(window.location.href);
  url.searchParams.set('category',category);url.searchParams.set('case',selected);
  window.history.replaceState(null,'',url.pathname+url.search+url.hash);
 },[category,selected,loading,detail?.id]);
 useEffect(()=>{const fn=(e:BeforeUnloadEvent)=>{if(dirty||recording){e.preventDefault();e.returnValue=''}};window.addEventListener('beforeunload',fn);return()=>window.removeEventListener('beforeunload',fn)},[dirty,recording]);
 async function choose(id:string){if(recording||busy||loading)return false;if(dirty&&!confirm('ยังมีคำตอบหรือเสียงที่ไม่ได้บันทึก ต้องการเปลี่ยนเคสและทิ้งสิ่งที่ยังไม่บันทึกไหม?'))return false;setNotice('');setMenu(false);return await load(id)}
 async function chooseCategory(next:string){
  if(busy||recording||loading||next===category)return;
  const matching=items.filter(c=>next==='all'||c.category===next);
  if(!matching.length)return;
  if(matching.some(c=>c.id===selected)){setCategory(next);return}
  if(await choose(matching[0].id))setCategory(next);
 }
 function edit(key:keyof Answers,value:string){setAnswers(a=>({...a,[key]:value}));setDirty(true);setNotice('')}
 async function save(action:'save'|'seal'|'submit'){
 if(!detail||busy||recording||readOnly)return;if(!consent){setError('ติ๊กยืนยันการเก็บคำตอบด้านล่างก่อนบันทึก');return}setBusy(true);setError('');setNotice('');
 try{
 const stage=detail.snapshot.stage;let next=answers;
 if(take){
 if(take.blob.size>16*1024*1024)throw new Error('ไฟล์เสียงใหญ่เกิน 16 MB เก็บเสียงนี้ลงเครื่องแล้วลองอัดให้สั้นลง');
 const mime=take.blob.type.split(';')[0];
 const upload=await api<{ready:boolean;bucket:string;path:string;token:string}>('audio/reserve',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:take.id,caseId:detail.id,stage,mime,bytes:take.blob.size,duration:take.duration,consent:true})});
 if(!upload.ready){const result=await browserClient().storage.from(upload.bucket).uploadToSignedUrl(upload.path,upload.token,take.blob,{contentType:mime});if(result.error)throw new Error('อัปโหลดเสียงไม่สำเร็จ ลองบันทึกอีกครั้ง');await api('audio/complete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:take.id})});}
 next={...answers,audioId:take.id};setAnswers(next)}
 const payload={revision:detail.snapshot.revision,stage,action,answers:next,consent:true},signature=JSON.stringify({caseId:detail.id,...payload});
 if(requestRef.current?.signature!==signature)requestRef.current={signature,id:crypto.randomUUID()};
 const d=await api<Detail>('cases/'+detail.id,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...payload,requestId:requestRef.current.id})});
 setDetail(d);setAnswers(d.snapshot.stage==='baseline'?d.snapshot.baseline:d.snapshot.followup);if(take)URL.revokeObjectURL(take.url);setTake(null);setDirty(false);
 setNotice(action==='seal'?'เก็บคำอ่าน 3 ใบแล้ว ลองดูว่าใบขยายช่วยให้เห็นอะไรเพิ่ม':action==='submit'?'ส่งเคสนี้เข้าคิวทบทวนแล้ว ขอบคุณสำหรับคำอ่านของคุณ':'บันทึกร่างลงฐานข้อมูลแล้ว');
 await refresh().catch(()=>{});
 }catch(e){setError((e as Error).message+' — เก็บเสียงลงเครื่องได้ก่อนลองอีกครั้ง')}finally{setBusy(false)}
 }
 const filtered=items.filter(c=>category==='all'||c.category===category),completed=filtered.filter(c=>c.stage==='review').length,index=filtered.findIndex(c=>c.id===selected),stage=detail?.snapshot.stage,locked=stage==='review'||readOnly;
 return <div className="workshop"><header className="topbar"><a href="/" className="brand"><span className="brand-mark">✧</span><span>แม่หมอกระต่าย<small>READING STUDIO</small></span></a><div className="account-actions"><span className="private-label"><LockKeyhole size={13}/>{member.display_name||'ห้องทดลองส่วนตัว'}</span><form action="/api/auth/signout" method="post"><button className="text-button" disabled={busy||recording}>ออกจากระบบ</button></form></div></header>
 <div className="workspace"><aside className={'sidebar '+(menu?'is-open':'')}><div className="sidebar-heading"><div><span className="eyebrow">สมุดคำอ่านของเรา</span><h2>เรื่องราว {categories.length} หมวด</h2></div><button className="mobile-toggle" aria-expanded={menu} onClick={()=>setMenu(!menu)} aria-label="เปิดรายการเคส"><ChevronDown size={20}/></button></div><div className="category-picker" role="group" aria-label="เลือกหมวดเรื่อง">{[{id:'all',label:'ทุกหมวด'},...categories].map(c=>{const count=items.filter(i=>c.id==='all'||i.category===c.id).length;return <button type="button" key={c.id} aria-pressed={category===c.id} aria-label={c.label+' '+count+' เคส'} className={'category-choice '+(c.id==='all'?'all-categories':'')} disabled={busy||recording||loading||!count} onClick={()=>chooseCategory(c.id)}><span>{c.label}</span><small>{count}</small></button>})}</div><div className="progress-copy"><span>{categoryLabel(category)} · ส่งทบทวนแล้ว</span><b>{completed} <span>/ {filtered.length} เคส</span></b></div><div className="progress-track"><span style={{width:(filtered.length?completed/filtered.length*100:0)+'%'}}/></div><nav className="case-list" aria-label="รายการเคส">{filtered.map(c=><button key={c.id} className={'case-item '+(selected===c.id?'selected':'')} disabled={busy||recording||loading} onClick={()=>choose(c.id)}><span className={'case-number '+(c.stage==='review'?'complete':'')}>{c.stage==='review'?<Check size={16}/>:String(c.number).padStart(2,'0')}</span><span><strong>{c.title}</strong><small>{categoryLabel(c.category)} · {c.situation} · {c.revision?stageLabel(c.stage):'ยังไม่เริ่ม'}</small></span>{c.id===selected&&<span className="selected-dot"/>}</button>)}</nav><div className="sidebar-footer"><p>สถานการณ์สมมติสำหรับเก็บวิธีอ่าน<br/>คำตอบทุกเคสยังรอทบทวนก่อนนำไปใช้</p>{member.role==='owner'?<><label className="field">เปิดดูคำอ่านของ<select aria-label="ผู้บันทึก" value={reader} disabled={busy||recording} onChange={e=>{if(dirty&&!confirm('มีสิ่งที่ยังไม่ได้บันทึก เปลี่ยนผู้บันทึกไหม?'))return;setReader(e.target.value)}}><option value={member.user_id}>สมุดของฉัน</option>{members.filter(m=>m.active&&m.user_id!==member.user_id).map(m=><option key={m.user_id} value={m.user_id}>{m.display_name||'ผู้บันทึก'}</option>)}</select></label><button className="text-button" disabled={busy||recording} onClick={exportData}><Download size={14}/> ส่งออกข้อความและรายการเสียง</button><small>ดาวน์โหลดเสียงจากแต่ละเคสได้<br/>สำรองครบทั้งไฟล์เสียงด้วยเครื่องมือของเจ้าของ</small>{withdrawals>0&&<p className="error">มีคำขอถอนความยินยอม {withdrawals} รายการ รอเจ้าของดำเนินการลบ</p>}</>:<button className="text-button" disabled={busy||recording} onClick={withdraw}>ถอนความยินยอมและขอลบข้อมูล</button>}</div></aside>
 <main className="main">{member.role==='owner'&&<div className="banner review-banner"><a href="/review" onClick={e=>{if((dirty||recording)&&!confirm('มีร่างหรือเสียงที่ยังไม่บันทึก จะออกไปหน้าตรวจไหม?'))e.preventDefault()}}>ตรวจคำอ่านและสำนวน →</a><p>ขั้นต่อไปหลังตอบครบ · ตรวจ 40 เคสเดิมและรับรองฉบับที่ต้องการใช้</p></div>}<div className="intro"><div><span className="eyebrow">เก็บความรู้จากเสียงของแม่หมอ</span><h1>อ่านในแบบของคุณ</h1><p>ค่อย ๆ อ่าน ค่อย ๆ เล่า ไม่ต้องเตรียมคำตอบให้สมบูรณ์ในครั้งเดียว</p></div><span className="intro-sparkle" aria-hidden="true">✧</span></div>
 {error&&<div className="error banner" role="alert">{error}<button className="text-button" disabled={busy||recording} onClick={()=>choose(selected)}><RefreshCw size={14}/> โหลดเคสใหม่</button></div>}
 {readOnly&&<div className="banner review-banner">กำลังอ่านสมุดของผู้ทดลอง · ดูได้อย่างเดียว</div>}
 {notice&&<div className="success banner" role="status"><CheckCircle2 size={18}/>{notice}</div>}
 {loading?<div className="loading" role="status">กำลังเปิดสมุดคำอ่าน…</div>:detail&&<div key={detail.id}>
 <section className="scenario panel"><div className="case-meta"><span className="pill">เคส {String(detail.number).padStart(2,'0')}</span><span className="category-tag">{categoryLabel(detail.category)}</span><span>{detail.situation}</span><span>ช่วงเวลา: {detail.horizon}</span></div><h2>{detail.question}</h2><p>{detail.context}</p>{detail.category==='health'&&<p className="category-hint">ชวนทบทวนการพักผ่อน ความเครียด และการดูแลตัวเอง · ไม่ใช้ไพ่วินิจฉัยโรคหรือเลือกการรักษา</p>}<div className="scenario-foot"><span>โจทย์สมมติ · ไพ่ตั้งตรงทุกใบ</span><span>{stageLabel(stage||'baseline')}</span></div></section>
 <ol className="steps" aria-label="ขั้นตอน"><li className={stage==='baseline'?'current':'done'}><span>{stage!=='baseline'?<Check size={14}/>:1}</span>อ่าน 3 ใบ</li><li className={stage==='followup'?'current':locked?'done':''}><span>{locked?<Check size={14}/>:2}</span>เปิดใบขยาย</li><li className={locked?'current':''}><span>3</span>ส่งทบทวน</li></ol>
 <section className="cards-section" aria-label="ไพ่ในเคส"><div className="section-title"><h3>{stage==='baseline'?'ไพ่ 3 ใบแรก':'ไพ่ของเคสนี้'}</h3><span>{stage==='baseline'?'อ่านก่อนเห็นใบที่ 4':'ใบที่ 4 ใช้ขยายใบอนาคต'}</span></div><div className="cards-grid">{detail.cards.map((c,i)=><article className={'tarot '+(i===3?'clarifier':'')} key={c.id}><span className="card-position">{String(i+1).padStart(2,'0')} · {c.position}</span><div className="card-face">{c.art?<img src={c.art} alt={c.name}/>:<div className="card-symbolic"><span aria-hidden="true">{c.id.includes('cups')?'♧':c.id.includes('swords')?'†':c.id.includes('pentacles')?'✥':c.id.includes('wands')?'❧':'✧'}</span><strong>{c.name}</strong><small>ชื่อไพ่ · ยังไม่มีภาพ</small></div>}</div><h4>{c.name}</h4></article>)}{stage==='baseline'&&<article className="tarot locked-card"><span className="card-position">04 · ขยายอนาคต</span><div className="card-face"><LockKeyhole size={24}/><p>เก็บคำอ่าน 3 ใบ<br/>ก่อนเปิดใบนี้</p><span aria-hidden="true">✦</span></div><h4>ใบขยาย</h4></article>}</div></section>
 {stage!=='baseline'&&<details className="baseline-saved panel"><summary><CheckCircle2 size={18}/> คำอ่าน 3 ใบแรกที่เก็บไว้ <ChevronDown size={17}/></summary><p className="muted small">เก็บต้นฉบับก่อนเห็นใบขยายไว้แล้ว</p>{detail.snapshot.baseline.audioId&&<audio controls src={'/api/workshop/audio/'+detail.snapshot.baseline.audioId}/>}<AnswerView value={detail.snapshot.baseline}/></details>}
 <section className="answer-section panel"><div className="section-title"><div><span className="eyebrow">{locked?'ต้นฉบับคำอ่าน':stage==='baseline'?'ขั้นที่ 1 · ก่อนเห็นใบขยาย':'ขั้นที่ 2 · หลังเห็นใบขยาย'}</span><h2>{readOnly?'คำอ่านที่บันทึกไว้':locked?'เก็บเคสนี้เรียบร้อยแล้ว':stage==='baseline'?'จาก 3 ใบนี้ คุณจะบอกลูกดวงว่า…':'ใบขยายช่วยให้เห็นอะไรเพิ่ม?'}</h2></div><Mic size={24} className="muted"/></div>
 {locked?<><p className="muted">คำอ่านอยู่ในคิวทบทวน ยังไม่นำไปตอบลูกค้าอัตโนมัติ</p>{answers.audioId&&<audio controls src={'/api/workshop/audio/'+answers.audioId}/>}<AnswerView value={answers}/></>:<>
 <Recorder key={detail.id+stage} take={take} onTake={t=>{setTake(t);setDirty(true);setNotice('')}} onRecording={setRecording} disabled={busy}/>
 {!take&&answers.audioId&&<div className="saved-audio"><span><Volume2 size={15}/> เสียงที่บันทึกไว้</span><audio controls src={'/api/workshop/audio/'+answers.audioId}/></div>}
 <label className="field">{stage==='baseline'?'คำอ่านฉบับข้อความ':'คำอ่านหลังเห็นใบขยาย'} <span>พิมพ์แทนเสียง หรือจดเพิ่มก็ได้</span><textarea rows={4} value={answers.answer} onChange={e=>edit('answer',e.target.value)} disabled={busy} placeholder="เล่าด้วยคำที่คุณใช้จริงกับลูกดวง…" maxLength={12000}/></label>
 {stage==='followup'&&<div className="field-pair"><label className="field">ส่วนไหนชัดขึ้นหรือเปลี่ยนไป?<textarea rows={3} value={answers.changes} onChange={e=>edit('changes',e.target.value)} disabled={busy} placeholder="เชื่อมใบขยายกับใบอนาคตอย่างไร" maxLength={12000}/></label><label className="field">ส่วนไหนยังเหมือนเดิม?<textarea rows={3} value={answers.unchanged} onChange={e=>edit('unchanged',e.target.value)} disabled={busy} placeholder="สิ่งที่ใบขยายไม่ได้เปลี่ยนคำอ่าน" maxLength={12000}/></label></div>}
 <details className="notes"><summary>จดเหตุผลและสำนวนเพิ่มเติม <span>ถ้าเล่าในเสียงแล้ว ข้ามได้</span><ChevronDown size={16}/></summary><label className="field">ไพ่ใบไหน / ตำแหน่งไหน ทำให้อ่านแบบนี้?<textarea rows={3} value={answers.evidence} onChange={e=>edit('evidence',e.target.value)} disabled={busy} maxLength={12000}/></label><div className="field-pair"><label className="field">จากไพ่เท่านี้ ยังสรุปอะไรไม่ได้?<textarea rows={3} value={answers.uncertainty} onChange={e=>edit('uncertainty',e.target.value)} disabled={busy} maxLength={12000}/></label><label className="field">อยากถามลูกดวงเพิ่มว่าอะไร?<textarea rows={3} value={answers.question} onChange={e=>edit('question',e.target.value)} disabled={busy} maxLength={12000}/></label></div><label className="field">คำพูดที่อยากให้เป็นสำนวนของเรา<textarea rows={2} value={answers.phrases} onChange={e=>edit('phrases',e.target.value)} disabled={busy} maxLength={12000}/></label></details>
 <label className="consent"><input type="checkbox" checked={consent} onChange={e=>setConsent(e.target.checked)} disabled={busy}/><span>ยินยอมให้เก็บเสียงและคำตอบนี้ในห้องทดลองส่วนตัว เพื่อพัฒนาวิธีอ่านและสำนวนแม่หมอกระต่าย ใช้ข้อมูลสมมติ ไม่กล่าวชื่อหรือข้อมูลลูกค้าจริง</span></label>
 <div className="save-state" aria-live="polite">{busy?'กำลังบันทึกเสียงและคำตอบ…':recording?'กำลังอัดเสียง — หยุดก่อนบันทึก':dirty?'มีการแก้ไขที่ยังไม่ได้บันทึก':detail.snapshot.updatedAt?'บันทึกล่าสุด '+new Date(detail.snapshot.updatedAt).toLocaleString('th-TH'):'ยังไม่มีคำตอบที่บันทึก'}</div>
 <div className="actions"><button className="secondary" onClick={()=>save('save')} disabled={busy||recording}>บันทึกร่าง</button><button className="primary" onClick={()=>save(stage==='baseline'?'seal':'submit')} disabled={busy||recording||(!answers.answer.trim()&&!answers.audioId&&!take)}>{busy?'กำลังบันทึก…':stage==='baseline'?'เก็บคำอ่าน แล้วเปิดใบที่ 4':'บันทึกและส่งทบทวน'}<ArrowRight size={16}/></button></div>
 {stage==='baseline'&&<p className="footnote">เมื่อเปิดใบขยาย คำอ่าน 3 ใบแรกจะถูกเก็บเป็นต้นฉบับและแก้ทับไม่ได้</p>}
 </>}
 </section>
 {detail.recordings.length>0&&<details className="history panel"><summary><Volume2 size={16}/> เสียงที่บันทึกทั้งหมด ({detail.recordings.length})<ChevronDown size={16}/></summary><p className="muted small">อัดใหม่แล้วเสียงเดิมยังอยู่ เลือกฟังหรือดาวน์โหลดเก็บได้</p>{detail.recordings.map(r=><div key={r.id} className="history-row"><span>{r.stage==='baseline'?'ก่อนเห็นใบขยาย':'หลังเห็นใบขยาย'} · {new Date(r.created_at).toLocaleString('th-TH')}</span><audio controls preload="none" src={'/api/workshop/audio/'+r.id}/><a href={'/api/workshop/audio/'+r.id+'?download=1'} download>ดาวน์โหลดเสียง</a></div>)}</details>}
 <div className="case-navigation"><button className="text-button" disabled={index<=0||busy||recording||loading} onClick={()=>choose(filtered[index-1].id)}><ArrowLeft size={16}/> เคสก่อนหน้า</button><span>{index+1} / {filtered.length} · {categoryLabel(category)}</span><button className="text-button" disabled={index<0||index>=filtered.length-1||busy||recording||loading} onClick={()=>choose(filtered[index+1].id)}>เคสถัดไป <ArrowRight size={16}/></button></div>
 <p className="page-note"><Sparkles size={14}/> เสียงต้นฉบับเก็บแยกจากข้อความ · ยังไม่มีการถอดเสียงหรือสร้างคำอ่านด้วย AI</p>
 </div>}
 </main></div></div>
}
function AnswerView({value}:{value:Answers}){const labels:Record<string,string>={answer:'คำอ่าน',evidence:'เหตุผลจากไพ่',uncertainty:'สิ่งที่ยังสรุปไม่ได้',question:'คำถามเพิ่มเติม',phrases:'สำนวน',changes:'สิ่งที่ชัดขึ้นหรือเปลี่ยนไป',unchanged:'สิ่งที่ยังเหมือนเดิม'};return <div className="answer-view">{Object.entries(labels).filter(([key])=>value[key as keyof Answers]).map(([key,label])=><div key={key}><strong>{label}</strong><p>{value[key as keyof Answers]}</p></div>)}</div>}
