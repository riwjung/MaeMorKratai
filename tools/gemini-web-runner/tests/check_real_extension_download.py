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
   report.update({'passed':not errors,'download_state':item['state'],'mime':item['mime'],'filename':str(actual),'bytes_identical':True,'sha256':hashlib.sha256(actual.read_bytes()).hexdigest(),'browser_errors':errors,'blob_to_data_to_download':True})
  except Exception as e:
   report['error']=str(e)
  finally:context.close()
(OUT/'real-extension-download-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False));assert report['passed']
