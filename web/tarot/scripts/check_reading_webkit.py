"""Safari-engine smoke check: the /reading/ flow on WebKit with iPhone 13 emulation.
Run: MMKT_TEST_URL=http://127.0.0.1:3010 ../.venv/bin/python scripts/check_reading_webkit.py
Needs `python -m playwright install webkit`. Uses reduced motion: headless WebKit delivers only about one
animation frame every two seconds, so the WebGL path cannot be timed here; check that one on a real phone.
"""
import json, os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
URL=os.getenv('MMKT_TEST_URL','http://127.0.0.1:3010')
OUT=Path(__file__).resolve().parents[1]/'artifacts'/'reading-webkit'
OUT.mkdir(parents=True,exist_ok=True)
report={'checks':[],'errors':[]}
def ok(name):report['checks'].append(name);print('PASS',name,flush=True)
def phase(page,value):expect(page.locator('main.ritual')).to_have_attribute('data-phase',value,timeout=15000)
with sync_playwright() as p:
 browser=p.webkit.launch()
 try:
  context=browser.new_context(**p.devices['iPhone 13'],reduced_motion='reduce');page=context.new_page()
  page.on('pageerror',lambda e:report['errors'].append(str(e)))
  page.on('console',lambda m:report['errors'].append(m.text) if m.type=='error' else None)
  page.goto(URL+'/');expect(page.locator('a.three-card-entry')).to_be_visible()
  # The home header must fit one line on a phone.
  assert page.locator('.site-header nav').evaluate('(n)=>[...n.children].filter(a=>getComputedStyle(a).display!=="none").every(a=>a.getClientRects().length===1)')
  page.screenshot(path=str(OUT/'iphone-home.png'));ok('home page and one-line header')
  page.locator('a.three-card-entry').tap();phase(page,'topic')
  page.get_by_role('button',name='ไปต่อ',exact=False).tap();phase(page,'question')
  page.get_by_role('button',name='พร้อมแล้ว',exact=False).tap();phase(page,'shuffling')
  page.locator('.ritual-shuffle').tap();phase(page,'selecting');ok('shuffle, stop and spread')
  page.get_by_role('button',name='ดูครบทุกใบ',exact=False).tap()
  for card_id in ['the-fool','the-lovers','queen-of-swords']:
   page.locator(f'[data-deck-id="{card_id}"]').tap();page.get_by_role('button',name='เลือกใบนี้',exact=False).tap()
  # WebKit ignored backface-visibility here once and showed the mirrored front; the closed front must be hidden.
  hidden=page.locator('[data-slot] .ritual-card-visual[data-open=false] .ritual-card-front').evaluate_all('(els)=>els.map(e=>getComputedStyle(e).visibility)')
  assert hidden==['hidden']*3,hidden
  page.screenshot(path=str(OUT/'iphone-placed.png'));ok('three cards placed; closed fronts hidden')
  for position in ['อนาคต','อดีต','ปัจจุบัน']:page.get_by_role('button',name='เปิดไพ่ตำแหน่ง'+position,exact=True).tap()
  phase(page,'locked');expect(page.locator('.ritual-card-visual[data-open=true]')).to_have_count(3)
  page.get_by_role('button',name='ปลดล็อกคำอ่านฉบับเต็ม',exact=False).tap();phase(page,'reading')
  expect(page.locator('[data-reading-id]')).to_have_count(3)
  assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'),'horizontal overflow'
  page.screenshot(path=str(OUT/'iphone-reading.png'),full_page=True);ok('open by tap, unlock demo and reading, no overflow')
  assert not report['errors'],report['errors']
  report['passed']=True
 finally:
  (OUT/'webkit-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');browser.close()
print(json.dumps({'passed':report.get('passed',False),'checks':len(report['checks'])}),flush=True)
