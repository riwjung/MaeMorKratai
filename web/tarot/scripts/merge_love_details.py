"""Merge knowledge/web/love-details/part*.json into lib/reading-cards.json as `details`.

The original short `meanings` (from the owner's chat) stay untouched and are shown as the
headline; `details` is the longer reading written in Mae Mor Kratai's voice (style taken
from her 40 development workshop readings, Supabase, read 2026-10-30). Status:
claude_draft_published_pending_owner_review. Fails on any gap, duplicate or banned pattern.
python3 scripts/merge_love_details.py
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VAULT = ROOT.parents[1]
SRC = VAULT / 'knowledge/web/love-details'
STATES = ['คนโสด', 'แอบชอบ', 'คุยกัน', 'ซับซ้อน', 'มีแฟน', 'เลิกกัน']
BANNED = [r'\d+\s*%', r'เปอร์เซ็นต์', r'ภายใน\s*\d', r'\d+\s*(วัน|สัปดาห์|เดือน)', r'แน่นอน100', r'(?<!เส้น)ตาย(?!ตัว)', r'โรค']

details = {}
for f in sorted(SRC.glob('part*.json')):
    for cid, texts in json.loads(f.read_text()).items():
        assert cid not in details, f'duplicate {cid} in {f.name}'
        details[cid] = texts
cards = json.loads((ROOT / 'lib/reading-cards.json').read_text())
ids = [c['id'] for c in cards]
assert set(details) == set(ids), (set(ids) - set(details), set(details) - set(ids))
seen, lengths = set(), []
for c in cards:
    t = details[c['id']]
    assert len(t) == 6, c['id']
    for s, body in zip(STATES, t):
        body = body.strip()
        assert body not in seen, ('duplicate text', c['id'], s)
        seen.add(body)
        for pat in BANNED:
            if pat == r'(?<!เส้น)ตาย(?!ตัว)' and 'ไม่ได้แปลว่าจะมีใครตาย' in body:
                continue
            assert not re.search(pat, body), (c['id'], s, pat)
        assert body.endswith(('ค่ะ', 'นะคะ', 'คะ')), (c['id'], s)
        lengths.append(len(body))
    c['details'] = dict(zip(STATES, [b.strip() for b in t]))
    c['details_status'] = 'claude_draft_published_pending_owner_review'
(ROOT / 'lib/reading-cards.json').write_text(json.dumps(cards, ensure_ascii=False, indent=1) + '\n')
lengths.sort()
print(json.dumps({'cards': len(cards), 'texts': len(lengths), 'chars_min': lengths[0],
                  'chars_median': lengths[len(lengths) // 2], 'chars_max': lengths[-1]}, ensure_ascii=False))
