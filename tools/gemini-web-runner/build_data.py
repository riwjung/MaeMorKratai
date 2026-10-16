from pathlib import Path
import json,shutil,hashlib
P=Path(__file__).resolve().parent
V=Path.home()/'Desktop/AI_Video/MaeMorKratai'
S=V/'animations/tarot-pilot/prompts-78'
m=json.loads((S/'manifest.json').read_text())
rows=[{k:c[k] for k in ['sequence','id','name','existing_generated_image']}|{'prompt':(S/c['prompt_file']).read_text()} for c in m['cards']]
assert len(rows)==len({r['id'] for r in rows})==78
(P/'extension/deck-data.js').write_text('globalThis.MMKT_DECK = '+json.dumps(rows,ensure_ascii=False)+';\n')
ref=V/'wiki/Images/IMG_5392.JPG';shutil.copy2(ref,P/'extension/assets/IMG_5392.JPG')
(P/'reference.json').write_text(json.dumps({'reference_image':'wiki/Images/IMG_5392.JPG','sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),'cards':78,'default_skip_existing':5},indent=2))
print('Prepared78prompts+originalreference; noAPI/no.env')
