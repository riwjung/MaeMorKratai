"""Local production browser acceptance. No generation, accounts or payments.
Run: ../.venv/bin/python scripts/check_reading_ui.py
"""
import json, time, os
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'reading'
OUT.mkdir(parents=True,exist_ok=True)
URL=os.getenv('MMKT_TEST_URL','http://127.0.0.1:3010')
report={'checks':[], 'errors':[], 'failed_requests':[], 'external_requests':[], 'screenshots':[]}
def record(name,**extra):
 report['checks'].append({'name':name,'passed':True,**extra});print('PASS',name,flush=True)
def shot(page,name):
 page.screenshot(path=str(OUT/(name+'.png')),full_page=True,animations='disabled');report['screenshots'].append(name+'.png')
def attach(page):
 page.on('pageerror',lambda e:report['errors'].append(str(e)))
 page.on('response',lambda r:report['failed_requests'].append(str(r.status)+' '+r.url) if r.status>=400 else None)
 def route(r):
  u=urlparse(r.request.url)
  if u.scheme in ['http','https'] and u.netloc!=urlparse(URL).netloc:report['external_requests'].append(r.request.url);r.abort()
  else:r.continue_()
 page.route('**/*',route)
def phase(page,value):expect(page.locator('main.ritual')).to_have_attribute('data-phase',value,timeout=12000)
def setup(page,category='ความรัก',situation='คนโสด',question='ฉันอยากเข้าใจความสัมพันธ์นี้'):
 page.goto(URL+'/reading/');phase(page,'topic')
 page.get_by_role('button',name=category,exact=False).first.click()
 page.locator('#reading-question').fill(question)
 page.get_by_role('button',name='ไปต่อ',exact=False).click();phase(page,'question')
 page.get_by_role('button',name=situation,exact=True).click()
 page.get_by_role('button',name='พร้อมแล้ว',exact=False).click();phase(page,'shuffling')
def deck_pose(page):
 # WebGL deck publishes its pose on the tap target; the DOM fallback deck exposes CSS transforms.
 page.wait_for_function("document.querySelector('.ritual-shuffle')?.dataset.pose || document.querySelectorAll('.ritual-shuffle-card').length>8",timeout=12000)
 return page.evaluate("(()=>{const d=document.querySelector('.ritual-shuffle');return d.dataset.pose||getComputedStyle(d.querySelectorAll('.ritual-shuffle-card')[8]).transform})()")
def grab_point(page,card_id):
 # The middle of the strip of a fanned card that its neighbours leave uncovered. A lifted neighbour can briefly
 # cover it, so look again a few times before giving up.
 for _ in range(3):
  page.locator(f'[data-deck-id="{card_id}"]').scroll_into_view_if_needed()
  point=page.evaluate('''(id)=>{const el=document.querySelector(`[data-deck-id="${id}"]`);const r=el.getBoundingClientRect();
   for(const f of [.5,.35,.65]){const y=r.top+r.height*f,hits=[];for(let x=r.left+2;x<r.right-2;x+=2)if(document.elementFromPoint(x,y)?.closest('[data-deck-id]')===el)hits.push(x);
    if(hits.length)return [hits[Math.floor(hits.length/2)],y];}return null}''',card_id)
  if point:return point
  page.wait_for_timeout(300)
 return None
def slots(page):return page.locator('[data-slot]').evaluate_all('(els)=>els.map(e=>e.dataset.cardId)')
def drag_to_slot(page,card_id,slot):
 # Hovering lifts the card under the mouse and a wave around it, which can cover a narrow strip. Like a person,
 # aim, check what is actually under the pointer, and if it is a neighbour, move away and aim again.
 hit=point=None
 for _ in range(4):
  point=grab_point(page,card_id)
  if point:
   page.mouse.move(*point);page.wait_for_timeout(350)
   hit=page.evaluate('([x,y])=>document.elementFromPoint(x,y)?.closest("[data-deck-id]")?.dataset.deckId',point)
   if hit==card_id:break
  page.mouse.move(5,5);page.wait_for_timeout(350)
 assert hit==card_id,'card not reachable'
 page.mouse.down();page.mouse.move(point[0],point[1]-24,steps=3)
 if slot is None:page.mouse.move(point[0]+40,point[1]-60,steps=6)
 else:
  t=page.locator(f'[data-slot="{slot}"] .ritual-slot-card').bounding_box();page.mouse.move(t['x']+t['width']/2,t['y']+t['height']/2,steps=14)
 page.mouse.up();expect(page.locator('.ritual-flight')).to_have_count(0);expect(page.locator('.ritual-ghost')).to_have_count(0)
 if slot is not None:expect(page.locator(f'[data-slot="{slot}"]')).to_have_attribute('data-card-id',card_id)
def touch_drag_to_slot(page,card_id,slot):
 # Real touch input through CDP, so touch-action and the vertical-pull rule are exercised.
 point=grab_point(page,card_id);assert point,'card not reachable'
 t=page.locator(f'[data-slot="{slot}"] .ritual-slot-card').bounding_box();goal=(t['x']+t['width']/2,t['y']+t['height']/2)
 cdp=page.context.new_cdp_session(page)
 cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':point[0],'y':point[1]}]})
 for k in range(1,19):cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':point[0]+(goal[0]-point[0])*k/18,'y':point[1]+(goal[1]-point[1])*k/18}]})
 cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
 expect(page.locator(f'[data-slot="{slot}"]')).to_have_attribute('data-card-id',card_id)
def stop(page):
 page.get_by_role('button',name='หยุดสับไพ่',exact=False).last.click();phase(page,'selecting')
def grid(page):page.get_by_role('button',name='ดูครบทุกใบ',exact=False).click()
def pick(page,card_id):
 page.locator(f'[data-deck-id="{card_id}"]').click()
 page.get_by_role('button',name='เลือกใบนี้',exact=False).click()
 expect(page.locator('.ritual-flight')).to_have_count(0)
def reveal(page):
 page.get_by_role('button',name='เปิดไพ่ทั้งสามใบ',exact=False).click();phase(page,'locked')
 expect(page.locator('.ritual-slot-card.is-open')).to_have_count(3)
def unlock(page):page.get_by_role('button',name='ปลดล็อกคำอ่านฉบับเต็ม',exact=False).click();phase(page,'reading')
def no_overflow(page):assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'horizontal page overflow'
with sync_playwright() as p:
 browser=p.chromium.launch()
 page=browser.new_page(viewport={'width':1440,'height':1000});attach(page)
 try:
  page.goto(URL+'/');expect(page.locator('a.three-card-entry')).to_be_visible();page.locator('a.three-card-entry').click();phase(page,'topic');shot(page,'desktop-question');no_overflow(page);record('homepage navigation and desktop topic')
  setup(page,situation='คุยกัน');shot(page,'desktop-shuffling')
  a=deck_pose(page)
  page.wait_for_timeout(1100)
  b=deck_pose(page);assert a!=b
  # Real elapsed duration, not a fast-forwarded clock.
  started=time.monotonic()
  while time.monotonic()-started<60:page.wait_for_timeout(1000)
  phase(page,'shuffling');record('shuffle stays live beyond 60 seconds',elapsed=round(time.monotonic()-started,1))
  # Freeze time only during the stop sampling to verify continuity, then resume.
  page.evaluate('window.gsap.ticker.sleep()')
  before=deck_pose(page)
  page.get_by_role('button',name='หยุดสับไพ่',exact=False).last.click()
  immediate=deck_pose(page)
  assert before==immediate, 'stop reset transform'
  page.evaluate('window.gsap.ticker.wake()');phase(page,'selecting');record('stop preserves current pose, then gathers and spreads')
  expect(page.locator('[data-deck-id]')).to_have_count(78);assert len(set(page.locator('[data-deck-id]').evaluate_all('(els)=>els.map(e=>e.dataset.deckId)')))==78
  expect(page.locator('.ritual-slot-card').first).to_be_visible();expect(page.locator('.ritual-slot-empty').first).to_be_visible();shot(page,'desktop-fan');grid(page);expect(page.locator('.ritual-deck-grid')).to_be_visible();record('78 identities and shared grid view')
  ids=['the-fool','the-lovers','queen-of-swords']
  pick(page,ids[0]);page.get_by_role('button',name='กลับมุมมองพัด',exact=False).click()
  drag_to_slot(page,ids[1],2);assert slots(page)==[ids[0],'',ids[1]]
  drag_to_slot(page,ids[2],None);assert slots(page)==[ids[0],'',ids[1]];expect(page.locator(f'[data-deck-id="{ids[2]}"]')).to_be_visible()
  grid(page);pick(page,ids[2]);assert slots(page)==[ids[0],ids[2],ids[1]];expect(page.locator('.ritual-slot-card.is-open')).to_have_count(0)
  page.get_by_role('button',name='นำไพ่ตำแหน่งปัจจุบันกลับสำรับ',exact=True).click();assert slots(page)==[ids[0],'',ids[1]]
  page.get_by_role('button',name='กลับมุมมองพัด',exact=False).click();drag_to_slot(page,ids[2],1);ids=[ids[0],ids[2],ids[1]];assert slots(page)==ids
  shot(page,'desktop-selected');reveal(page);shot(page,'desktop-unlock')
  assert page.locator('.ritual-card-front img').evaluate_all('(els)=>els.map(e=>e.getAttribute("src"))')==['/cards/web/'+i+'.webp' for i in ids]
  unlock(page);shot(page,'desktop-reading');record('drag to chosen slot, drop outside returns, remove keeps slots, reveal and unlock retain exact identities')
  before_summary=page.get_by_test_id('reading-summary').inner_text()
  expect(page.locator('[data-reading-id]')).to_have_count(3);assert all(i in page.locator('[data-reading-id]').evaluate_all('(els)=>els.map(e=>e.dataset.readingId)') for i in ids)
  assert 'คุยกัน' in before_summary
  page.reload();phase(page,'topic');expect(page.locator('#reading-question')).to_have_value('');record('refresh clears question and entire round')
  # Release the desktop portrait while exercising independent mobile contexts.
  page.goto('about:blank')
  # One complete touch-sized flow per acceptance viewport.
  for width in [360,390,430]:
   mobile=browser.new_context(viewport={'width':width,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce')
   m=mobile.new_page();attach(m);setup(m,category='การงาน',situation='มองหางานใหม่',question='อยากเปลี่ยนงาน');no_overflow(m);stop(m)
   scroll=m.locator('.ritual-fan-scroll');before_x=scroll.evaluate('(e)=>e.scrollLeft');scroll.evaluate('(e)=>e.scrollLeft+=300');assert scroll.evaluate('(e)=>e.scrollLeft')!=before_x
   # Simulate a drag gesture with a synthetic click afterward; must not select.
   btn=m.locator('[data-deck-id]').nth(35)
   btn.dispatch_event('pointerdown',{'clientX':180,'clientY':600,'pointerId':1})
   btn.dispatch_event('pointerup',{'clientX':60,'clientY':600,'pointerId':1})
   btn.dispatch_event('click',{'detail':1});expect(m.locator('.is-candidate')).to_have_count(0)
   touch_drag_to_slot(m,'the-magician',0);grid(m);pick(m,'the-fool');pick(m,'the-high-priestess');shot(m,f'mobile-{width}-selected');no_overflow(m)
   for position in ['อนาคต','อดีต','ปัจจุบัน']:m.get_by_role('button',name='เปิดไพ่ตำแหน่ง'+position,exact=True).click()
   phase(m,'locked');expect(m.locator('.ritual-slot-card.is-open')).to_have_count(3)
   expect(m.locator('.ritual-placeholder')).to_have_count(2);unlock(m);shot(m,f'mobile-{width}-reading');assert 'มองหางานใหม่' in m.get_by_test_id('reading-summary').inner_text();expect(m.locator('[data-reading-id]')).to_have_count(3)
   assert all('รอคำอ่าน' in t for t in m.locator('.ritual-reading-entries article>p').all_inner_texts())
   no_overflow(m);record(f'{width}px touch drag to slot, open by tap, reduced motion, drag guard, placeholders and work demo');mobile.close()
  # Keyboard targeting and resize while a selection exists.
  setup(page);stop(page)
  page.locator('[data-deck-id]').nth(38).focus();page.keyboard.press('ArrowRight');expect(page.locator('.is-candidate')).to_have_count(1)
  page.get_by_role('button',name='เลือกใบนี้',exact=False).focus();page.keyboard.press('Enter');expect(page.locator('.ritual-flight')).to_have_count(0)
  retained=page.locator('[data-slot="0"]').get_attribute('data-card-id');page.set_viewport_size({'width':390,'height':844});no_overflow(page);assert page.locator('[data-slot="0"]').get_attribute('data-card-id')==retained
  record('keyboard selection and resize preserve chosen card')
  # Reduced motion preference changed during a running shuffle.
  setup(page);page.emulate_media(reduced_motion='reduce');stop(page);record('live reduced-motion preference change')
  # Motion download failure must leave a usable static flow.
  fallback=browser.new_context();f=fallback.new_page();attach(f);f.route('**/gsap.min.js',lambda route:route.abort());setup(f);stop(f);record('missing animation library falls back to selectable deck');fallback.close()
  assert not report['errors'],report['errors'];assert not report['failed_requests'],report['failed_requests'];assert not report['external_requests'],report['external_requests']
  report['passed']=True
 finally:
  (OUT/'ui-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');browser.close()
print(json.dumps({'passed':report.get('passed',False),'checks':len(report['checks'])}),flush=True)
