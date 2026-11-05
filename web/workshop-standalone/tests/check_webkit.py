"""WebKit mobile layout + real MediaRecorder with a synthetic Web Audio source.
This is not a physical iPhone/microphone test.
"""
import asyncio
from playwright.async_api import async_playwright
from check_browser import BASE, login
async def main():
 async with async_playwright() as p:
  browser=await p.webkit.launch()
  context=await browser.new_context(viewport={'width':390,'height':844},is_mobile=True,device_scale_factor=3)
  page=await context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  await login(page)
  await page.get_by_role('heading',name='เก็บเคสนี้เรียบร้อยแล้ว',exact=True).wait_for()
  await page.get_by_role('button',name='เคสถัดไป',exact=False).click()
  await page.get_by_role('heading',name='จาก 3 ใบนี้ คุณจะบอกลูกดวงว่า…',exact=True).wait_for()
  await page.get_by_role('button',name='เคสถัดไป',exact=False).click()
  await page.get_by_role('heading',name='ความสัมพันธ์นี้มีแนวโน้มจะจบลงไหม?',exact=True).wait_for()
  assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  await page.evaluate('''()=>{navigator.mediaDevices.getUserMedia=async()=>{
   const ctx=new AudioContext();await ctx.resume();const oscillator=ctx.createOscillator();
   const dest=ctx.createMediaStreamDestination();oscillator.connect(dest);oscillator.start();
   window.testAudioContext=ctx;return dest.stream;
  }}''')
  await page.get_by_role('button',name='เริ่มอัดเสียง',exact=True).click()
  await page.get_by_role('button',name='หยุดอัด',exact=True).wait_for()
  await page.wait_for_timeout(1700)
  await page.get_by_role('button',name='หยุดอัด',exact=True).click()
  await page.locator('.local-take audio').wait_for()
  await page.locator('.consent input').check()
  await page.get_by_role('button',name='บันทึกร่าง',exact=True).click()
  await page.get_by_role('status').filter(has_text='บันทึกร่างลงฐานข้อมูลแล้ว').wait_for()
  response=await context.request.get(BASE+'/api/workshop/cases/case-03');detail=await response.json()
  assert detail['snapshot']['baseline']['audioId']
  audio=await context.request.get(BASE+'/api/workshop/audio/'+detail['snapshot']['baseline']['audioId'],headers={'Range':'bytes=0-63'})
  assert audio.status==206 and len(await audio.body())==64
  await page.locator('.saved-audio audio').evaluate('(e)=>e.play()')
  await page.wait_for_timeout(500)
  assert await page.locator('.saved-audio audio').evaluate('(e)=>e.currentTime>0 && !e.error')
  await page.screenshot(path='artifacts/webkit-mobile.png',full_page=True)
  assert not errors,errors
  print('PASS: WebKit mobile, MediaRecorder synthetic audio, private upload, playback with byte ranges; MIME:',audio.headers['content-type'])
  await browser.close()
asyncio.run(main())
