from pathlib import Path
import json
from playwright.sync_api import sync_playwright
P=Path('/Users/sawettachatsuthum/AIVideoLocal/maemorkratai/endcard')
with sync_playwright() as p:
    browser=p.chromium.launch()
    page=browser.new_page(viewport={'width':1080,'height':1920},device_scale_factor=1)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto((P/'index.html').as_uri())
    page.evaluate('document.fonts.ready')
    page.wait_for_timeout(300)
    for t in (0.5,1.6,2.5,4.6,6.7,8.5,9.9):
        page.evaluate('(t)=>{window.__timelines["maemorkratai-endcard"].seek(t,false);return true;}',t)
        page.screenshot(path=str(P/f'renders/frame-{t}.png'))
    metrics=page.evaluate('''()=>({duration:window.__timelines['maemorkratai-endcard'].duration(),title:document.querySelector('#wordmark').textContent,width:document.querySelector('#wordmark').getBoundingClientRect().width})''')
    print(json.dumps({'errors':errors,'metrics':metrics}))
    browser.close()
