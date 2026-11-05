'use client';
import {useEffect,useRef,useState} from 'react';
import {Mic,Square,Download,RotateCcw} from 'lucide-react';
export type Take={id:string;blob:Blob;url:string;duration:number};
export default function Recorder({take,onTake,onRecording,disabled}:{take:Take|null;onTake:(t:Take|null)=>void;onRecording:(v:boolean)=>void;disabled:boolean}){
 const [active,setActive]=useState(false),[pending,setPending]=useState(false),[seconds,setSeconds]=useState(0),[error,setError]=useState('');
 const recorder=useRef<MediaRecorder|null>(null),stream=useRef<MediaStream|null>(null),started=useRef(0),mounted=useRef(true),takeRef=useRef(take);takeRef.current=take;
 const stop=()=>{if(recorder.current?.state==='recording')recorder.current.stop()};
 useEffect(()=>{mounted.current=true;return()=>{mounted.current=false;stop();stream.current?.getTracks().forEach(t=>t.stop());if(takeRef.current)URL.revokeObjectURL(takeRef.current.url)}},[]);
 useEffect(()=>{if(!active)return;const id=setInterval(()=>{const n=Math.floor((Date.now()-started.current)/1000);setSeconds(n);if(n>=600)stop()},250);const hidden=()=>{if(document.hidden)stop()};document.addEventListener('visibilitychange',hidden);return()=>{clearInterval(id);document.removeEventListener('visibilitychange',hidden)}},[active]);
 async function start(){
 if(pending||active||disabled)return;
 if(take&&!confirm('มีเสียงที่ยังอยู่ในหน้านี้ บันทึกร่างหรือดาวน์โหลดก่อน หากอัดใหม่เสียงนี้จะถูกแทนที่ เริ่มอัดใหม่ไหม?'))return;
 setError('');if(!window.isSecureContext||!navigator.mediaDevices?.getUserMedia||!window.MediaRecorder){setError('เบราว์เซอร์นี้ยังอัดเสียงไม่ได้ ลองเปิดลิงก์ด้วย Safari หรือ Chrome หรือพิมพ์คำตอบแทนได้');return}
 try{
 setPending(true);onRecording(true);const media=await navigator.mediaDevices.getUserMedia({audio:true});if(!mounted.current){media.getTracks().forEach(t=>t.stop());return}stream.current=media;
 const mime=['audio/webm;codecs=opus','audio/mp4','audio/webm','audio/ogg;codecs=opus'].find(v=>MediaRecorder.isTypeSupported(v));
 const rec=new MediaRecorder(media,mime?{mimeType:mime,audioBitsPerSecond:64000}:undefined);recorder.current=rec;const chunks:BlobPart[]=[];
 rec.ondataavailable=e=>{if(e.data.size)chunks.push(e.data)};
 rec.onstop=()=>{media.getTracks().forEach(t=>t.stop());if(!mounted.current)return;setActive(false);onRecording(false);const blob=new Blob(chunks,{type:rec.mimeType||mime||'audio/webm'});if(!blob.size){setError('ยังไม่ได้รับเสียง กรุณาลองอัดใหม่');return}if(takeRef.current)URL.revokeObjectURL(takeRef.current.url);onTake({id:crypto.randomUUID(),blob,url:URL.createObjectURL(blob),duration:Math.min(600,Math.round((Date.now()-started.current)/1000))})};
 rec.onerror=()=>{setError('การอัดเสียงสะดุด ตรวจเสียงที่ได้ก่อนบันทึก');stop();media.getTracks().forEach(t=>t.stop());setActive(false);onRecording(false)};
 started.current=Date.now();setSeconds(0);rec.start(1000);setActive(true);
 }catch(e){stream.current?.getTracks().forEach(t=>t.stop());setActive(false);onRecording(false);setError(e instanceof DOMException&&e.name==='NotAllowedError'?'ยังไม่ได้อนุญาตไมโครโฟน เปิดสิทธิ์ในเบราว์เซอร์แล้วลองอีกครั้ง หรือพิมพ์คำตอบแทนได้':'เปิดไมโครโฟนไม่สำเร็จ ลองใหม่หรือพิมพ์คำตอบแทนได้')}finally{if(mounted.current)setPending(false)}
 }
 return <div className={'recorder '+(active?'is-recording':'')}>
  <div className="recorder-top"><span className="recorder-icon"><Mic size={22}/></span><div><strong>{active?'กำลังฟังเสียงของคุณ…':'เล่าเหมือนกำลังอ่านให้ลูกดวงฟัง'}</strong><p>{active?'หยุดอัดก่อนสลับแอปหรือพักหน้าจอ':'พูดคำอ่าน เหตุผลจากไพ่ และสิ่งที่ยังสรุปไม่ได้'}</p></div></div>
  <div className="record-controls"><button className={active?'record-stop':'record-start'} disabled={disabled||pending} onClick={active?stop:start}>{active?<Square size={16}/>:take?<RotateCcw size={17}/>:<Mic size={17}/>} {pending?'กำลังเปิดไมโครโฟน…':active?'หยุดอัด':take?'อัดใหม่':'เริ่มอัดเสียง'}</button><span className="timer">{String(Math.floor(seconds/60)).padStart(2,'0')}:{String(seconds%60).padStart(2,'0')}</span><span className="muted small">สูงสุด 10 นาที / ครั้ง</span></div>
  {take&&<div className="local-take"><audio controls src={take.url} preload="metadata"/><div className="take-caption"><span>ฟังตรวจเสียงก่อนบันทึก</span><a href={take.url} download={`คำอ่าน-${take.id}.${take.blob.type.includes('mp4')?'m4a':take.blob.type.includes('ogg')?'ogg':'webm'}`}><Download size={14}/> เก็บเสียงไว้ในเครื่อง</a></div></div>}
  {error&&<p className="error" role="alert">{error}</p>}
 </div>
}
