from pathlib import Path
import re,os
P=Path(__file__).resolve().parents[1]
B=Path(os.environ.get('MAEMOR_SCENE_DIR',P.parent/'halloween-2026'))
if not B.exists():B=P.parents[1]/'animations/halloween-2026'
s=(B/'index.html').read_text()
s=re.sub(r"@font-face\{[^}]*\}",'',s).replace('Brand,Georgia,serif','Georgia,serif')
s=s.replace('</body>','<script src="controller.js"></script></body>')
# A failed animation download must let controller.js report a static fallback.
s=s.replace('const tl=gsap.timeline({paused:true});', 'if (window.gsap) {\nconst tl=gsap.timeline({paused:true});', 1)
s=s.replace("window.__timelines['maemorkratai-halloween']=tl;", "window.__timelines['maemorkratai-halloween']=tl;\n}", 1)
(P/'public/scene/index.html').write_text(s)
