from pathlib import Path
import json
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parents[1];root=P.parent/'tarot-cards'
cards=json.loads((P/'lib/cards.json').read_text());checks=[]
with sync_playwright() as pw:
 b=pw.chromium.launch()
 page=b.new_page(viewport={'width':600,'height':960});errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 for c in cards:
  d=root/c['id'];page.goto((d/'index.html').as_uri());page.wait_for_timeout(120)
  duration=page.evaluate('(id)=>window.__timelines[id].duration()',c['id']);assert duration==6
  page.evaluate('(id)=>{window.__timelines[id].seek(3,false);return true}',c['id'])
  page.screenshot(path=str(d/'preview.png'))
  checks.append({'id':c['id'],'duration':duration,'width':600,'height':960,'preview':str(d/'preview.png')})
 # Exercise every possible result using deterministic entropy ONLY in this isolated QA browser.
 pg=b.new_page(viewport={'width':390,'height':844},reduced_motion='reduce')
 pg.on('pageerror',lambda e:errors.append(str(e)))
 pg.goto('http://127.0.0.1:3010',wait_until='networkidle')
 pg.locator('.draw-button:not([disabled])').wait_for()
 for i,c in enumerate(cards):
  pg.evaluate('(i)=>{crypto.getRandomValues=(a)=>{a[0]=i;return a;}}',i)
  pg.locator('.draw-button').click()
  pg.locator('.reading-result[data-card-id="'+c['id']+'"]').wait_for(timeout=3000)
  href=pg.frame_locator('.room-window iframe').locator('#card-front image').get_attribute('href')
  assert c['id']+'.svg' in href
  for state,meaning in c['meanings'].items():
   pg.locator('#context').select_option(state)
   assert pg.locator('.meaning').inner_text()==meaning
 # Modal keyboard cycle and close.
 pg.get_by_role('button',name='ดูไพ่ The Lovers',exact=True).click()
 pg.get_by_role('button',name='ปิดรายละเอียดไพ่').focus()
 pg.keyboard.press('Shift+Tab')
 assert pg.locator('.card-modal .text-link').evaluate('(e)=>document.activeElement===e')
 pg.keyboard.press('Escape');assert pg.get_by_role('dialog').count()==0
 b.close()
assert not errors
out={'passed':True,'cards':checks,'browser_errors':errors,'all_five_draws_match_art':True,'thirty_readings_match_source':True,'modal_keyboard_cycle':True}
(P/'artifacts/cards-check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps({'passed':True,'cards':len(checks),'all_five_draws_match_art':True,'thirty_readings_match_source':True}))
