"""Exercise motion fallbacks and interruptible drag without changing the deck."""
import json, os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
URL=os.getenv('MMKT_TEST_URL','http://127.0.0.1:3012')
OUT=Path(__file__).resolve().parents[1]/'artifacts/reading-motion/interruptions-check.json'
checks=[]
def ok(name):checks.append(name);print('PASS',name,flush=True)
def phase(p,v):expect(p.locator('main.ritual')).to_have_attribute('data-phase',v,timeout=15000)
def begin(p):
 p.goto(URL+'/reading/');p.get_by_role('button',name='ไปต่อ',exact=False).click();p.get_by_role('button',name='พร้อมแล้ว',exact=False).click();phase(p,'shuffling')
with sync_playwright() as w:
 b=w.chromium.launch();p=b.new_page(viewport={'width':1200,'height':1000})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.add_init_script("const original=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(k,...args){return String(k).includes('webgl')?null:original.call(this,k,...args)}")
 try:
  begin(p);expect(p.locator('.ritual-shuffle-card')).to_have_count(24)
  a=p.locator('.ritual-shuffle-card').nth(8).evaluate('(e)=>e.style.transform');p.wait_for_timeout(300)
  assert a!=p.locator('.ritual-shuffle-card').nth(8).evaluate('(e)=>e.style.transform')
  p.locator('.ritual-stop').click();phase(p,'spreading');p.locator('.ritual-motion-toggle').click();phase(p,'selecting')
  p.locator('.ritual-motion-toggle').click();ok('WebGL unavailable uses animated DOM deck; pause during spread completes')
  p.get_by_role('button',name='ดูครบทุกใบ',exact=False).click()
  def lift():
   card=p.locator('.ritual-deck-card:not(:disabled)').first;card.scroll_into_view_if_needed();box=card.bounding_box();x=box['x']+box['width']/2;y=box['y']+box['height']/2
   p.mouse.move(x,y);p.wait_for_timeout(300);box=card.bounding_box();x=box['x']+box['width']/2;y=box['y']+box['height']/2
   p.mouse.move(x,y);p.mouse.down();p.mouse.move(x,y-25,steps=4);expect(p.locator('.ritual-ghost')).to_have_count(1)
  def empty():assert p.locator('[data-slot]').evaluate_all('(els)=>els.every(e=>!e.dataset.cardId)')
  lift();p.keyboard.press('Escape');p.mouse.up();expect(p.locator('.ritual-ghost')).to_have_count(0);empty();ok('Escape cancels drag without selecting a card')
  lift();p.set_viewport_size({'width':1100,'height':900});p.mouse.up();expect(p.locator('.ritual-ghost')).to_have_count(0);empty();ok('resize cancels drag and preserves empty slots')
  lift();p.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'))");p.mouse.up();expect(p.locator('.ritual-ghost')).to_have_count(0);empty()
  p.evaluate("delete document.hidden;document.dispatchEvent(new Event('visibilitychange'))");ok('hidden tab cancels active drag safely')
  lift();p.evaluate("dispatchEvent(new PointerEvent('pointercancel',{pointerId:1}))");p.mouse.up();expect(p.locator('.ritual-ghost')).to_have_count(0);empty();ok('pointer cancel returns card from current location')
  p.locator('.ritual-deck-card:not(:disabled)').first.click();p.get_by_role('button',name='เลือกใบนี้',exact=False).click();p.locator('.ritual-motion-toggle').click();expect(p.locator('.ritual-flight')).to_have_count(0)
  for _ in range(2):p.locator('.ritual-deck-card:not(:disabled)').first.click();p.get_by_role('button',name='เลือกใบนี้',exact=False).click()
  ids=p.locator('[data-slot]').evaluate_all('(els)=>els.map(e=>e.dataset.cardId)');assert len(set(ids))==3
  p.get_by_role('button',name='เปิดไพ่ทั้งสามใบ',exact=False).click();phase(p,'locked');p.get_by_role('button',name='ปลดล็อกคำอ่านฉบับเต็ม',exact=False).click();phase(p,'reading')
  assert p.locator('[data-reading-id]').evaluate_all('(els)=>els.map(e=>e.dataset.readingId)')==ids;ok('flight interrupted by pause retains selection and completes no-WebGL flow')
  assert not errors,errors
 finally:
  p.screenshot(path=str(OUT.parent/'interruptions-last.png'),full_page=True)
  OUT.write_text(json.dumps({'checks':checks,'errors':errors},ensure_ascii=False,indent=2));b.close()
