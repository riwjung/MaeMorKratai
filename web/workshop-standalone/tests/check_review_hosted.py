"""Hosted review checks; writes only isolated synthetic accounts; credentials stay in memory."""
import asyncio,json,os,secrets,sys,uuid,hashlib
from pathlib import Path
from urllib.request import Request,urlopen
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from passwords import request,CONFIG,PASSWORDS
import keyring
from playwright.async_api import async_playwright
BASE=os.environ.get('WORKSHOP_TEST_URL','http://127.0.0.1:3012')
assert BASE in ['http://127.0.0.1:3012','https://maemorkratai-workshop.vercel.app']
OUT=Path('artifacts');OUT.mkdir(exist_ok=True)
JOURNAL=OUT/'review-cleanup.json'

def storage(path,body):return request('/storage/v1/object/workshop-review/'+path,'POST',body)
def source_doc(payload):return {**payload,'sourceHash':hashlib.sha256(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()}
async def login(browser,user):
 ctx=await browser.new_context(viewport={'width':390,'height':844});page=await ctx.new_page();await page.goto(BASE+'/login');await page.get_by_label('อีเมลที่ได้รับสิทธิ์',exact=True).fill(user['email']);await page.get_by_label('รหัสผ่าน',exact=True).fill(user['password']);await page.get_by_role('button',name='เข้าห้องทดลอง',exact=True).click();await page.get_by_role('heading',name='อ่านในแบบของคุณ',exact=True).wait_for();return ctx,page
async def main():
 assert not JOURNAL.exists(),'Previous synthetic cleanup pending'
 users=[];objects=[];report={'passed':False,'application':BASE}
 try:
  for role in ['owner','reader']:
   email='workshop-smoke-review-'+uuid.uuid4().hex+'@example.com';pw=secrets.token_urlsafe(24);u=request('/auth/v1/admin/users','POST',{'email':email,'password':pw,'email_confirm':True});users.append({'id':u['id'],'email':email,'password':pw});JOURNAL.write_text(json.dumps({'users':[{k:u[k] for k in ['id','email']} for u in users],'objects':objects}));request('/rest/v1/workshop_members','POST',{'user_id':u['id'],'role':role,'display_name':'ทดสอบหน้าตรวจ','active':True})
  who=users[0]['id'];case=json.loads(Path('lib/cases.json').read_text())[3];assert case['split']=='development'
  answer={'answer':'คำอ่านสมมติ','evidence':'','uncertainty':'','question':'','phrases':'','changes':'','unchanged':'','audioId':None}
  request('/rest/v1/workshop_readings','POST',{'reader_id':who,'case_id':case['id'],'revision':1,'stage':'review','baseline':answer,'followup':answer})
  stage={'originalText':'คำอ่านสมมติ','machineTranscript':'','reviewText':'คำอ่านสมมติ','sourceType':'typed','notes':{},'audioId':None}
  src=source_doc({'id':case['id'],'sourceRevision':1,'caseVersion':case['version'],'baseline':stage,'followup':stage});style=source_doc({'id':'style','observations':[{'id':'style-01','observation':'สำนวนสมมติ','question':'ต้องการอย่างไร','sources':[case['id']]}]})
  for id,body in [(case['id']+'/source.json',src),('style/source.json',style),('manifest.json',{'items':[{'id':case['id'],'title':'เคสทดสอบ','category':'love','sourceHash':src['sourceHash']},{'id':'style','title':'สำนวนทดสอบ','category':'style','sourceHash':style['sourceHash']}]})]:
   path=who+'/'+id;objects.append(path);JOURNAL.write_text(json.dumps({'users':[{k:u[k] for k in ['id','email']} for u in users],'objects':objects}));storage(path,body)
  async with async_playwright() as p:
   browser=await p.chromium.launch();anon=await browser.new_context();assert (await anon.request.get(BASE+'/api/review')).status==401
   ctx,page=await login(browser,users[0]);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   await page.get_by_role('link',name='ตรวจคำอ่านและสำนวน →').click();await page.get_by_role('heading',name='เคสทดสอบ',exact=True).wait_for();assert await page.locator('textarea').count()==3
   await page.locator('textarea').nth(0).fill('ฉบับแก้สมมติ');await page.get_by_role('button',name='บันทึกร่าง',exact=True).click();await page.get_by_text('บันทึกผลตรวจแล้ว เปิดกลับมาตรวจต่อได้',exact=True).wait_for();await page.reload();await page.get_by_role('heading',name='เคสทดสอบ',exact=True).wait_for();assert await page.locator('textarea').nth(0).input_value()=='ฉบับแก้สมมติ'
   d=await (await ctx.request.get(BASE+'/api/review?id='+case['id'])).json();state=d['state'];payload={'id':case['id'],'sourceHash':src['sourceHash'],'revision':state['revision'],'content':state['content'],'status':'approved','requestId':str(uuid.uuid4())}
   assert (await ctx.request.post(BASE+'/api/review',data=payload,headers={'Origin':BASE})).status==400
   assert (await ctx.request.post(BASE+'/api/review',data={**payload,'confirm':True},headers={'Origin':'https://bad.example'})).status==403
   req={**payload,'confirm':True};r=await ctx.request.post(BASE+'/api/review',data=req,headers={'Origin':BASE});assert r.status==200;approved=(await r.json())['state'];assert approved['status']=='approved' and approved['reviewedBy']==who
   assert (await ctx.request.post(BASE+'/api/review',data=req,headers={'Origin':BASE})).status==200
   assert (await ctx.request.post(BASE+'/api/review',data={**req,'requestId':str(uuid.uuid4())},headers={'Origin':BASE})).status==409
   concurrent={**req,'status':'draft','revision':approved['revision']};rs=await asyncio.gather(*[ctx.request.post(BASE+'/api/review',data={**concurrent,'requestId':str(uuid.uuid4())},headers={'Origin':BASE}) for _ in range(2)]);assert sorted(r.status for r in rs)==[200,409]
   d=await (await ctx.request.get(BASE+'/api/review?id='+case['id'])).json();assert d['state']['status']=='draft' and len(d['history'])==3
   old=await (await ctx.request.get(BASE+'/api/review?id='+case['id']+'&revision=2')).json();assert old['state']['status']=='approved'
   holdout=next(c['id'] for c in json.loads(Path('lib/cases.json').read_text()) if c['split']=='holdout');assert (await ctx.request.get(BASE+'/api/review?id='+holdout)).status==404
   assert (await ctx.request.get(BASE+'/api/review?id=../../manifest')).status==404
   reader,rpage=await login(browser,users[1]);assert (await reader.request.get(BASE+'/api/review')).status==403;assert (await reader.request.post(BASE+'/api/review',data=req,headers={'Origin':BASE})).status==403
   await rpage.goto(BASE+'/review');assert '/access-denied' in rpage.url
   await page.reload();await page.get_by_role('heading',name='เคสทดสอบ',exact=True).wait_for();assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   await page.locator('textarea').nth(0).fill('ร่างยังไม่บันทึก');page.once('dialog',lambda dialog:dialog.dismiss());await page.get_by_role('button',name='สำนวนทดสอบ').click();assert await page.locator('textarea').nth(0).input_value()=='ร่างยังไม่บันทึก'
   page.once('dialog',lambda dialog:dialog.accept());await page.get_by_role('button',name='สำนวนทดสอบ').click();await page.get_by_role('heading',name='สำนวนสมมติ',exact=True).wait_for();await page.locator('textarea').nth(0).fill('ใช้สำนวนสมมติที่ตรวจแล้ว');await page.get_by_role('checkbox').check();await page.get_by_role('button',name='รับรองฉบับนี้',exact=True).click();await page.get_by_text('รับรองฉบับนี้แล้ว ยังไม่เปิดให้ AI ตอบลูกค้าอัตโนมัติ',exact=True).wait_for()
   await page.screenshot(path=str(OUT/'review-synthetic-mobile.png'),full_page=True);assert not errors
   # Read-only check of real owner packet; no real approvals or drafts written.
   members=request('/rest/v1/workshop_members?select=user_id&role=eq.owner&active=eq.true');real=next(x['user_id'] for x in members if x['user_id']!=who);u=request('/auth/v1/admin/users/'+real);pw=keyring.get_password(PASSWORDS,u['email'].lower());assert pw
   rc,rp=await login(browser,{'email':u['email'],'password':pw});await rp.goto(BASE+'/review');await rp.locator('.review-case').first.wait_for();listing=await (await rc.request.get(BASE+'/api/review')).json();assert len(listing['items'])==41 and sum(x['category']!='style' for x in listing['items'])==40
   detail=await (await rc.request.get(BASE+'/api/review?id=case-01')).json();audio=detail['source']['baseline']['audioId'];assert audio
   audio_result=await rc.request.get(BASE+'/api/workshop/audio/'+audio,max_redirects=0);assert audio_result.status==302
   assert (await rc.request.get(BASE+'/api/review?id='+holdout)).status==404
   # Storage endpoint cannot expose review objects through authenticated public client.
   token=request('/auth/v1/token?grant_type=password','POST',{'email':users[1]['email'],'password':users[1]['password']},public=True)['access_token']
   url=keyring.get_password(CONFIG,'NEXT_PUBLIC_SUPABASE_URL');key=keyring.get_password(CONFIG,'NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY')
   direct=await anon.request.get(url+'/storage/v1/object/authenticated/workshop-review/'+real+'/manifest.json',headers={'apikey':key,'Authorization':'Bearer '+token});assert direct.status in [400,403,404]
   original=request('/rest/v1/workshop_readings?reader_id=eq.'+who)[0];assert original['baseline']==answer and original['revision']==1
   report.update(passed=True,anonymousDenied=True,readerDenied=True,directStorageDenied=True,holdoutExcluded=True,draftReload=True,approvalAndHistory=True,idempotentRetry=True,concurrentConflict=True,csrfRejected=True,unsavedGuard=True,mobileNoOverflow=True,realDevelopmentCases=40,realAudioAccessible=True,realReviewsWritten=0,pageErrors=len(errors))
   await browser.close()
 finally:
  for u in users:
   if u==users[0]:
    for id in [case['id'],'style'] if 'case' in locals() else []:
     rows=request('/storage/v1/object/list/workshop-review','POST',{'prefix':u['id']+'/'+id+'/revisions','limit':100});objects.extend(u['id']+'/'+id+'/revisions/'+r['name'] for r in rows)
    if objects:request('/storage/v1/object/workshop-review','DELETE',{'prefixes':objects})
   actual=request('/auth/v1/admin/users/'+u['id']);assert actual['email']==u['email'] and u['email'].startswith('workshop-smoke-review-')
   request('/rest/v1/workshop_readings?reader_id=eq.'+u['id'],'DELETE');request('/rest/v1/workshop_members?user_id=eq.'+u['id'],'DELETE');request('/auth/v1/admin/users/'+u['id'],'DELETE')
  JOURNAL.unlink(missing_ok=True)
  (OUT/('review-production.json' if 'vercel' in BASE else 'review-hosted.json')).write_text(json.dumps(report,indent=2))
 print(json.dumps(report))
asyncio.run(main())
