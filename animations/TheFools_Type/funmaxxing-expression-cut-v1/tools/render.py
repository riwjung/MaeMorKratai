from pathlib import Path
import subprocess,json,sys,time
P=Path(__file__).resolve().parent.parent;B='/Applications/Blender.app/Contents/MacOS/Blender'
shots=json.loads((P/'timing/shots.json').read_text());stills='--stills' in sys.argv
for s in shots:
 i=s['index'];dst=P/f'renders/shot-{i:02}.mp4'
 if not stills and dst.exists():continue
 with (P/f'qa/render-{i:02}.log').open('w') as log:
  cmd=[B,'-b','--factory-startup','-P',str(P/'blender/build_scenes.py'),'--',str(i)]
  if not stills:cmd+=['--render']
  subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
 if stills:
  assert (P/f'review/shot-{i:02}.jpg').exists()
 else:
  seq=P/f'renders/shot-{i:02}';fs=list(seq.glob('*.jpg'));assert len(fs)==s['frames'],(i,len(fs),s['frames'])
  subprocess.run(['ffmpeg','-v','error','-y','-framerate','30','-start_number','1','-i',str(seq/'frame-%04d.jpg'),'-frames:v',str(s['frames']),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(dst)],check=True)
  # The MP4 and .blend are kept; discard only reproducible frames from this run.
  for f in fs:f.unlink()
 print('STILL' if stills else 'RENDERED',i,flush=True)
