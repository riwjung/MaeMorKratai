"""Local-only integration QA; uses synthetic answers and fake microphone audio."""
import asyncio, json, uuid
from pathlib import Path
from playwright.async_api import async_playwright
BASE='http://127.0.0.1:3012'
OUT=Path(__file__).resolve().parents[1]/'artifacts'
async def login(page, who='reader'):
 await page.goto(BASE+'/login')
 await page.get_by_label('อีเมลที่ได้รับสิทธิ์').fill(who+'@example.test')
 await page.get_by_label('รหัสผ่าน',exact=True).fill('loopback-password')
 await page.get_by_role('button',name='เข้าห้องทดลอง',exact=True).click()

async def main():
 OUT.mkdir(exist_ok=True)
 async with async_playwright() as p:
  browser=await p.chromium.launch(args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream'])
  context=await browser.new_context(viewport={'width':1440,'height':1100},permissions=['microphone'])
  page=await context.new_page(); errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  anonymous=await context.request.get(BASE+'/api/workshop/')
  assert anonymous.status==401,anonymous.status
  await login(page)
  await page.get_by_role('heading',name='อ่านในแบบของคุณ',exact=True).wait_for()
  await page.get_by_role('heading',name='เขาพร้อมพัฒนาความสัมพันธ์ให้จริงจังไหม?',exact=True).wait_for()
  req=context.request
  async def get(path):
   r=await req.get(BASE+'/api/workshop/'+path);assert r.ok,(r.status,await r.text());return await r.json()
  async def post(path,payload,origin=True):
   return await req.post(BASE+'/api/workshop/'+path,data=payload,headers={'Origin':BASE} if origin else {})
  first=await get('cases/case-01');assert len(first['cards'])==3 and first['snapshot']['revision']==0
  assert first['cards'][-1]['id']=='knight-of-wands'
  await page.screenshot(path=str(OUT/'desktop.png'),full_page=True)
  await page.get_by_role('button',name='เริ่มอัดเสียง',exact=True).click()
  await page.get_by_role('button',name='หยุดอัด',exact=True).wait_for()
  await page.wait_for_timeout(1700)
  await page.get_by_role('button',name='หยุดอัด',exact=True).click()
  await page.locator('.local-take audio').wait_for()
  assert await page.locator('.local-take audio').evaluate('(e)=>e.src.startsWith("blob:")')
  await page.locator('.consent input').check()
  await page.get_by_role('button',name='บันทึกร่าง',exact=True).click()
  await page.get_by_role('status').filter(has_text='บันทึกร่างลงฐานข้อมูลแล้ว').wait_for()
  draft=await get('cases/case-01');assert draft['snapshot']['baseline']['audioId'] and len(draft['recordings'])==1
  audio_id=draft['snapshot']['baseline']['audioId'];audio=await req.get(BASE+'/api/workshop/audio/'+audio_id)
  assert audio.ok and len(await audio.body())>100
  partial=await req.get(BASE+'/api/workshop/audio/'+audio_id,headers={'Range':'bytes=0-31'})
  assert partial.status==206 and len(await partial.body())==32
  bad_range=await req.get(BASE+'/api/workshop/audio/'+audio_id,headers={'Range':'bytes=999999999-'})
  assert bad_range.status==416
  await page.reload();await page.locator('.saved-audio audio').wait_for()
  assert len((await get('cases/case-01'))['cards'])==3
  await page.locator('.consent input').check()
  await page.get_by_role('button',name='เก็บคำอ่าน แล้วเปิดใบที่ 4',exact=True).click()
  await page.get_by_role('heading',name='ใบขยายช่วยให้เห็นอะไรเพิ่ม?',exact=True).wait_for()
  after=await get('cases/case-01');assert len(after['cards'])==4 and after['cards'][3]['id']=='justice'
  frozen=after['snapshot']['baseline']
  payload={'requestId':str(uuid.uuid4()),'revision':after['snapshot']['revision'],'stage':'baseline','action':'save','answers':frozen,'consent':True}
  assert (await post('cases/case-01',payload)).status==409
  await page.get_by_label('คำอ่านหลังเห็นใบขยาย',exact=False).fill('คำตอบสมมติสำหรับทดสอบระบบบันทึก ไม่ใช่คำทำนายของแม่หมอ')
  await page.get_by_role('button',name='บันทึกและส่งทบทวน',exact=True).click()
  await page.get_by_role('heading',name='เก็บเคสนี้เรียบร้อยแล้ว',exact=True).wait_for()
  done=await get('cases/case-01');assert done['snapshot']['stage']=='review' and done['snapshot']['baseline']==frozen
  await page.reload();await page.get_by_role('heading',name='เก็บเคสนี้เรียบร้อยแล้ว',exact=True).wait_for()
  # Optimistic concurrency, idempotency, consent, origin, and immutable submitted state.
  c=await get('cases/case-02');empty=c['snapshot']['baseline'];empty['answer']='ข้อความทดสอบ API'
  payload={'requestId':str(uuid.uuid4()),'revision':0,'stage':'baseline','action':'save','answers':empty,'consent':True}
  assert (await post('cases/case-02',payload,False)).status==403
  assert (await post('cases/case-02',{**payload,'consent':False})).status==400
  good=await post('cases/case-02',payload);assert good.ok,await good.text()
  assert (await post('cases/case-02',payload)).ok
  assert (await get('cases/case-02'))['snapshot']['revision']==1
  assert (await post('cases/case-02',{**payload,'requestId':str(uuid.uuid4())})).status==409
  assert (await post('cases/case-01',{**payload,'revision':done['snapshot']['revision'],'stage':'followup'})).status==409
  races=await asyncio.gather(*(post('cases/case-02',{**payload,'requestId':str(uuid.uuid4()),'revision':1}) for _ in range(2)))
  assert sorted(r.status for r in races)==[200,409]
  assert (await get('cases/case-02'))['snapshot']['revision']==2
  # Reader cannot export or read another reader; owner can inspect without editing.
  assert (await req.get(BASE+'/api/workshop/export')).status==403
  assert (await req.get(BASE+'/api/workshop/?reader=33333333-3333-4333-8333-333333333333')).status==403
  owner=await browser.new_context(viewport={'width':1440,'height':1100})
  op=await owner.new_page();await login(op,'owner')
  await op.get_by_role('heading',name='อ่านในแบบของคุณ',exact=True).wait_for()
  await op.get_by_label('ผู้บันทึก',exact=True).select_option('22222222-2222-4222-8222-222222222222')
  await op.get_by_role('heading',name='คำอ่านที่บันทึกไว้',exact=True).wait_for()
  assert await op.get_by_role('button',name='บันทึกร่าง',exact=True).count()==0
  exported=await owner.request.get(BASE+'/api/workshop/export?table=responses&reader=22222222-2222-4222-8222-222222222222')
  assert exported.ok and len((await exported.json())['data'])==5
  stranger=await browser.new_context();sp=await stranger.new_page();await login(sp,'stranger')
  await sp.wait_for_url('**/access-denied')
  assert (await stranger.request.get(BASE+'/api/workshop/')).status==403
  # Responsive layout and typed fallback.
  await page.get_by_role('button',name='เคสถัดไป',exact=False).click()
  await page.get_by_role('heading',name='จาก 3 ใบนี้ คุณจะบอกลูกดวงว่า…',exact=True).wait_for()
  for width in [360,390,430]:
   await page.set_viewport_size({'width':width,'height':844})
   assert await page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'),width
  await page.screenshot(path=str(OUT/'mobile.png'),full_page=True)
  denied=await browser.new_context(viewport={'width':390,'height':844})
  await denied.grant_permissions([])
  dp=await denied.new_page();await login(dp)
  await dp.get_by_role('heading',name='เก็บเคสนี้เรียบร้อยแล้ว',exact=True).wait_for()
  await dp.get_by_role('button',name='เคสถัดไป',exact=False).click()
  await dp.get_by_role('heading',name='จาก 3 ใบนี้ คุณจะบอกลูกดวงว่า…',exact=True).wait_for()
  await dp.evaluate("()=>{navigator.mediaDevices.getUserMedia=async()=>{throw new DOMException('Denied','NotAllowedError')}}")
  await dp.get_by_role('button',name='เริ่มอัดเสียง',exact=True).click()
  await dp.get_by_role('alert').filter(has_text='ยังไม่ได้อนุญาตไมโครโฟน').wait_for()
  await dp.get_by_label('คำอ่านฉบับข้อความ',exact=False).fill('พิมพ์แทนเสียงได้')
  assert await dp.get_by_role('button',name='บันทึกร่าง',exact=True).is_enabled()
  assert not errors,errors
  await browser.close()
  print('PASS: Chromium loopback auth/API/real SQL-RLS, MediaRecorder audio upload/playback, immutable baseline, review, consent/CSRF, idempotency/races, owner/reader access, export, mobile widths, denied microphone')
if __name__=='__main__':asyncio.run(main())
