"""Focused regression for interruption during opening/closing (local browser only)."""
from pathlib import Path
import json,sys
from playwright.sync_api import sync_playwright,expect
OUT=Path(sys.argv[1] if len(sys.argv)>1 else '/private/tmp/mmkt-reveal-qa');OUT.mkdir(exist_ok=True)
errors=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True)
 page=b.new_page(viewport={'width':1440,'height':1000},reduced_motion='no-preference')
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:3010',wait_until='networkidle')
 page.locator('.draw-button').click()
 expect(page.locator('.reveal-layer')).to_have_attribute('data-state','opening',timeout=15000)
 page.keyboard.press('Escape')
 expect(page.locator('.reveal-layer')).to_have_count(0,timeout=4000)
 # Closing no longer turns the card to its back: it stays face up in her hand (owner's request).
 expect(page.frame_locator('.room-window iframe').locator('#card-front')).to_have_css('opacity','1')
 card=page.locator('#reading-details').get_attribute('data-card-id')
 page.locator('.stage-reopen').click()
 expect(page.locator('.reveal-layer')).to_have_attribute('data-state','open',timeout=4000)
 expect(page.locator('.reveal-layer')).to_have_attribute('data-card-id',card)
 page.get_by_role('button',name='อ่านความหมายทั้งหมดด้านล่าง').click()
 expect(page.locator('.reveal-layer')).to_have_attribute('data-state','closing')
 page.emulate_media(reduced_motion='reduce')
 expect(page.locator('.reveal-layer')).to_have_count(0)
 page.wait_for_function("document.querySelector('#reading-details').getBoundingClientRect().top < 120")
 expect(page.frame_locator('.room-window iframe').locator('#card-front')).to_have_css('opacity','1')
 page.locator('.result-card-toggle').click()
 expect(page.locator('.reveal-layer')).to_have_attribute('data-state','open')
 expect(page.locator('.reveal-layer')).to_have_attribute('data-card-id',card)
 page.screenshot(path=str(OUT/'final-reveal.png'))
 page.keyboard.press('Escape')
 expect(page.locator('.reveal-layer')).to_have_count(0)
 b.close()
result={'passed':not errors,'early_close_then_reopen':True,'reduced_motion_during_close_keeps_details_scroll':True,'same_card_after_interruptions':True,'browser_errors':errors}
(OUT/'rapid-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result));assert result['passed']
