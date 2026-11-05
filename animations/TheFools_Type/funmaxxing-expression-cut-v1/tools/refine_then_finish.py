from pathlib import Path
import subprocess,time,json
P=Path(__file__).resolve().parent.parent
while 'RENDERED 12' not in (P/'qa/render-progress.log').read_text():time.sleep(5)
old=P/'renders/shot-11.mp4';old.replace(P/'qa/shot-11-before-arm-refine.mp4')
with (P/'qa/arm-refine-render.log').open('w') as log:subprocess.run(['python3',str(P/'tools/render.py')],cwd=P,stdout=log,stderr=subprocess.STDOUT,check=True)
m=json.loads((P/'production.json').read_text());m['refinements']=['Shot 11: reduced asking-arm lift to 42 degrees to reduce underarm stretching and keep paw in frame'];(P/'production.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
subprocess.run(['python3',str(P/'tools/finish_after_render.py')],cwd=P,check=True)
