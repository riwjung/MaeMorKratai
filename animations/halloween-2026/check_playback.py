from pathlib import Path
import json,httpx
from playwright.sync_api import sync_playwright
url='http://127.0.0.1:3004'
r=httpx.get(url+'/renders/MaeMorKratai_Halloween_2026_v3.mp4',headers={'Range':'bytes=0-99'})
assert r.status_code==206 and len(r.content)==100
errors=[]
with sync_playwright() as p:
    browser=p.chromium.launch()
    page=browser.new_page(viewport={'width':1280,'height':1000})
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(url)
    page.locator('video').evaluate('(v)=>{v.muted=true;return v.play();}')
    page.wait_for_function('document.querySelector("video").ended',timeout=20000)
    playback=page.locator('video').evaluate('(v)=>({ended:v.ended,duration:v.duration,error:v.error?.message||null,width:v.videoWidth,height:v.videoHeight,quality:v.getVideoPlaybackQuality().totalVideoFrames})')
    assert playback['duration']==12 and playback['error'] is None and playback['width']==1080
    page.get_by_role('button',name='ดูเทมเพลตแอนิเมชัน').click()
    page.locator('#time').evaluate('(el)=>{el.value=10.8;el.dispatchEvent(new Event("input"));}')
    assert page.locator('#stamp').inner_text()=='10.8s'
    page.screenshot(path='/Users/sawettachatsuthum/AIVideoLocal/maemorkratai/halloween-2026/delivery-preview.png',full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    browser.close()
assert not errors
out={'passed':True,'http_range':206,'encoded_playback':playback,'iframe_seek':10.8,'mobile_width':390,'browser_errors':errors}
Path('/Users/sawettachatsuthum/AIVideoLocal/maemorkratai/halloween-2026/playback-check.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out))
