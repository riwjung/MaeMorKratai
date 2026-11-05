import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlsplit
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from plotly.offline import get_plotlyjs
from . import store, analysis, importer
from .config import ROOT, VAULT, Secrets, settings, save_settings, now, TZ
from .meta import Graph, discovery, MetaError
from .sync import run_sync, is_running
from .report import write_report

STATIC = Path(__file__).parent / 'static'
secrets = Secrets()

@asynccontextmanager
async def lifespan(app):
    store.init()
    yield

app = FastAPI(title='แม่หมอกระต่าย', docs_url=None, redoc_url=None, lifespan=lifespan)

@app.middleware('http')
async def local_only(request: Request, call_next):
    host = request.url.hostname
    if host not in ('127.0.0.1', 'localhost', '::1') or request.client.host not in ('127.0.0.1', '::1'):
        return JSONResponse({'detail':'เปิดระบบนี้จากเครื่อง Mac เท่านั้น'}, status_code=403)
    if request.method not in ('GET', 'HEAD'):
        origin = request.headers.get('origin')
        if request.headers.get('x-maemor-local') != '1' or (origin and origin != f'{request.url.scheme}://{request.headers.get("host")}'):
            return JSONResponse({'detail':'คำขอนี้ไม่ได้มาจากหน้าระบบบนเครื่อง'}, status_code=403)
    try:
        response = await call_next(request)
    except Exception:
        # Catch outside Starlette's server-error logger so a traceback cannot echo a secret.
        response = JSONResponse({'detail':'ทำรายการไม่สำเร็จ ตรวจ Keychain และลองใหม่'}, status_code=500)
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['X-Frame-Options'] = 'DENY'
    return response

@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    # FastAPI defaults echo invalid inputs, which can include a token.
    return JSONResponse({'detail':'ข้อมูลที่กรอกไม่ครบหรือรูปแบบไม่ถูกต้อง'}, status_code=422)

@app.exception_handler(MetaError)
async def meta_error(request, exc):
    return JSONResponse({'detail':str(exc), 'category':exc.category}, status_code=400)

@app.exception_handler(ValueError)
async def value_error(request, exc):
    return JSONResponse({'detail':str(exc)}, status_code=400)

@app.exception_handler(Exception)
async def hidden_error(request, exc):
    return JSONResponse({'detail':'ระบบทำรายการไม่สำเร็จ กรุณาตรวจ Keychain/ไฟล์ตั้งค่าแล้วลองใหม่'}, status_code=500)

app.mount('/static', StaticFiles(directory=STATIC), name='static')

@app.get('/')
def index():
    return FileResponse(STATIC / 'index.html')

@app.get('/static-plotly.js')
def plotly_js():
    return Response(get_plotlyjs(), media_type='application/javascript')

@app.get('/api/status')
def status():
    cfg = settings()
    jobs = store.rows('SELECT * FROM jobs ORDER BY started_at DESC LIMIT 5')
    running = is_running()
    if jobs and jobs[0]['status']=='running' and not running:
        jobs[0].update(status='partial', message='งานก่อนหน้าหยุด กดซิงก์เพื่อเก็บต่อ')
    latest = ROOT/'data/latest-report.json'
    scheduler = ROOT/'data/scheduler.json'
    connection = cfg.get('connection', {'status':'not_configured','verified_at':None,
                                        'message':'ยังไม่เชื่อม Meta กรุณาสร้าง App และกรอก User token'})
    if cfg['page_id'] and connection['status']=='not_configured':
        connection = {'status':'selected','verified_at':None,'message':'เลือกเพจแล้ว กรุณาตรวจบัญชีกับ Meta'}
    if jobs and jobs[0]['status']=='reconnect' and (jobs[0].get('ended_at') or '') > connection.get('checked_at',''):
        connection = {**connection,'status':'reconnect','message':jobs[0]['message']}
    return {'app_version':'0.2.0','configured':bool(cfg['page_id']),
            'connected': connection['status'] in ('verified','verified_with_limits'),
            'connection':connection, 'settings': cfg, 'accounts': analysis.current_accounts(),
            'jobs':jobs, 'sync_running':running, 'latest_report':json.loads(latest.read_text()) if latest.exists() else None,
            'data_dir':str(ROOT), 'daily_sync':'08:00 Asia/Bangkok เมื่อ Mac พร้อมทำงาน',
            'scheduler':json.loads(scheduler.read_text()) if scheduler.exists() else {'installed':False}}

@app.get('/api/overview')
def overview(platform: str='instagram'):
    if platform not in ('facebook','instagram'):
        raise ValueError('แพลตฟอร์มไม่ถูกต้อง')
    return analysis.overview(platform)

@app.get('/api/content')
def content(platform: str='instagram', metric: str='views', age: int=0, kind: str='all'):
    if platform not in ('facebook','instagram') or age not in (0,7,30,90):
        raise ValueError('ตัวกรองไม่ถูกต้อง')
    return {'rows':analysis.content(platform,metric,age,kind), 'ranking_metric':metric, 'basis':'lifetime'}

@app.get('/api/findings')
def findings(platform: str='instagram'):
    if platform not in ('facebook','instagram'):
        raise ValueError('แพลตฟอร์มไม่ถูกต้อง')
    return analysis.findings(platform)

@app.get('/api/source/{source_id}')
def source(source_id: str):
    found = store.rows('SELECT * FROM sources WHERE id=?', (source_id,))
    if not found:
        raise HTTPException(404, 'ไม่พบ snapshot')
    p = Path(found[0]['path']).resolve()
    if not p.is_relative_to((ROOT/'data/snapshots').resolve()):
        raise HTTPException(403)
    return {'metadata':found[0], 'snapshot':json.loads(p.read_text())}

class Connect(BaseModel):
    token: str = Field(min_length=10, max_length=8192)
    api_version: str = Field(pattern=r'^v\d{2}\.\d+$')

@app.post('/api/connect/discover')
def connect(body: Connect):
    if is_running():
        raise ValueError('รอซิงก์เสร็จก่อนเชื่อม token ใหม่')
    graph = Graph(body.api_version, body.token, budget=100)
    try:
        result = discovery(graph)
    finally:
        graph.close()
    # Only store a token after Meta actually accepts it.
    secrets.set('user', body.token)
    cfg = settings()
    cfg.update(api_version=body.api_version, permissions=result['permissions'],
               connection={'status':'token_verified','verified_at':None,'checked_at':now(),
                           'message':'Meta รับ User token แล้ว เลือกเพจและตรวจบัญชีต่อ'})
    save_settings(cfg)
    return result

class Selection(BaseModel):
    page_id: str = Field(pattern=r'^\d+$')
    allow_facebook_only: bool=False

@app.get('/api/connect/pages')
def connected_pages():
    cfg, token = settings(), secrets.get('user')
    if not token or not cfg['api_version']:
        raise ValueError('เชื่อม User token ก่อน')
    graph = Graph(cfg['api_version'], token, budget=100)
    try:
        return discovery(graph)
    finally:
        graph.close()

@app.post('/api/connect/select')
def select_page(body: Selection):
    if is_running():
        raise ValueError('รอซิงก์เสร็จก่อนเปลี่ยนเพจ')
    cfg, token = settings(), secrets.get('user')
    if not token:
        raise ValueError('เชื่อม User token ก่อน')
    graph = Graph(cfg['api_version'], token, budget=100)
    try:
        result = discovery(graph)
        chosen = next((p for p in result['pages'] if p['id']==body.page_id), None)
        if not chosen:
            raise ValueError('เพจนี้ไม่อยู่ในบัญชีที่ Meta อนุญาต')
        if not {'ANALYZE','MANAGE','PROFILE_PLUS_ANALYZE','PROFILE_PLUS_MANAGE',
                'PROFILE_PLUS_FULL_CONTROL'} & set(chosen.get('tasks',[])):
            raise ValueError('ยังไม่พบสิทธิ์ ANALYZE/MANAGE ของเพจนี้ ตรวจสิทธิ์กับเจ้าของ')
        ig = chosen.get('instagram_business_account', {})
        if not ig and not body.allow_facebook_only:
            raise ValueError('เพจยังไม่เชื่อม IG professional กรุณาเชื่อม @maemorkratai ใน Meta ก่อน')
        if ig and chosen['ig_username'].lower() != cfg['expected_ig']:
            raise ValueError('IG ที่เชื่อมกับเพจนี้ไม่ตรงกับ @maemorkratai หรือยังอ่านชื่อไม่ได้')
        record, _ = graph.get(body.page_id, {'fields':'id,access_token'})
        page_token = record.get('access_token')
        if not page_token:
            raise ValueError('Meta ยังไม่ให้ Page token ตรวจสิทธิ์และ App roles')
        secrets.set('page', page_token)
        cfg.update(page_id=body.page_id, page_name=chosen.get('name',''),
                   ig_id=str(ig.get('id','')), ig_username=chosen.get('ig_username',''),
                   permissions=result['permissions'], connection={'status':'selected','verified_at':None,'checked_at':now(),
                       'message':'เลือกเพจและตรวจ IG ที่เชื่อมแล้ว กดตรวจบัญชีเพื่อทดสอบ Page token และข้อมูลจริง'})
        save_settings(cfg)
        store.coverage('facebook',body.page_id,'connection','available','พบเพจและ Page tasks; Insights ต้องทดสอบด้วยการซิงก์')
        if ig:
            store.coverage('instagram',str(ig['id']),'connection','available','พบ professional IG ที่เชื่อมและชื่อบัญชีตรงกัน')
        return {'selected':chosen['name'], 'instagram':cfg['ig_username']}
    finally:
        graph.close()

@app.post('/api/disconnect')
def disconnect():
    if is_running():
        raise ValueError('รอซิงก์เสร็จก่อนยกเลิกการเชื่อม')
    for name in ('user','page'):
        secrets.delete(name)
    cfg = settings()
    cfg.update(page_id='',ig_id='',page_name='',permissions=[],ig_username='',
               connection={'status':'not_configured','verified_at':None,'message':'ยังไม่เชื่อม Meta'})
    save_settings(cfg)
    return {'status':'disconnected','message':'ลบ token ใน Keychain แล้ว ข้อมูลที่เก็บไว้ยังอยู่'}

@app.post('/api/connect/verify')
def verify_connection():
    from datetime import datetime, timedelta
    if is_running():
        raise ValueError('รอซิงก์เสร็จก่อนตรวจบัญชี')
    cfg = settings()
    if not cfg['page_id'] or not cfg['api_version']:
        raise ValueError('เลือกเพจในขั้นตอนเชื่อมบัญชีก่อน')
    token = secrets.get('page')
    if not token:
        raise ValueError('ยังไม่มี Page token ใน Keychain กรุณาเชื่อมใหม่')
    checks = []
    identity_passed = True
    today = datetime.now(TZ).replace(hour=0,minute=0,second=0,microsecond=0)
    for platform, aid in (('facebook',cfg['page_id']),('instagram',cfg['ig_id'])):
        if not aid:
            continue
        graph = Graph(cfg['api_version'],token,platform,budget=15)
        first_media = None
        def check(capability, endpoint, params):
            try:
                value,sid = graph.get(endpoint,params)
                result = {'platform':platform,'capability':capability,'status':'available',
                          'detail':'อ่านจาก Meta สำเร็จ','source_id':sid}
                if 'data' in value and not value['data']:
                    result.update(status='empty',detail='Meta ให้ผลว่าง ยังไม่มีข้อมูลในขอบเขตนี้')
                checks.append(result)
                store.coverage(platform,aid,endpoint,result['status'],result['detail'],capability)
                return value
            except MetaError as e:
                checks.append({'platform':platform,'capability':capability,'status':e.category,'detail':str(e)})
                store.coverage(platform,aid,endpoint,e.category,str(e),capability)
                if e.category=='expired':
                    raise
                return None
        try:
            profile = check('identity',aid,{'fields':'id,name' if platform=='facebook' else 'id,username'})
            if not profile or str(profile.get('id',''))!=aid or (platform=='instagram' and profile.get('username','').lower()!=cfg['expected_ig']):
                identity_passed = False
                if profile:
                    checks[-1].update(status='mismatch',detail='ตัวตนบัญชีไม่ตรงกับ Page ID / IG @maemorkratai ที่เลือก')
            edge = 'published_posts' if platform=='facebook' else 'media'
            media = check('content',f'{aid}/{edge}',{'fields':'id','limit':1})
            if media is None:
                identity_passed = False
            if media and media.get('data'):
                first_media = str(media['data'][0]['id'])
            if first_media:
                check('comments',f'{first_media}/comments',{'fields':'id','limit':1})
            else:
                checks.append({'platform':platform,'capability':'comments','status':'not_tested',
                               'detail':'ยังไม่มีคลิปตัวอย่างให้ตรวจคอมเมนต์'})
            names = cfg[f'{platform}_account_metrics']
            if names:
                params = {'metric':names[0],'period':'day','since':(today-timedelta(days=1)).isoformat(),
                          'until':today.isoformat()}
                if platform=='instagram':
                    params['metric_type']='total_value'
                check('insights',f'{aid}/insights',params)
        except MetaError as e:
            identity_passed = False
            cfg['connection'] = {'status':'reconnect' if e.category=='expired' else 'failed',
                                 'verified_at':None,'checked_at':now(),'message':str(e),'checks':checks}
            save_settings(cfg)
            return cfg['connection']
        finally:
            graph.close()
    limited = any(c['status'] not in ('available','empty') for c in checks)
    cfg['connection'] = {'status':('verified_with_limits' if limited else 'verified') if identity_passed else 'failed',
                         'verified_at':now() if identity_passed else None,'checked_at':now(),
                         'message':'ตรวจตัวตนและสิทธิ์อ่านคอนเทนต์ผ่าน ดูข้อจำกัดแต่ละกลุ่มก่อนซิงก์' if identity_passed
                                   else 'ยังอ่านบัญชี/คอนเทนต์ไม่ครบ ตรวจสิทธิ์ App และเลือกบัญชีใหม่',
                         'checks':checks}
    save_settings(cfg)
    return cfg['connection']

@app.get('/api/brand')
def brand():
    p = ROOT/'data/brand-analysis.json'
    if not p.exists():
        raise HTTPException(404,'ยังไม่ได้เตรียมการวิเคราะห์ภาพและคลิปอ้างอิง')
    payload = json.loads(p.read_text())
    cfg = settings()
    verified = status()['connected']
    items = store.rows('''SELECT p.* FROM posts p JOIN sources s ON s.id=p.source_id
                         WHERE s.kind='meta' AND ((p.platform='facebook' AND p.account_id=?)
                         OR (p.platform='instagram' AND p.account_id=?))
                         ORDER BY p.published_at DESC''', (cfg['page_id'], cfg['ig_id']))
    samples = items[:20] if verified else []
    captions = [p['text'] for p in samples if p.get('text')]
    topics = {name: sum(any(word in text.lower() for word in words) for text in captions)
              for name, words in analysis.TOPICS.items()}
    observations = [f'ตัวอย่างล่าสุด {len(samples)} โพสต์ มีคำบรรยาย {len(captions)} โพสต์'] if samples else []
    observations.extend(f'พบคำเกี่ยวกับ{topic}ในคำบรรยาย {count} โพสต์' for topic, count in topics.items() if count)
    payload['channel_audit'] = {
        'status': 'awaiting_connection' if not verified else ('review_ready' if samples else 'awaiting_content'),
        'post_count':len(items),
        'method':'ตัวอย่างล่าสุดไม่เกิน 20 โพสต์จาก Meta API ของบัญชีที่เลือก; จัดหมวดคำบรรยายด้วยคำสำคัญ ไม่ใช่การวิเคราะห์ภาพหรือเสียงอัตโนมัติ',
        'samples':[{'platform':p['platform'],'post_id':p['post_id'],'caption':p['text'],
                    'permalink':p['permalink'],'media_type':p['media_type'],
                    'thumbnail_url':p['thumbnail_url'],'media_url':p['media_url'],'source_id':p['source_id']} for p in samples],
        'caption_observations':observations,
        'limitations':['ยังต้องเปิดดูภาพและคลิปต้นทางก่อนสรุป mood/tone ของทั้งช่อง',
                       'URL สื่อจาก Meta อาจหมดอายุหรือ API ไม่ให้ภาพตัวอย่าง ใช้ลิงก์โพสต์ต้นทางแทน',
                       'ภาพโปรไฟล์และคลิปที่เจ้าของให้เป็นแหล่งอ้างอิงแยกจากโพสต์จริง; ไม่นับข้อมูล CSV เป็นข้อมูลจาก API']}
    return payload

@app.get('/api/brand/media/{name}')
def brand_media(name: str):
    paths = {'profile-sparkles':VAULT/'wiki/Images/IMG_5391.JPG',
             'profile-clean':VAULT/'wiki/Images/IMG_5392.JPG',
             'profile-pride':VAULT/'wiki/Images/IMG_5393.JPG',
             'reference-video':ROOT/'brand-assets/reference-preview.mp4',
             'contact-sheet':ROOT/'brand-assets/contact-sheet.jpg'}
    path = paths.get(name)
    if path is None or not path.exists():
        raise HTTPException(404,'ไม่พบภาพหรือคลิปอ้างอิง')
    return FileResponse(path, media_type='video/mp4' if name=='reference-video' else 'image/jpeg')

def sync_and_report():
    run_sync()
    write_report()

@app.post('/api/sync')
def sync(background: BackgroundTasks):
    cfg = settings()
    if not cfg['page_id']:
        raise ValueError('เชื่อมและเลือกเพจก่อน หรือใช้ CSV เพื่อเริ่มวิเคราะห์')
    if is_running():
        raise ValueError('มีงานซิงก์กำลังทำอยู่')
    background.add_task(sync_and_report)
    return {'status':'queued'}

@app.post('/api/import/preview')
async def import_preview(file: UploadFile=File(...)):
    return importer.preview(await file.read(20*1024*1024+1))

@app.post('/api/import')
async def import_data(file: UploadFile=File(...), platform: str=Form(...), account_id: str=Form(...),
                      kind: str=Form('content'), mapping: str=Form('{}'), timezone: str=Form('Asia/Bangkok'),
                      period: str=Form('lifetime'), start: str=Form(''), end: str=Form('')):
    if is_running():
        raise ValueError('รอซิงก์เสร็จก่อนนำเข้า CSV')
    try:
        fields = json.loads(mapping)
    except json.JSONDecodeError:
        raise ValueError('การจับคู่คอลัมน์ไม่ถูกต้อง') from None
    if not isinstance(fields, dict):
        raise ValueError('การจับคู่คอลัมน์ไม่ถูกต้อง')
    result = importer.import_csv(await file.read(20*1024*1024+1),platform,account_id,kind,
                                 fields,timezone,period,start,end,Path(file.filename or 'export.csv').name)
    if result['status']=='imported':
        result['report'] = write_report()
    return result

@app.post('/api/report')
def report():
    if is_running():
        raise ValueError('รอซิงก์เสร็จก่อนสร้างรายงาน')
    return write_report()

@app.get('/api/report/latest')
def latest_report():
    p = ROOT/'data/latest-report.json'
    if not p.exists():
        raise HTTPException(404,'ยังไม่มีรายงาน')
    entry = json.loads(p.read_text())
    return {**entry,'content':Path(entry['path']).read_text()}

class MetricSettings(BaseModel):
    facebook_account_metrics: list[str]
    facebook_post_metrics: list[str]
    instagram_account_metrics: list[str]
    instagram_post_metrics: list[str]

@app.post('/api/settings/metrics')
def metric_settings(body: MetricSettings):
    if is_running():
        raise ValueError('รอซิงก์เสร็จก่อนเปลี่ยนรายการ metric')
    import re
    values = body.model_dump()
    if any(not re.fullmatch(r'[a-z][a-z0-9_]{0,100}',n) for names in values.values() for n in names):
        raise ValueError('ชื่อ metric ใช้ตัวอักษรอังกฤษ ตัวเลข และ underscore เท่านั้น')
    if any(len(names)>20 for names in values.values()):
        raise ValueError('ตั้ง metric ได้ไม่เกิน 20 รายการต่อกลุ่ม')
    cfg = settings()
    cfg.update(values)
    save_settings(cfg)
    # New capability choices should re-probe historical media too.
    with store.db() as c:
        c.execute("DELETE FROM checkpoints WHERE key LIKE '%:insights:%'")
    return {'status':'saved'}
