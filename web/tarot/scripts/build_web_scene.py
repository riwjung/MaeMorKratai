from pathlib import Path
import re,os
P=Path(__file__).resolve().parents[1]
B=Path(os.environ.get('MAEMOR_SCENE_DIR',P.parent/'halloween-2026'))
if not B.exists():B=P.parents[1]/'animations/halloween-2026'
s=(B/'index.html').read_text()
s=re.sub(r"@font-face\{[^}]*\}",'',s).replace('Brand,Georgia,serif','Georgia,serif')
s=s.replace('</body>','<script src="controller.js"></script></body>')
(P/'public/scene/index.html').write_text(s)
