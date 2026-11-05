from pathlib import Path
import json,shutil,html
P=Path(__file__).resolve().parent.parent;O=P/'overlay';A=O/'assets'
old=Path('/Users/sawettachatsuthum/AIVideoLocal/maemorkratai/content/lovers-paris/video-projects/claude-cut-v1/overlay/assets')
shutil.copy2(old/'gsap.min.js',A/'gsap.min.js');(A/'fonts').mkdir(exist_ok=True);shutil.copy2(old/'fonts/Kanit-ExtraBold.ttf',A/'fonts/Kanit-ExtraBold.ttf')
for f in (P/'assets/narrator').glob('*.png'):shutil.copy2(f,A/f.name)
pieces=json.loads((P/'timing/pieces.json').read_text());cues=json.loads((P/'timing/mouth-cues.json').read_text())['mouthCues']
texts=[['คุณเป็นคนประเภทเดอะฟูล|ในที่ทำงานรึเปล่าคะ'],['ถ้าใช่ ไม่แย่เลยนะ|คนแบบนี้แพ้ยากที่สุดในออฟฟิศ'],['เพราะเขาทำงานแบบเป็นตัวเอง|ไม่เรื่องมาก อยากทำก็ทำ'],['ไม่สนกระแสใครว่า|แต่พอมีเทรนด์ใหม่','กลับไหลไปกับมันได้|อย่างแนบเนียน'],['สนุกของเขาไม่ใช่อู้งานนะคะ','แต่คือจดจ่อจนลืมดูนาฬิกา'],['ต่างจากผู้ใหญ่หลายคน|ที่ชอบนั่งจิบกาแฟ'],['มองลงมาจากบนหอคอย'],['มองคนข้างล่าง|ปล้ำกับกองงานยักษ์อย่างบ้าคลั่ง'],['แล้วบ่นว่า|ถ้าเป็นเราคงทำได้ดีกว่า'],['แต่เดอะฟูลต่างออกไปค่ะ|เขาเดินลงสนามเอง'],['แล้วแทนที่จะเครียด|เขากลับเปลี่ยนกองงานนั้นให้เป็นของเล่น'],['งานที่ดูน่ากลัว|เลยกลายเป็นเรื่องสนุก'],['พังก็ขำ แผนเปลี่ยนก็ปรับ'],['เพราะคนนั่งดูได้แค่ความเห็น','ส่วนคนลงสนามได้ฝีมือกลับไป'],['และพลังวิเศษอันดับหนึ่งของเขาคือ'],['เขาไม่กลัวที่จะดูโง่|ในสายตาคนอื่นค่ะ'],['คำถามที่ทุกคนไม่กล้าถาม|เขาถามก่อน','ทั้งทีมเลยเข้าใจไปด้วย'],['ถ้าคุณเป็นเดอะฟูลในออฟฟิศ|แท็กเพื่อน','แล้วกดติดตามแม่หมอกระต่ายนะคะ'],['ฝากกดไลก์ กดแชร์|และกดติดตามแม่หมอกระต่ายด้วยนะคะ']]
normal=lambda x:''.join(x.replace('|','').split())
caps=[]
for piece,parts in zip(pieces,texts):
 assert normal(''.join(parts))==normal(piece['text']),(piece['piece'],parts)
 weights=[len(normal(x)) for x in parts];t=piece['start']
 for part,w in zip(parts,weights):
  end=t+piece['dur']*w/sum(weights);caps.append({'text':part,'start':t,'end':end,'piece':piece['piece']});t=end
(P/'timing/captions.json').write_text(json.dumps(caps,ensure_ascii=False,indent=2))
def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
(P/'timing/transcript.srt').write_text('\n\n'.join(f"{i+1}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text'].replace('|',chr(10))}" for i,c in enumerate(caps)))
keywords=['เดอะฟูล','แพ้ยากที่สุด','เป็นตัวเอง','เทรนด์ใหม่','ไม่ใช่อู้งาน','จดจ่อ','หอคอย','กองงานยักษ์','ลงสนามเอง','ของเล่น','เรื่องสนุก','พังก็ขำ','ฝีมือ','ไม่กลัว','ทั้งทีม','แท็กเพื่อน','กดติดตาม']
divs=[]
for i,c in enumerate(caps):
 text=html.escape(c['text'])
 for term in keywords:text=text.replace(term,'<span class="hl">'+term+'</span>')
 text='<br>'.join(text.split('|'));endclass=' endcap' if c['piece']==19 else ''
 divs.append(f'<div id="c{i}" class="cap{endclass}"><div class="words">{text}</div></div>')
page='''<!doctype html><html lang="th"><meta charset="utf-8"><script src="assets/gsap.min.js"></script><style>
@font-face{font-family:Kanit;font-weight:800;src:url(assets/fonts/Kanit-ExtraBold.ttf)}*{box-sizing:border-box}html,body{margin:0;width:1080px;height:1920px;background:transparent;overflow:hidden}#reel{position:relative;width:1080px;height:1920px}#shade{position:absolute;inset:1000px 0 0;background:linear-gradient(transparent,rgba(23,10,36,.45))}#brand{position:absolute;top:64px;width:100%;text-align:center;color:#ffe3a1;font:800 29px Kanit;-webkit-text-stroke:5px #241129;paint-order:stroke fill}#narr{position:absolute;width:440px;height:440px;left:320px;top:1475px;filter:drop-shadow(0 5px 12px #23172a88)}#narr img{position:absolute;inset:0;width:100%;opacity:0}.cap{position:absolute;top:1195px;left:60px;width:960px;text-align:center;opacity:0}.words{font:800 66px/1.25 Kanit;color:white;-webkit-text-stroke:11px #170e20;paint-order:stroke fill;text-shadow:0 5px 0 #170e2099}.hl{color:#ffd400;display:inline-block}.endcap{top:1330px}.endcap .words{font-size:49px}.cta{position:absolute;left:70px;width:940px;top:1360px;text-align:center;font:800 46px/1.3 Kanit;color:#ffeab4;-webkit-text-stroke:7px #241129;paint-order:stroke fill;opacity:0}
</style><div id="reel" data-composition-id="fool-office" data-start="0" data-duration="61" data-fps="30" data-width="1080" data-height="1920"><div id="shade"></div><div id="brand">แม่หมอกระต่าย · The Fool ในออฟฟิศ</div><div id="narr">'''+''.join(f'<img id="m{x}" src="assets/mouth_{x}.png">' for x in 'ABCDEF')+'''</div>'''+''.join(divs)+'''<div id="cta" class="cta">กด Like · Share · Follow<br>แม่หมอกระต่ายด้วยนะค้า 🐰</div></div><script>
const tl=gsap.timeline({paused:true});tl.set('#mA',{opacity:1},0);tl.to('#narr',{y:-4,scaleY:1.01,duration:1.5,repeat:33,yoyo:true,ease:'sine.inOut'},0);
'''
for cue in cues:
 if cue['start']>=50.9667:break
 shape=cue['value'] if cue['value'] in 'ABCDEF' else 'A'
 page+=f"tl.set('#narr img',{{opacity:0}},{cue['start']});tl.set('#m{shape}',{{opacity:1}},{cue['start']});\n"
for i,c in enumerate(caps):
 page+=f"tl.fromTo('#c{i}',{{opacity:0,scale:.85}},{{opacity:1,scale:1,duration:.13,ease:'back.out(1.8)',immediateRender:false}},{c['start']});tl.set('#c{i}',{{opacity:0}},{c['end']});\n"
page+="tl.set('#narr,#shade,#brand',{opacity:0},50.9667);tl.set('#cta',{opacity:1},54.2);tl.set('#cta',{opacity:0},59.9);tl.to({},{duration:61},0);window.__timelines={'fool-office':tl};</script></html>"
(O/'index.html').write_text(page);(O/'hyperframes.json').write_text(json.dumps({'paths':{'assets':'assets'}}));print('captions',len(caps),'mouth cues',len(cues))
