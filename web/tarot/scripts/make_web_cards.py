"""Web-size card faces for the reading page: public/cards/<id>.jpeg -> public/cards/web/<id>.webp (600 px wide).
The originals stay byte-identical (see public/cards/manifest.json) and remain the fallback.
Run after adding card art: python3 scripts/make_web_cards.py   (needs `cwebp`, e.g. `brew install webp`)
"""
import json, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'public' / 'cards' / 'web'
WIDTH, QUALITY = 600, 82

def main():
    cwebp = shutil.which('cwebp')
    if not cwebp:
        sys.exit('cwebp not found (brew install webp)')
    data = json.loads((ROOT / 'lib' / 'reading-cards.json').read_text())
    cards = data['cards'] if isinstance(data, dict) else data
    OUT.mkdir(parents=True, exist_ok=True)
    made = 0
    for card in cards:
        art = card.get('art') or ''
        if not art.startswith('/cards/') or not art.endswith(('.jpeg', '.jpg')):
            continue
        source = ROOT / 'public' / art.lstrip('/')
        target = OUT / (card['id'] + '.webp')
        if not source.exists():
            sys.exit(f'missing art for {card["id"]}: {source}')
        if target.exists() and target.stat().st_mtime >= source.stat().st_mtime:
            continue
        subprocess.run([cwebp, '-quiet', '-q', str(QUALITY), '-resize', str(WIDTH), '0', '-metadata', 'none', str(source), '-o', str(target)], check=True)
        made += 1
        print(f'{card["id"]}: {source.stat().st_size // 1024} KB -> {target.stat().st_size // 1024} KB')
    print(json.dumps({'made': made, 'web_cards': len(list(OUT.glob('*.webp')))}))

if __name__ == '__main__':
    main()
