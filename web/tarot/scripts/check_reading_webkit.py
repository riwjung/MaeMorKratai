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
  context.close()
  # Frame rate with normal motion settings. The filtered SVG scene used to animate here and held the whole page
  # near 1 fps; on Safari and touch devices it now stays still, so the page and the WebGL shuffle keep up.
  fps="()=>new Promise(r=>{let n=0;const t0=performance.now();const f=()=>{n++;if(performance.now()-t0<2000)requestAnimationFrame(f);else r(n/2)};requestAnimationFrame(f)})"
  context=browser.new_context(**p.devices['iPhone 13']);page=context.new_page()
  page.on('pageerror',lambda e:report['errors'].append(str(e)))
  page.goto(URL+'/');page.wait_for_timeout(4000)
  scene=page.frames[1]
  # The scene fits itself with CSS zoom; a transform left 3x screens building filter buffers past Safari's limit.
  assert scene.evaluate('document.documentElement.dataset.motion')=='still' and float(scene.evaluate("document.querySelector('#halloween').style.zoom")) < 1
  # Her idle motion plays as a baked loop over the still scene.
  page.wait_for_function("(()=>{const v=document.querySelector('.room-window .idle-video');return v&&v.classList.contains('is-playing')&&!v.paused&&v.currentTime>0.5})()",timeout=8000)
  home=page.evaluate(fps);assert home>=30,f'home page {home} fps'
  # The home reveal used to stay on the mirrored back on Safari; the drawn card's face must be the visible side.
  expect(page.locator('.draw-button')).to_be_enabled(timeout=15000);page.locator('.draw-button').tap()
  # The still scene plays the baked shuffle-and-raise video for the draw; the reveal waits for it.
  page.wait_for_function("(()=>{const v=document.querySelector('.room-window .draw-video');return v&&v.classList.contains('is-playing')&&!v.paused&&v.currentTime>1})()",timeout=8000)
  assert not page.locator('.reveal-layer').count(),'reveal opened before the shuffle video ended'
  assert not page.evaluate("document.querySelector('.room-window .idle-video').classList.contains('is-playing')"),'idle loop still shown during the draw'
  expect(page.locator('.reveal-layer')).to_have_attribute('data-state','open',timeout=20000)
  faces=page.locator('.reveal-flipper').evaluate("(f)=>[getComputedStyle(f.querySelector('.reveal-front')).visibility,getComputedStyle(f.querySelector('.reveal-back')).visibility]")
  assert faces==['visible','hidden'],faces
  page.screenshot(path=str(OUT/'iphone-home-reveal.png'))
  # After "read the meaning below" the card stays face up in her hand (owner's request).
  page.locator('.reveal-details').tap();expect(page.locator('.reveal-layer')).to_have_count(0,timeout=8000)
  hand=page.frame_locator('.room-window iframe')
  expect(hand.locator('#card-front')).to_have_css('opacity','1');expect(hand.locator('#card-back')).to_have_css('opacity','0')
  # The reading below shows the card's face too, loaded, with no card back left on the page.
  page.wait_for_function("(()=>{const i=document.querySelector('.result-art img.result-card-face');return !!i&&i.complete&&i.naturalWidth>0})()",timeout=8000)
  assert not page.locator('.result-art .shared-card-back').count(),'card back still shown in the reading'
  page.screenshot(path=str(OUT/'iphone-home-details.png'))
  ok('idle loop plays; shuffle video plays, the reveal shows the face, and the card stays face up after closing, in her hand and in the reading')
  page.goto(URL+'/reading/');phase(page,'topic');page.get_by_role('button',name='ไปต่อ',exact=False).tap();phase(page,'question')
  page.get_by_role('button',name='พร้อมแล้ว',exact=False).tap();phase(page,'shuffling');page.wait_for_timeout(2500)
  assert page.evaluate("!!document.querySelector('canvas.ritual-deck-canvas')"),'WebGL deck not live'
  shuffle=page.evaluate(fps);assert shuffle>=30,f'3D shuffle {shuffle} fps'
  report['fps']={'home':home,'shuffle':shuffle};ok(f'still scenes keep the page fluid: home {home} fps, 3D shuffle {shuffle} fps')
  context.close()
  # iOS Low Power Mode refuses to play videos; the draw must still reveal the card, over the still scene.
  context=browser.new_context(**p.devices['iPhone 13']);page=context.new_page()
  page.on('pageerror',lambda e:report['errors'].append(str(e)))
  page.add_init_script("HTMLMediaElement.prototype.play=function(){return Promise.reject(new DOMException('Low Power Mode','NotAllowedError'))}")
  page.goto(URL+'/');expect(page.locator('.draw-button')).to_be_enabled(timeout=15000);page.locator('.draw-button').tap()
  expect(page.locator('.reveal-layer')).to_have_attribute('data-state','open',timeout=15000)
  assert not page.evaluate("document.querySelector('.room-window .draw-video').classList.contains('is-playing')"),'refused video still covers the scene'
  ok('video playback refused (Low Power Mode): the reveal opens over the still scene')
  assert not report['errors'],report['errors']
  report['passed']=True
 finally:
  (OUT/'webkit-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');browser.close()
print(json.dumps({'passed':report.get('passed',False),'checks':len(report['checks'])}),flush=True)
