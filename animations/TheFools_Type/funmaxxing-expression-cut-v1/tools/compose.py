from pathlib import Path
import json,subprocess,sys
P=Path(__file__).resolve().parent.parent
shots=json.loads((P/'timing/shots.json').read_text());proof='--proof' in sys.argv
chosen=shots[:3] if proof else shots
for s in chosen:assert (P/f'renders/shot-{s["index"]:02}.mp4').exists(),s['index']
(P/'edit').mkdir(exist_ok=True)
(P/'edit/scenes.txt').write_text(''.join(f"file '{P}/renders/shot-{s['index']:02}.mp4'\n" for s in chosen))
main=sum(s['frames'] for s in chosen);total=round(12*30) if proof else 1830
cmd=['ffmpeg','-y','-hide_banner','-loglevel','warning','-threads','2','-f','concat','-safe','0','-i',str(P/'edit/scenes.txt')]
filters=[]
if not proof:
 cmd+=['-i',str(P/'assets/end/end-credit-v1.mp4'),'-c:v','libvpx-vp9','-i',str(P/'overlay/overlay.webm'),'-i',str(P/'audio/episode-mix.wav')]
 filters += [f'[0:v]trim=end_frame={main},setpts=PTS-STARTPTS,setsar=1[a]','[1:v]fps=30,trim=end_frame=300,setpts=PTS-STARTPTS,setsar=1[b]',f'[a][b]concat=n=2:v=1:a=0,tpad=stop_mode=clone:stop_duration=0.1,trim=end_frame={total}[base]', '[base][2:v]overlay=0:0:eof_action=pass,format=yuv420p[v]']
 audio='3:a';out=P/'fool-office-expression-v1.mp4'
else:
 cmd+=['-c:v','libvpx-vp9','-i',str(P/'overlay/overlay.webm'),'-i',str(P/'audio/episode-mix.wav')]
 filters+=['[0:v][1:v]overlay=0:0:eof_action=pass,format=yuv420p[v]'];audio='2:a';out=P/'review/opening-proof-12s.mp4'
cmd+=['-filter_complex_threads','2','-filter_complex',';'.join(filters),'-map','[v]','-map',audio,'-frames:v',str(total),'-t',str(total/30),'-r','30','-c:v','libx264','-threads','4','-preset','fast','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(out)]
(P/'edit/compose-command.json').write_text(json.dumps(cmd,indent=2));
with (P/'qa/compose.log').open('w') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
print('COMPOSED',out,flush=True)
