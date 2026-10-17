"""Real MV3 content-script/SW/downloads test on an offline Gemini DOM fixture.
Uses a fresh throwaway browser profile. Never touches the owner's browser session.
"""
from pathlib import Path
import tempfile,json,base64,time,hashlib
from playwright.sync_api import sync_playwright,expect
from fixture_support import P,CHAT,fixture,ref
OUT=P/'tests/artifacts';downloads=OUT/'real-extension-downloads';downloads.mkdir(exist_ok=True)
report={'passed':False,'live_gemini_generation':False,'uses_real_chrome_extension':True,'api_calls':0,'images_generated':0}
with tempfile.TemporaryDirectory(prefix='mmkt-extension-') as profile:
 prefs=Path(profile)/'Default';prefs.mkdir();(prefs/'Preferences').write_text(json.dumps({'download':{'default_directory':str(downloads),'prompt_for_download':False}}))
 with sync_playwright() as pw:
  context=pw.chromium.launch_persistent_context(profile,channel='chromium',headless=True,accept_downloads=True,downloads_path=str(downloads),args=['--disable-extensions-except='+str(P/'extension'),'--load-extension='+str(P/'extension')])
  try:
   context.route('https://gemini.google.com/**',lambda route:route.fulfill(body=fixture,content_type='text/html'))
   page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(CHAT)
   expect(page.locator('#mmkt-card-runner').locator('#status')).to_contain_text('พร้อม',timeout=15000)
   page.locator('#mmkt-card-runner').locator('#mode').select_option('legacy');expect(page.locator('#mmkt-card-runner').locator('#status')).to_contain_text('เปิดคิวเดิมแล้ว')
   page.evaluate('base64=>{const bytes=Uint8Array.from(atob(base64),c=>c.charCodeAt(0));window.FIXTURE_IMAGE=URL.createObjectURL(new Blob([bytes],{type:"image/jpeg"}));window.SCENARIO="normal";}',base64.b64encode(ref).decode())
   page.locator('#mmkt-card-runner').get_by_role('button',name='เริ่มอัตโนมัติ').click()
   expect(page.locator('#mmkt-card-runner').locator('#status')).to_contain_text('จบรอบแล้ว',timeout=15000)
   sw=context.service_workers[0] if context.service_workers else context.wait_for_event('serviceworker')
   state=sw.evaluate('async()=>{const k="mmkt-card-runner-v1-c1051ca2e5090320";return (await chrome.storage.local.get(k))[k]}')
   card=state['cards']['the-magician'];assert card['status']=='downloaded',card
   item=sw.evaluate('async id=>(await chrome.downloads.search({id}))[0]',card['downloadId'])
   assert item['state']=='complete' and item['mime']=='image/jpeg',{'state':item['state'],'mime':item['mime']}
   actual=Path(item['filename']);assert actual.is_file(),str(actual)
   assert actual.read_bytes()==ref,'Downloaded bytes changed'
   assert page.evaluate('sent.length')==1
   sw.evaluate('()=>{const original=chrome.downloads.download.bind(chrome.downloads);globalThis.requestedFilenames=[];chrome.downloads.download=(options,...args)=>{requestedFilenames.push(options.filename);return original(options,...args)}}')
   panel=page.locator('#mmkt-card-runner');panel.locator('#mode').select_option('new');expect(panel.locator('#status')).to_contain_text('เปิดคิวชื่อไพ่แล้ว');panel.locator('#candidate').check();panel.locator('#start').click();expect(panel.locator('#status')).to_contain_text('จบรอบแล้ว',timeout=15000)
   titled=sw.evaluate('async()=>{const k="mmkt-card-runner-title-v1-c1051ca2e5090320";return (await chrome.storage.local.get(k))[k].cards["the-magician"]}')
   title_item=sw.evaluate('async id=>(await chrome.downloads.search({id}))[0]',titled['downloadId'])
   assert sw.evaluate('requestedFilenames.at(-1)')=='MaeMorKratai/cards-titled/v1/the-magician.jpg'
   assert Path(title_item['filename']).read_bytes()==ref and title_item['filename']!=item['filename']
   assert actual.read_bytes()==ref and page.evaluate('sent.length')==2
   report['title_output_separate_and_original_preserved']=True
   panel.locator('#mode').select_option('repair');expect(panel.locator('#status')).to_contain_text('เปิดคิวซ่อมภาพแล้ว');panel.locator('#source-card').select_option('the-emperor');panel.locator('#source-file').set_input_files({'name':'the-emperor.jpg','mimeType':'image/jpeg','buffer':ref});expect(panel.locator('#status')).to_contain_text('เลือกจุดแก้');panel.locator('#queue-repair').click();expect(panel.locator('#status')).to_contain_text('เข้าคิวซ่อมแล้ว');panel.locator('#start').click();expect(panel.locator('#status')).to_contain_text('จบรอบแล้ว',timeout=15000)
   repair=sw.evaluate('async()=>{const k="mmkt-card-runner-repair-v1-c1051ca2e5090320";return (await chrome.storage.local.get(k))[k].cards["the-emperor"]}')
   repair_item=sw.evaluate('async id=>(await chrome.downloads.search({id}))[0]',repair['downloadId'])
   assert sw.evaluate('requestedFilenames.at(-1)')=='MaeMorKratai/cards-repaired/v1/the-emperor.jpg'
   assert Path(repair_item['filename']).read_bytes()==ref and repair_item['filename'] not in (item['filename'],title_item['filename'])
   assert actual.read_bytes()==ref and page.evaluate('sent.length')==3
   report['repair_output_separate_and_original_preserved']=True

   report.update({'passed':not errors,'download_state':item['state'],'mime':item['mime'],'filename':str(actual),'bytes_identical':True,'sha256':hashlib.sha256(actual.read_bytes()).hexdigest(),'browser_errors':errors,'blob_to_data_to_download':True})
  except Exception as e:
   import traceback
   report['error']=repr(e);report['traceback']=traceback.format_exc()
  finally:context.close()
(OUT/'real-extension-download-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False));assert report['passed']
