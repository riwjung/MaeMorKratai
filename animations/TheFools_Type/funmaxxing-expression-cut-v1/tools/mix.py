from pathlib import Path
import subprocess
P=Path(__file__).resolve().parent.parent
fc='[0:a]pan=stereo|c0=c0|c1=c0,apad=whole_dur=61,asplit=2[v][side];[1:a][side]sidechaincompress=threshold=0.025:ratio=5:attack=15:release=220[bed];[v][bed]amix=inputs=2:normalize=0,alimiter=limit=0.95:level=false,volume=-3dB,atrim=0:61[a]'
subprocess.run(['ffmpeg','-y','-v','error','-i',str(P/'audio/sai-voicestudio-seedref-v8-final.wav'),'-i',str(P/'audio/music-sfx.wav'),'-filter_complex',fc,'-map','[a]','-ar','48000','-c:a','pcm_s16le',str(P/'audio/episode-mix.wav')],check=True)
with (P/'qa/loudness-final-mix.log').open('w') as f:subprocess.run(['ffmpeg','-hide_banner','-i',str(P/'audio/episode-mix.wav'),'-af','ebur128=peak=true','-f','null','-'],stderr=f,stdout=f,check=True)
