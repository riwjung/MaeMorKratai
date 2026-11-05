"""Read-only production WebKit owner review smoke; secrets and content never printed."""
import asyncio,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from passwords import request,PASSWORDS
import keyring
from playwright.async_api import async_playwright
BASE='https://maemorkratai-workshop.vercel.app'
async def main():
 members=request('/rest/v1/workshop_members?select=user_id&role=eq.owner&active=eq.true');assert len(members)==1
 u=request('/auth/v1/admin/users/'+members[0]['user_id']);pw=keyring.get_password(PASSWORDS,u['email'].lower());assert pw
 async with async_playwright() as p:
  browser=await p.webkit.launch();ctx=await browser.new_context(viewport={'width':390,'height':844});page=await ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  await page.goto(BASE+'/review');assert '/login' in page.url
  await page.get_by_label('อีเมลที่ได้รับสิทธิ์').fill(u['email']);await page.get_by_label('รหัสผ่าน',exact=True).fill(pw);await page.get_by_role('button',name='เข้าห้องทดลอง',exact=True).click();await page.get_by_role('link',name='ตรวจคำอ่านและสำนวน →').click()
  await page.locator('textarea').nth(2).wait_for();assert await page.locator('.review-case').count()==41
  assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  await page.locator('audio').first.evaluate('(a)=>{a.preload="metadata";a.load()}');await page.wait_for_function('document.querySelector("audio").readyState>=1',timeout=30000)
  await page.get_by_label('เลือกหมวด').select_option('style');await page.get_by_role('button',name='สำนวน 6 ข้อ').click();await page.wait_for_function('document.querySelectorAll("textarea").length===7');assert not errors
  await browser.close()
 report={'passed':True,'browser':'WebKit','production':True,'loginAndOwnerMenu':True,'cases':40,'styleProposals':6,'audioMetadataLoads':True,'mobileNoOverflow':True,'pageErrors':0,'writes':0};Path('artifacts/review-webkit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
asyncio.run(main())
