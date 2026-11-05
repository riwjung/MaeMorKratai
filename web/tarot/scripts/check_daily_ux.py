"""Verify primary action placement and natural card bounds on mobile browsers."""
import json, os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

root = Path(__file__).resolve().parents[1]
url = os.environ.get('MMKT_TEST_URL', 'http://127.0.0.1:3014').rstrip('/')
out = root / 'artifacts/launch-20261105-ux'
out.mkdir(parents=True, exist_ok=True)
cards = json.loads((root / 'lib/reading-cards.json').read_text())
report = {'url': url, 'passed': False, 'checks': [], 'errors': []}
with sync_playwright() as p:
    for engine, motion in [('chromium', 'reduce'), ('webkit', 'no-preference')]:
        browser = getattr(p, engine).launch()
        page = browser.new_page(viewport={'width': 390, 'height': 760}, is_mobile=True, has_touch=True, reduced_motion=motion)
        page.on('pageerror', lambda e: report['errors'].append(str(e)))
        page.add_init_script('window.__index=0;window.__draws=0;crypto.getRandomValues=a=>{window.__draws++;a.fill(0);a[0]=window.__index;return a}')
        page.goto(url, wait_until='networkidle')
        button = page.locator('.stage-bottom .draw-button')
        expect(button).to_be_enabled(timeout=15000)
        assert page.locator('.draw-button').count() == 1
        assert button.bounding_box()['y'] < page.locator('#context').bounding_box()['y']
        page.locator('.stage-bottom').screenshot(path=str(out / (engine + '-actions.png')))
        samples = ['the-world', 'eight-of-pentacles', 'ten-of-cups', 'the-magician'] if engine == 'chromium' else ['the-world', 'the-magician']
        for card_id in samples:
            index = next(i for i, c in enumerate(cards) if c['id'] == card_id)
            page.evaluate('(i)=>window.__index=i', index)
            button.click()
            expect(page.locator('.reveal-layer')).to_have_attribute('data-state', 'open', timeout=25000)
            expect(page.locator('.reveal-layer')).to_have_attribute('data-card-id', card_id)
            assert page.locator('.reveal-front img').evaluate('''img=>{const r=img.getBoundingClientRect(),shell=img.closest('.reveal-card-shell').getBoundingClientRect();return Math.abs(r.height-r.width*img.naturalHeight/img.naturalWidth)<.15&&Math.abs(shell.height-r.height)<.15&&getComputedStyle(img).boxShadow==='none'}''')
            assert page.locator('.reveal-back').evaluate("el=>getComputedStyle(el).display==='none'")
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            page.screenshot(path=str(out / (engine + '-' + card_id + '.png')))
            page.get_by_role('button', name='ปิดไพ่และเก็บกลับ', exact=True).click()
            expect(page.locator('.reveal-layer')).to_have_count(0, timeout=5000)
        before = page.evaluate('window.__draws')
        page.get_by_role('button', name='เปิดไพ่ใบเดิมจากมือแม่หมอ', exact=True).click()
        expect(page.locator('.reveal-layer')).to_have_attribute('data-state', 'open', timeout=25000)
        assert page.evaluate('window.__draws') == before
        report['checks'].append(f'{engine}: primary action before preferences under scene; natural image/frame bounds; no outer stroke/back face; reopen does not redraw; motion={motion}')
        browser.close()
assert not report['errors'], report['errors']
report['passed'] = True
path = out / ('production-ux.json' if 'vercel.app' in url else 'local-ux.json')
path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False))
