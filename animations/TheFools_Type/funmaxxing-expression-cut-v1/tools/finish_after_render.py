from pathlib import Path
import json,subprocess,time,hashlib,shutil
P=Path(__file__).resolve().parent.parent
shots=json.loads((P/'timing/shots.json').read_text());state=P/'qa/finalization.json'
start=time.monotonic()
while True:
 done=[s['index'] for s in shots if (P/f'renders/shot-{s["index"]:02}.mp4').exists()]
 state.write_text(json.dumps({'phase':'rendering','completed_shots':done,'total_shots':12},indent=2))
 if len(done)==12 and 'RENDERED 12' in (P/'qa/render-progress.log').read_text():break
 log=(P/'qa/render-progress.log').read_text()
 if 'Traceback' in log:raise RuntimeError('Render stopped; inspect qa/render-progress.log')
 if time.monotonic()-start>7200:raise TimeoutError('Render watchdog expired')
 time.sleep(10)
state.write_text(json.dumps({'phase':'composing'}))
subprocess.run(['python3',str(P/'tools/compose.py')],cwd=P,check=True)
for t in [2,7,18,22,28,33,40,44,50,52,56,60]:
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(P/'fool-office-expression-v1.mp4'),'-frames:v','1',str(P/f'review/final-{t:03}.jpg')],check=True)
subprocess.run(['python3',str(P/'tools/make_review.py')],cwd=P,check=True)
subprocess.run(['python3',str(P/'tools/verify.py')],cwd=P,check=True)
(P/'qa/render-progress.json').write_text(json.dumps({'completed_shots':list(range(1,13)),'completed_frames':1529,'total_frames':1529},indent=2))
video=P/'fool-office-expression-v1.mp4';dst=Path('/Users/sawettachatsuthum/Desktop/AI_Video/FinalResult/MaeMorKratai_TheFool_Office_Expression_v1.mp4')
sha=hashlib.sha256(video.read_bytes()).hexdigest()
if dst.exists():assert hashlib.sha256(dst.read_bytes()).hexdigest()==sha,'Existing destination differs; stop to inspect'
else:shutil.copy2(video,dst)
assert hashlib.sha256(dst.read_bytes()).hexdigest()==sha
state.write_text(json.dumps({'phase':'verified_and_delivered','video':str(video),'delivery':str(dst),'sha256':sha},indent=2));print('DELIVERED',dst,flush=True)
