"""Short viewport-only previews; screenshots are captured by the acceptance suite separately."""
from pathlib import Path
import os, subprocess
from playwright.sync_api import sync_playwright,expect
URL=os.getenv('MMKT_TEST_URL','http://127.0.0.1:3012')
OUT=Path(__file__).resolve().parents[1]/'artifacts/reading-motion'
with sync_playwright() as p:
 b=p.chromium.launch(channel=os.getenv("MMKT_BROWSER_CHANNEL") or None)
 for label,width,height in [('desktop',1440,1000),('mobile',390,844)]:
  context=b.new_context(viewport={'width':width,'height':height},is_mobile=width<500,has_touch=width<500,record_video_dir=str(OUT/'videos'),record_video_size={'width':width,'height':height})
  page=context.new_page();page.goto(URL+'/reading/')
  expect(page.locator('.ritual-rabbit')).to_have_attribute('data-ready','true',timeout=8000)
  if width<500:page.locator('.ritual-welcome-art').scroll_into_view_if_needed()
  page.wait_for_timeout(3200)
  page.get_by_role('button',name='ไปต่อ',exact=False).click();page.get_by_role('button',name='พร้อมแล้ว',exact=False).click();page.wait_for_timeout(3200)
  page.locator('.ritual-stop').click();expect(page.locator('main')).to_have_attribute('data-phase','selecting',timeout=15000)
  page.wait_for_timeout(1400)
  page.get_by_role('button',name='ดูครบทุกใบ',exact=False).click()
  # Choose three existing illustrated cards in this isolated QA session.
  for card_id in ['the-fool','the-lovers','queen-of-swords']:
   page.locator(f'[data-deck-id="{card_id}"]').click();page.get_by_role('button',name='เลือกใบนี้',exact=False).click();expect(page.locator('.ritual-flight')).to_have_count(0)
  page.locator('.ritual-slots').scroll_into_view_if_needed();page.wait_for_timeout(2600)
  for slot in [2,0,1]:page.locator(f'[data-slot="{slot}"] .ritual-slot-open').click();page.wait_for_timeout(800)
  page.wait_for_timeout(1200)
  video=page.video;context.close();dest=OUT/f'{label}-preview.webm';video.save_as(str(dest))
  subprocess.run(['ffmpeg','-y','-v','error','-i',str(dest),'-an','-c:v','libx264','-crf','23','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/f'{label}-preview.mp4')],check=True)
  print('RECORDED',label,flush=True)
 b.close()
