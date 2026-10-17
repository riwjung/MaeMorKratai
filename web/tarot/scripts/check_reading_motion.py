"""Motion, lifecycle and accessibility acceptance against a local production export."""
import json, os, traceback
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
URL=os.getenv('MMKT_TEST_URL','http://127.0.0.1:3012')
OUT=Path(__file__).resolve().parents[1]/'artifacts/reading-motion'
OUT.mkdir(parents=True,exist_ok=True)
report={'checks':[], 'errors':[], 'videos':[], 'screenshots':[]}
def ok(name):report['checks'].append(name);print('PASS',name,flush=True)
def shot(page,name):
 page.screenshot(path=str(OUT/(name+'.png')),full_page=True);report['screenshots'].append(name+'.png')
def phase(page,value):expect(page.locator('main.ritual')).to_have_attribute('data-phase',value,timeout=12000)
def begin(page):
 page.get_by_role('button',name='ไปต่อ',exact=False).click()
 page.get_by_role('button',name='พร้อมแล้ว',exact=False).click();phase(page,'shuffling')
def stop(page):page.locator('.ritual-stop').click();phase(page,'selecting')
def pick(page,n):
 page.locator('.ritual-deck-card:not(:disabled)').nth(n).click()
 page.get_by_role('button',name='เลือกใบนี้',exact=False).click()
 expect(page.locator('.ritual-flight')).to_have_count(0)
def ids(page):return page.locator('[data-slot]').evaluate_all('(els)=>els.map(e=>e.dataset.cardId)')
def rabbit(page):
 expect(page.locator('.ritual-rabbit')).to_have_attribute('data-ready','true')
 return page.frames[1]
def pose(frame):return frame.locator('#rabbit').evaluate('(e)=>getComputedStyle(e).transform')
def transform(page,selector):return page.locator(selector).first.evaluate('(e)=>getComputedStyle(e).transform')
with sync_playwright() as p:
 b=p.chromium.launch()
 try:
  context=b.new_context(viewport={'width':1440,'height':1000},record_video_dir=str(OUT/'videos'),record_video_size={'width':1440,'height':1000})
  page=context.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)))
  page.goto(URL+'/reading/');f=rabbit(page)
  a=pose(f);ca=transform(page,'.ritual-card-bob');page.wait_for_timeout(550)
  assert pose(f)!=a and transform(page,'.ritual-card-bob')!=ca
  f.evaluate('window.__blinkSamples=[];window.__blinkTimer=setInterval(()=>window.__blinkSamples.push(Number(getComputedStyle(document.querySelector("#blink")).opacity)),20)')
  page.wait_for_timeout(4200);assert f.evaluate('Math.max(...window.__blinkSamples)')>.8;f.evaluate('clearInterval(window.__blinkTimer)')
  shot(page,'desktop-welcome');ok('shared rabbit breathes and blinks; welcome cards float')
  # Neither a forged origin nor a same-origin non-parent source can control the portrait.
  f.evaluate('''()=>{dispatchEvent(new MessageEvent('message',{origin:'https://invalid.example',source:parent,data:{type:'mmkt:portrait-motion',playing:false}}));dispatchEvent(new MessageEvent('message',{origin:location.origin,source:window,data:{type:'mmkt:portrait-motion',playing:false}}))}''')
  a=pose(f);page.wait_for_timeout(250);assert pose(f)!=a
  page.evaluate("document.querySelector('iframe').contentWindow.postMessage({type:'mmkt:draw',cardId:'the-fool'},location.origin)")
  page.wait_for_timeout(300);assert f.locator('#show-card').evaluate('(e)=>getComputedStyle(e).opacity')=='0';ok('portrait bridge rejects foreign origin/source and never draws a home-page card')
  page.locator('.ritual-motion-toggle').click();page.wait_for_timeout(100);a=pose(f)
  page.wait_for_timeout(350);assert pose(f)==a;assert transform(page,'.ritual-card-bob')=='none'
  page.locator('.ritual-motion-toggle').click();page.wait_for_timeout(250);assert pose(f)!=a;ok('pause/play controls rabbit and CSS decorations')
  page.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'))")
  page.wait_for_timeout(100);a=pose(f);page.wait_for_timeout(300);assert pose(f)==a
  page.evaluate("delete document.hidden;document.dispatchEvent(new Event('visibilitychange'))");page.wait_for_timeout(300);assert pose(f)!=a;ok('visibility lifecycle pauses and resumes mascot')
  begin(page);page.wait_for_timeout(1800);shot(page,'desktop-shuffle');page.locator('.ritual-stop').click()
  page.locator('.ritual-motion-toggle').click();phase(page,'selecting')
  page.locator('.ritual-motion-toggle').click();page.get_by_role('button',name='ดูครบทุกใบ',exact=False).click()
  pick(page,0);pick(page,1);pick(page,2)
  selected=ids(page);page.locator('.ritual-slots').scroll_into_view_if_needed();page.wait_for_timeout(350)
  before=page.locator('.ritual-slot-card').first.bounding_box();a=transform(page,'.ritual-slot .ritual-card-bob');page.wait_for_timeout(450)
  assert a!=transform(page,'.ritual-slot .ritual-card-bob');assert before==page.locator('.ritual-slot-card').first.bounding_box()
  assert page.locator('.ritual-slot .ritual-card-edge').count()==12;shot(page,'desktop-selected');ok('fixed slot hitboxes, gentle floating and four physical edges per card')
  page.locator('[data-slot="2"] .ritual-slot-open').click();page.wait_for_timeout(700)
  assert page.locator('[data-slot="2"] .ritual-card-visual').get_attribute('data-open')=='true'
  assert transform(page,'[data-slot="2"] .ritual-card-bob')=='none'
  page.get_by_role('button',name='เปิดใบที่เหลือ',exact=False).click();page.locator('.ritual-motion-toggle').click();phase(page,'locked')
  assert ids(page)==selected;page.get_by_role('button',name='ปลดล็อกคำอ่านฉบับเต็ม',exact=False).click();phase(page,'reading');shot(page,'desktop-reading')
  assert page.locator('[data-reading-id]').evaluate_all('(els)=>els.map(e=>e.dataset.readingId)')==selected
  ok('pause during gather/reveal completes; out-of-order reveal preserves card and reading identities')
  video=page.video;context.close();video.save_as(str(OUT/'desktop-motion.webm'));report['videos'].append('desktop-motion.webm')
  for width in [360,390,430]:
   context=b.new_context(viewport={'width':width,'height':844},is_mobile=True,has_touch=True,device_scale_factor=1,record_video_dir=str(OUT/'videos') if width==390 else None,record_video_size={'width':390,'height':844} if width==390 else None)
   page=context.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)))
   page.goto(URL+'/reading/');f=rabbit(page)
   page.locator('.ritual-welcome-art').scroll_into_view_if_needed();page.wait_for_timeout(500);shot(page,f'mobile-{width}-welcome')
   a=pose(f);page.wait_for_timeout(300);assert pose(f)!=a
   page.evaluate('scrollTo(0,0)');page.wait_for_timeout(300)
   expect(page.locator('.ritual-rabbit')).to_have_attribute('data-motion-active','false')
   a=pose(f);page.wait_for_timeout(250);assert pose(f)==a
   begin(page);page.wait_for_timeout(700);stop(page)
   page.get_by_role('button',name='ดูครบทุกใบ',exact=False).click()
   pick(page,0);pick(page,1);pick(page,2);selected=ids(page)
   page.locator('.ritual-slots').scroll_into_view_if_needed();shot(page,f'mobile-{width}-selected')
   page.locator('[data-slot="1"] .ritual-slot-open').click();page.wait_for_timeout(700)
   page.get_by_role('button',name='เปิดใบที่เหลือ',exact=False).click();phase(page,'locked')
   assert ids(page)==selected;assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   page.get_by_role('button',name='ปลดล็อกคำอ่านฉบับเต็ม',exact=False).click();phase(page,'reading');shot(page,f'mobile-{width}-reading')
   video=page.video;context.close()
   if video:video.save_as(str(OUT/'mobile-motion.webm'));report['videos'].append('mobile-motion.webm')
   ok(f'mobile {width}px: motion, offscreen sleep, touch selection, reveal, reading, no overflow')
  # Reduced motion + failed portrait + no WebGL are independent of the reading flow.
  context=b.new_context(reduced_motion='reduce',viewport={'width':390,'height':844});page=context.new_page()
  page.route('**/scene/index.html?presentation=portrait',lambda route:route.abort())
  page.add_init_script("const get=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(k,...args){return String(k).includes('webgl')?null:get.call(this,k,...args)}")
  page.goto(URL+'/reading/');expect(page.locator('main')).to_have_attribute('data-reduced','true')
  page.wait_for_timeout(8300);expect(page.locator('.ritual-rabbit iframe')).to_have_count(0)
  assert page.locator('.ritual-rabbit-fallback').evaluate('(e)=>e.complete&&e.naturalWidth>0')
  begin(page);stop(page);page.get_by_role('button',name='ดูครบทุกใบ',exact=False).click()
  for _ in range(3):pick(page,0)
  page.get_by_role('button',name='เปิดไพ่ทั้งสามใบ',exact=False).click();phase(page,'locked')
  page.get_by_role('button',name='ปลดล็อกคำอ่านฉบับเต็ม',exact=False).click();phase(page,'reading')
  ok('reduced motion + failed mascot + no WebGL still complete full flow');context.close()
  assert not report['errors'],report['errors']
 except Exception:
  report['failure']=traceback.format_exc();print(report['failure']);raise
 finally:
  (OUT/'motion-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));b.close()
