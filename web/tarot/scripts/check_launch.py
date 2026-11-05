"""Public launch QA; forced entropy exists only in isolated browser test contexts."""
import json,os,hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright,expect

root=Path(__file__).resolve().parents[1]
url=os.environ.get('MMKT_TEST_URL','http://127.0.0.1:3014').rstrip('/')
out=root/'artifacts/launch-20261105-ux';out.mkdir(parents=True,exist_ok=True)
cards=json.loads((root/'lib/reading-cards.json').read_text())
daily={card['card_id']:card for card in json.loads((root/'lib/daily-cards.json').read_text())['cards']}
assert len(cards)==len(daily)==78 and {card['id'] for card in cards}==set(daily)
report={'url':url,'passed':False,'checks':[],'errors':[],'badResponses':[]}
def overflow(page):
 assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
def attach(page):
 page.on('pageerror',lambda e:report['errors'].append(str(e)))
 page.on('response',lambda r:report['badResponses'].append({'url':r.url,'status':r.status}) if r.status>=400 else None)
 page.add_init_script('window.__qaIndex=0;window.__qaDraws=0;crypto.getRandomValues=a=>{window.__qaDraws++;a.fill(0);a[0]=window.__qaIndex;return a;}')
def draw(page,index):
 card=cards[index];reading=daily[card['id']]['content'];page.evaluate('(i)=>window.__qaIndex=i',index)
 page.locator('.draw-button').click()
 expect(page.locator('.reveal-layer')).to_have_attribute('data-card-id',card['id'],timeout=18000)
 expect(page.locator('#reveal-title')).to_have_text(card['name'])
 expect(page.locator('#reveal-meaning')).to_have_text(reading['theme']); expect(page.locator('.reveal-detail')).to_have_text(reading['rabbit_message'])
 if card['art']:
  expect(page.locator('.reveal-front img')).to_have_attribute('src',card['art'])
  expect(page.locator('.reveal-layer')).to_have_attribute('data-state','open',timeout=5000)
  assert page.locator('.reveal-front img').evaluate('''img=>{const r=img.getBoundingClientRect();return Math.abs(r.height-r.width*img.naturalHeight/img.naturalWidth)<0.15&&getComputedStyle(img).boxShadow==='none'}'''),card['id']
 else:expect(page.locator('.reveal-front .card-name-fallback')).to_have_text(card['name'])
 page.get_by_role('button',name='ปิดไพ่และเก็บกลับ',exact=True).click()
 expect(page.locator('.reveal-layer')).to_have_count(0,timeout=5000)
 expect(page.locator('#reading-details')).to_have_attribute('data-card-id',card['id'])
 for heading in ['ภาพรวมวันนี้','การงาน','การเงิน','ความรัก · คนโสด','ข้อความจากแม่หมอ']:
  expect(page.locator('#reading-details')).to_contain_text(heading)
 for text in [reading['overview'],reading['work'],reading['money'],reading['love_by_status']['single'],reading['rabbit_message'],reading['colors'],reading['affirmation']]:
  assert text.replace('**','') in page.locator('#reading-details').text_content()

with sync_playwright() as p:
 browser=p.chromium.launch();context=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce');page=context.new_page();attach(page)
 page.goto(url,wait_until='networkidle');expect(page.locator('.draw-button')).to_be_enabled(timeout=15000)
 expect(page.locator('.stage-bottom .draw-button')).to_have_count(1)
 expect(page.locator('.stage-bottom #context')).to_have_count(1)
 expect(page.locator('.stage-reopen')).to_have_count(0)
 expect(page.locator('.gallery-card')).to_have_count(78)
 assert page.locator('.gallery-card img').count()==sum(bool(c['art']) for c in cards)
 overflow(page);page.screenshot(path=str(out/'desktop.png'))
 for i in range(78):
  draw(page,i)
  if (i+1)%10==0:print('draws',i+1,flush=True)
 report['checks'].append('78 draws show source daily theme, overview, work, money, love, message, colors and affirmation; image/name-only faces')
 before=page.evaluate('window.__qaDraws');page.get_by_role('button',name='เปิดไพ่ใบเดิมจากมือแม่หมอ',exact=True).click()
 expect(page.locator('#reveal-title')).to_have_text(cards[-1]['name'])
 assert page.evaluate('window.__qaDraws')==before
 page.keyboard.press('Escape');expect(page.locator('.reveal-layer')).to_have_count(0)
 report['checks'].append('Reopen same card without new draw; Escape closes')
 expect(page.locator('.three-card-entry')).to_contain_text('เปิดไพ่ 3 ใบ');assert page.get_by_text('Coming soon').count()==0
 response=page.goto(url+'/reading/');assert response.status==200
 expect(page.locator('main.ritual')).to_have_attribute('data-phase','topic');expect(page.locator('.ritual-continue')).to_be_visible()
 page.get_by_role('link',name='กลับหน้าแรกแม่หมอกระต่าย').click();expect(page.locator('#context')).to_be_visible()
 report['checks'].append('Home links to the 3-card room; direct /reading/ opens it; return to home works')
 for c in cards:
  if c['art']:
   response=context.request.get(url+c['art']);assert response.status==200
   assert hashlib.sha256(response.body()).digest()==hashlib.sha256((root/'public'/c['art'].lstrip('/')).read_bytes()).digest()
 report['checks'].append('Every v3 card asset served with expected bytes')
 context.close();browser.close()
 for name,engine in [('chromium',p.chromium),('webkit',p.webkit)]:
  browser=engine.launch();context=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce')
  page=context.new_page();attach(page);page.goto(url,wait_until='networkidle');expect(page.locator('.draw-button')).to_be_enabled(timeout=15000)
  overflow(page);page.screenshot(path=str(out/(name+'-mobile.png')))
  for i in [0,11,77]:draw(page,i);overflow(page)
  page.locator('#reading-details').screenshot(path=str(out/(name+'-name-only.png')))
  page.goto(url+'/reading/');expect(page.locator('.ritual-continue')).to_be_visible();overflow(page);page.screenshot(path=str(out/(name+'-reading.png')))
  report['checks'].append(name+' mobile: image, new image, name-only, no overflow, 3-card room')
  context.close();browser.close()
 # Real animation path remains usable on desktop, independent of reduced-motion QA.
 browser=p.chromium.launch();context=browser.new_context(viewport={'width':1280,'height':900});page=context.new_page();attach(page)
 page.goto(url,wait_until='networkidle');expect(page.locator('.draw-button')).to_be_enabled(timeout=15000);draw(page,13)
 report['checks'].append('Desktop animated draw completes');context.close();browser.close()
 browser=p.chromium.launch();context=browser.new_context(reduced_motion='reduce');page=context.new_page();attach(page)
 page.route('**/cards/v3/the-fool-*',lambda route:route.abort())
 page.goto(url,wait_until='networkidle');expect(page.locator('.draw-button')).to_be_enabled(timeout=15000)
 page.locator('.draw-button').click()
 expect(page.locator('.reveal-front .card-name-fallback')).to_have_text(cards[0]['name'],timeout=18000)
 expect(page.locator('#reveal-meaning')).to_have_text(daily[cards[0]['id']]['content']['theme'])
 assert page.frame_locator('iframe').locator('#card-front tspan').all_text_contents()==cards[0]['name'].split(' ')
 report['checks'].append('Blocked card image falls back to name in reveal and mascot hand')
 context.close();browser.close()
 assert not report['errors'],report['errors']
 assert not report['badResponses'],report['badResponses']
 report['passed']=True
(out/('production-check.json' if 'vercel.app' in url else 'local-check.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False),flush=True)
