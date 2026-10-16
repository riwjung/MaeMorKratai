from pathlib import Path
import json
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parents[1]
errors=[];failed=[]
with sync_playwright() as pw:
 b=pw.chromium.launch()
 page=b.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('response',lambda r:failed.append({'url':r.url,'status':r.status}) if r.status>=400 else None)
 page.goto('http://127.0.0.1:3010',wait_until='networkidle')
 page.get_by_role('button',name='ตั้งจิต แล้วเปิดไพ่').wait_for()
 page.screenshot(path=str(P/'artifacts/desktop.png'),full_page=True)
 assert page.locator('.gallery-card').count()==5
 page.get_by_label('วันนี้อยากมองความรักในมุมไหน').select_option('คุยกัน')
 page.get_by_role('button',name='ตั้งจิต แล้วเปิดไพ่').click()
 assert page.locator('.draw-button').is_disabled()
 page.locator('.reading-result').wait_for(timeout=15000)
 chosen=page.locator('.reading-result').get_attribute('data-card-id')
 f=page.frame_locator('.room-window iframe')
 href=f.locator('#card-front image').get_attribute('href')
 assert chosen+'.svg' in href,(chosen,href)
 meaning=page.locator('.meaning').inner_text()
 card=next(c for c in json.loads((P/'lib/cards.json').read_text()) if c['id']==chosen)
 assert meaning==card['meanings']['คุยกัน']
 page.locator('.reading-result').screenshot(path=str(P/'artifacts/reading-result.png'))
 page.get_by_role('button',name='ดูไพ่ The Fool',exact=True).click()
 page.get_by_role('dialog').wait_for()
 page.wait_for_timeout(700)
 assert page.frame_locator('.animated-card iframe').locator('[data-composition-id="the-fool"]').count()==1
 page.screenshot(path=str(P/'artifacts/card-detail.png'))
 page.keyboard.press('Escape')
 assert page.get_by_role('dialog').count()==0
 page.set_viewport_size({'width':390,'height':844})
 page.goto('http://127.0.0.1:3010',wait_until='networkidle')
 page.get_by_role('button',name='ตั้งจิต แล้วเปิดไพ่').wait_for()
 assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 page.screenshot(path=str(P/'artifacts/mobile.png'),full_page=True)
 page.emulate_media(reduced_motion='reduce')
 page.get_by_role('button',name='ตั้งจิต แล้วเปิดไพ่').click()
 page.locator('.reading-result').wait_for(timeout=3000)
 reduced_id=page.locator('.reading-result').get_attribute('data-card-id')
 assert reduced_id+'.svg' in page.frame_locator('.room-window iframe').locator('#card-front image').get_attribute('href')
 b.close()
out={'passed':not errors and not failed,'browser_errors':errors,'failed_requests':failed,'desktop_width':1440,'mobile_width':390,'no_mobile_overflow':True,'animated_draw_card':chosen,'reduced_motion_card':reduced_id,'card_in_hand_matches_result':True,'meaning_matches_source_status':True,'gallery_cards':5}
(P/'artifacts/web-check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(out,ensure_ascii=False))
assert out['passed']
