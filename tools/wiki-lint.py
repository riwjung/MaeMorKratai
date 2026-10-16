#!/usr/bin/env python3
"""Check actual vault YAML, internal links and index coverage without modifying it."""
import os
import re
import sys
from pathlib import Path
try:
    import yaml
except ImportError:
    interpreter=Path.home()/'AIVideoLocal/maemorkratai/.venv/bin/python'
    if interpreter.exists():
        os.execv(str(interpreter),[str(interpreter),__file__,*sys.argv[1:]])
    raise SystemExit('ต้องติดตั้ง PyYAML ใน virtualenv ของโปรเจกต์')
vault=Path(os.environ.get('MAEMOR_VAULT_DIR',Path.home()/'Desktop/AI_Video/MaeMorKratai'))
files=list((vault/'wiki').rglob('*.md'))
names=[p.stem for p in files]
targets={p.stem for p in vault.rglob('*') if p.is_file() and p.suffix in ('.md','.json','.csv')}
errors=[]
if len(names)!=len(set(names)):errors.append('slug ใน wiki ซ้ำ')
index=(vault/'index.md').read_text() if (vault/'index.md').exists() else ''
for p in files:
    text=p.read_text()
    try:
        if not text.startswith('---\n'):raise ValueError('ไม่มี frontmatter')
        meta=yaml.safe_load(text.split('---',2)[1])
        required={'type','title','aliases','tags','created','updated'}
        if meta.get('type')=='source':required|={'source_type','author','published','url','raw_path','ingested'}
        else:required|={'status','sources'}
        missing=required-meta.keys()
        if missing:errors.append(f'{p.name}: missing {sorted(missing)}')
        if meta.get('type')=='source' and not (vault/meta['raw_path']).exists():errors.append(f'{p.name}: raw_path ไม่พบ')
    except Exception as e:
        errors.append(f'{p.name}: frontmatter ไม่ถูกต้อง ({type(e).__name__})')
    for target in re.findall(r'\[\[([^\]|#]+)(?:[^\]]*)\]\]',text):
        if target.replace('\\','') not in targets:errors.append(f'{p.name}: link ไม่พบ {target}')
    if f'[[{p.stem}]]' not in index:errors.append(f'{p.name}: ไม่มีใน index')
if errors:
    print('\n'.join(errors));raise SystemExit(1)
print(f'PASS: {len(files)} wiki pages; YAML / raw references / links / index ครบ')
