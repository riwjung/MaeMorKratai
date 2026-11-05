"""Open Next.js and start only missing local services."""
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

root=Path(__file__).resolve().parents[1]
api_url='http://127.0.0.1:8787'
web_url='http://127.0.0.1:3000'
children=[]

def status(url):
    try:
        with urllib.request.urlopen(url+'/api/status',timeout=2) as response:
            return json.load(response)
    except Exception:
        return None

def wait_for(url,process):
    for _ in range(200):
        if process.poll() is not None:
            raise RuntimeError('เปิดบริการไม่สำเร็จ ตรวจ port 3000/8787 และคู่มือ README')
        result=status(url)
        if result:
            return result
        time.sleep(.1)
    raise RuntimeError('บริการยังไม่พร้อม กรุณาลองเปิดใหม่')

try:
    backend=status(api_url)
    if backend and backend.get('app_version')!='0.2.0':
        raise RuntimeError('มี API รุ่นเก่าเปิดอยู่ที่ 8787 กรุณาหยุดรุ่นเก่าก่อนเปิด Next.js')
    if backend is None:
        process=subprocess.Popen([sys.executable,'-m','maemorkratai.cli','serve'],cwd=root)
        children.append(process)
        wait_for(api_url,process)
    if status(web_url) is None:
        npm=shutil.which('npm') or '/usr/local/bin/npm'
        env={**os.environ,'MAEMOR_API_URL':api_url,'NEXT_TELEMETRY_DISABLED':'1',
             'PATH':'/usr/local/bin:'+os.environ.get('PATH','/usr/bin:/bin')}
        if not (root/'web/.next/BUILD_ID').exists():
            subprocess.run([npm,'run','build','--','--webpack'],cwd=root/'web',env=env,check=True)
        process=subprocess.Popen([npm,'start'],cwd=root/'web',env=env)
        children.append(process)
        wait_for(web_url,process)
    subprocess.run(['/usr/bin/open',web_url+'/#connect'],check=True)
    if children:
        print('ระบบพร้อมแล้ว ปิดหน้าต่าง Terminal นี้จะหยุดบริการที่เพิ่งเปิด')
        while all(process.poll() is None for process in children):
            time.sleep(1)
except KeyboardInterrupt:
    pass
except Exception as e:
    print(str(e))
    raise SystemExit(1)
finally:
    for process in children:
        if process.poll() is None:
            process.terminate()
