"""Render the real empty app, then verify an isolated CSV workflow; never seed real data."""
import csv
import io
import json
import os
import subprocess
import tempfile
import time
from datetime import datetime,timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import httpx
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
artifacts=ROOT/'artifacts'
artifacts.mkdir(exist_ok=True)
checks=[]
with sync_playwright() as p:
    candidates=list((Path.home()/'Library/Caches/ms-playwright').glob('chromium_headless_shell-*/chrome-mac/headless_shell'))
    try:
        browser=p.chromium.launch()
    except Exception:
        if not candidates:raise
        browser=p.chromium.launch(executable_path=str(candidates[-1]))
    page=browser.new_page(viewport={'width':1440,'height':1100})
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto('http://127.0.0.1:8787')
    page.wait_for_function("document.querySelector('#cards').children.length===4")
    assert page.locator('#empty-banner').is_visible()
    assert page.locator('#connection').inner_text()=='ยังไม่เชื่อมบัญชี'
    assert page.locator('#trend-empty').is_visible()
    assert page.locator('.card-value').nth(0).inner_text()=='—'
    page.screenshot(path=str(artifacts/'dashboard-empty-desktop.png'),full_page=True)
    for name in ('connect','import','reports'):
        page.locator(f'.nav[data-view="{name}"]').click()
        assert page.locator('#'+name).is_visible()
    page.locator('.nav[data-view="dashboard"]').click()
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
    page.screenshot(path=str(artifacts/'dashboard-empty-mobile.png'),full_page=True)
    checks.append('Real app: empty-state truthfulness; four views; 1440px / 390px layouts')
    assert not errors,errors
    with tempfile.TemporaryDirectory(prefix='maemor-browser-test-') as temporary:
        temp=Path(temporary)
        env={**os.environ,'MAEMOR_DATA_DIR':str(temp/'runtime'),'MAEMOR_VAULT_DIR':str(temp/'vault')}
        subprocess.run([str(ROOT/'.venv/bin/python'),'-m','maemorkratai.cli','init'],cwd=ROOT,env=env,check=True,stdout=subprocess.DEVNULL)
        server=subprocess.Popen([str(ROOT/'.venv/bin/python'),'-m','maemorkratai.cli','serve','--port','8789'],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try:
            for _ in range(100):
                try:
                    if httpx.get('http://127.0.0.1:8789/api/status',timeout=.5).status_code==200:break
                except httpx.HTTPError:pass
                time.sleep(.1)
            else:raise AssertionError('test server not ready')
            page.set_viewport_size({'width':1440,'height':1100})
            page.goto('http://127.0.0.1:8789')
            page.wait_for_function("document.querySelector('#cards').children.length===4")
            page.locator('.nav[data-view="import"]').click()
            out=io.StringIO();writer=csv.writer(out)
            writer.writerow(['Post ID','Views','Shares','Publish time','Description','Post link'])
            for i in range(1,11):
                writer.writerow([f'p-{i}',i*13,i,'2026-10-01',f'ไพ่ความรัก {i}',f'https://www.instagram.com/p/test{i}/'])
            page.locator('#csv-file').set_input_files({'name':'synthetic-test-content.csv','mimeType':'text/csv','buffer':out.getvalue().encode()})
            page.wait_for_function("!document.querySelector('#import-submit').disabled")
            page.locator('#import-form [name="account_id"]').fill('synthetic-account')
            page.locator('#import-submit').click()
            page.wait_for_function("document.querySelector('#notice').textContent.includes('นำเข้า 10 แถว')")
            page.locator('.nav[data-view="dashboard"]').click()
            page.wait_for_function("document.querySelector('#content-rows').children.length===10")
            assert '130' in page.locator('#content-rows tr').first.inner_text()
            page.locator('#content-rows .source-button').first.click()
            assert page.locator('#detail').is_visible()
            page.locator('#detail .source-button').first.click()
            page.wait_for_function("document.querySelector('#detail-body').textContent.includes('csv-import')")
            assert 'csv-import' in page.locator('#detail-body').inner_text()
            page.locator('#close-detail').click()
            page.locator('#age-filter').select_option('7')
            page.wait_for_function("document.querySelector('#content-summary').textContent.includes('จาก 0 รายการ')")
            page.locator('#age-filter').select_option('0')
            page.wait_for_function("document.querySelector('#content-rows').children.length===10")
            # Add 60 days of account data via the same CSV UI.
            page.locator('.nav[data-view="import"]').click()
            out=io.StringIO();writer=csv.writer(out);writer.writerow(['Date','Views','Total interactions','Followers'])
            today=datetime.now(ZoneInfo('Asia/Bangkok')).replace(hour=0,minute=0,second=0,microsecond=0)
            for i in range(1,61):writer.writerow([(today-timedelta(days=i)).date(),10 if i<=30 else 5,2,100+61-i])
            page.locator('#csv-file').set_input_files({'name':'synthetic-test-daily.csv','mimeType':'text/csv','buffer':out.getvalue().encode()})
            page.wait_for_function("!document.querySelector('#import-submit').disabled")
            page.locator('#import-form [name="kind"]').select_option('daily')
            page.locator('#import-submit').click()
            page.wait_for_function("document.querySelector('#notice').textContent.includes('นำเข้า 60 แถว')")
            page.locator('.nav[data-view="dashboard"]').click()
            page.wait_for_function("document.querySelectorAll('.card-value')[1].textContent==='300'")
            assert '+100.0%' in page.locator('.card').nth(1).inner_text()
            assert page.locator('#trend').is_visible()
            page.evaluate('window.scrollTo(0,0)')
            page.screenshot(path=str(artifacts/'dashboard-test-data-desktop.png'),full_page=True)
            page.locator('.nav[data-view="reports"]').click()
            page.wait_for_function("document.querySelector('#report-content').textContent.includes('แผนทดลอง 30 วัน')")
            assert not errors,errors
            checks.append('Isolated synthetic data: CSV column mapping; ten posts; filters; source inspection; 60 daily rows; 300 vs 150 (+100%); chart; sourced report')
        finally:
            server.terminate();server.wait(timeout=10)
    browser.close()
result={'status':'passed','checks':checks,'errors':errors,'fixtures_in_real_database':False}
(artifacts/'browser-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False))
