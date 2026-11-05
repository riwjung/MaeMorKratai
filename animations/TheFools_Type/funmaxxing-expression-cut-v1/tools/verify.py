from pathlib import Path
from html.parser import HTMLParser
import subprocess,json,hashlib
P=Path(__file__).resolve().parent.parent
video=P/'fool-office-expression-v1.mp4'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
v=next(x for x in probe['streams'] if x['codec_type']=='video');a=next(x for x in probe['streams'] if x['codec_type']=='audio')
assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1080,1920,'30/1',1830)
assert abs(float(probe['format']['duration'])-61)<.05
assert a['sample_rate']=='48000' and a['channels']==2
subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(video),'-f','null','-'],check=True)
manifest=json.loads((P/'production.json').read_text());voice=P/manifest['voice']['file'];assert hashlib.sha256(voice.read_bytes()).hexdigest()==manifest['voice']['sha256']
shots=json.loads((P/'timing/shots.json').read_text());assert sum(s['frames'] for s in shots)==1529
caps=json.loads((P/'timing/captions.json').read_text());pieces=json.loads((P/'timing/pieces.json').read_text())
norm=lambda x:''.join(x.replace('|','').split())
assert norm(''.join(c['text'] for c in caps))==norm(''.join(c['text'] for c in pieces))
cues=json.loads((P/'timing/mouth-cues.json').read_text())['mouthCues']
assert len(cues)>100 and cues[-1]['end']>=53.8
for s in shots:
 r=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=nb_frames','-of','json',str(P/f'renders/shot-{s["index"]:02}.mp4')]))
 assert int(r['streams'][0]['nb_frames'])==s['frames']
class Links(HTMLParser):
 def __init__(self):super().__init__();self.paths=[]
 def handle_starttag(self,tag,attrs):
  self.paths += [v for k,v in attrs if k in ('href','src','poster') and v and not v.startswith(('http:','https:','#','data:'))]
l=Links();l.feed((P/'review.html').read_text());missing=[x for x in l.paths if not (P/x).exists()];assert not missing,missing
report={'duration_s':float(probe['format']['duration']),'video':{'width':v['width'],'height':v['height'],'fps':v['r_frame_rate'],'frames':int(v['nb_frames'])},'audio':{'sample_rate':a['sample_rate'],'channels':a['channels']},'full_decode_passed':True,'voice_original_sha256_unchanged':True,'exact_script_in_captions':True,'captions':len(caps),'mouth_cues':len(cues),'all_12_render_frame_counts_passed':True,'review_links_missing':missing,'video_sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'credits_used':0,'limitations':['Rhubarb phonetic follows Thai speech rhythm approximately','Fool mouth/eye edge topology from Tripo remains visible in closeups','Glasses rabbit uses original face texture; expression morphs applied to Fool only','Inner-phrase caption boundaries are proportional to text length, phrase starts follow final.sources.json']}
(P/'qa/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
