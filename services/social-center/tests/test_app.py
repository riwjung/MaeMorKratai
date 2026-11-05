import httpx
import pytest
from fastapi.testclient import TestClient
from maemorkratai import app as appmodule, config, store
from maemorkratai.meta import Graph

@pytest.fixture
def client(isolated,monkeypatch,memory_secrets):
    monkeypatch.setattr(appmodule,'ROOT',isolated[0])
    monkeypatch.setattr(appmodule,'VAULT',isolated[1])
    monkeypatch.setattr(appmodule,'secrets',memory_secrets)
    with TestClient(appmodule.app,base_url='http://127.0.0.1:8787',client=('127.0.0.1',50000)) as c:
        yield c

HEADERS={'X-MaeMor-Local':'1'}

def test_empty_dashboard_and_csrf_guard(client):
    assert client.get('/').status_code==200
    body=client.get('/api/overview').json()
    assert body['cards'][0]['value'] is None
    assert client.post('/api/report').status_code==403
    assert client.post('/api/report',headers={**HEADERS,'Origin':'https://evil.example'}).status_code==403
    assert client.get('/',headers={'Host':'evil.example'}).status_code==403
    status=client.get('/api/status').json()
    assert status['configured'] is False and status['connected'] is False
    assert status['connection']['status']=='not_configured'

def test_selected_is_not_verified_and_new_page_tasks(client,monkeypatch,memory_secrets):
    cfg=config.settings();cfg['api_version']='v25.0';config.save_settings(cfg)
    memory_secrets.set('user','test-user-token')
    def handler(r):
        if r.url.path.endswith('me/permissions'):
            return httpx.Response(200,json={'data':[]})
        if r.url.path.endswith('me/accounts'):
            return httpx.Response(200,json={'data':[{'id':'123','name':'แม่หมอกระต่าย',
                'tasks':['PROFILE_PLUS_FULL_CONTROL'],'instagram_business_account':{'id':'456'}}]})
        if r.url.path.endswith('/456'):
            return httpx.Response(200,json={'id':'456','username':'maemorkratai'})
        return httpx.Response(200,json={'id':'123','access_token':'test-page-token'})
    monkeypatch.setattr(appmodule,'Graph',lambda version,token,*args,**kw:Graph(version,token,
        transport=httpx.MockTransport(handler),sleeper=lambda x:None))
    selected=client.post('/api/connect/select',headers=HEADERS,json={'page_id':'123'})
    assert selected.status_code==200
    status=client.get('/api/status').json()
    assert status['configured'] is True and status['connected'] is False
    assert memory_secrets.get('page')=='test-page-token'

def test_live_verify_expired_token_does_not_claim_connected(client,monkeypatch,memory_secrets):
    cfg=config.settings();cfg.update(api_version='v25.0',page_id='123',ig_id='456');config.save_settings(cfg)
    memory_secrets.set('page','secret-test-page-token')
    handler=lambda r:httpx.Response(400,json={'error':{'code':190,'message':'secret-test-page-token'}})
    monkeypatch.setattr(appmodule,'Graph',lambda version,token,*args,**kw:Graph(version,token,
        transport=httpx.MockTransport(handler),sleeper=lambda x:None))
    result=client.post('/api/connect/verify',headers=HEADERS).json()
    assert result['status']=='reconnect'
    assert client.get('/api/status').json()['connected'] is False
    assert 'secret-test-page-token' not in str(config.settings())

def test_live_verify_partial_insights_keeps_identity_result(client,monkeypatch,memory_secrets):
    cfg=config.settings();cfg.update(api_version='v25.0',page_id='123',ig_id='456');config.save_settings(cfg)
    memory_secrets.set('page','test-page-token')
    def handler(r):
        if r.url.path.endswith('/insights'):
            return httpx.Response(400,json={'error':{'code':100,'message':'metric unsupported'}})
        if r.url.path.endswith('/456'):
            return httpx.Response(200,json={'id':'456','username':'maemorkratai'})
        if r.url.path.endswith('/123'):
            return httpx.Response(200,json={'id':'123','name':'แม่หมอกระต่าย'})
        return httpx.Response(200,json={'data':[]})
    monkeypatch.setattr(appmodule,'Graph',lambda version,token,*args,**kw:Graph(version,token,
        transport=httpx.MockTransport(handler),sleeper=lambda x:None))
    result=client.post('/api/connect/verify',headers=HEADERS).json()
    assert result['status']=='verified_with_limits'
    assert client.get('/api/status').json()['connected'] is True
    assert any(c['capability']=='insights' and c['status']=='unsupported' for c in result['checks'])

def test_brand_media_allowlist_and_range(client,isolated):
    import json
    root,vault=isolated
    (root/'data/brand-analysis.json').write_text(json.dumps({'scope':'local_references_only'}))
    (vault/'wiki/Images').mkdir(parents=True)
    (vault/'wiki/Images/IMG_5392.JPG').write_bytes(b'test-image-bytes')
    assert client.get('/api/brand').json()['scope']=='local_references_only'
    assert client.get('/api/brand/media/profile-clean').status_code==200
    assert client.get('/api/brand/media/unknown').status_code==404
    assert client.get('/api/brand/media/profile-clean',headers={'Range':'bytes=0-3'}).content==b'test'

def test_channel_style_only_uses_selected_verified_meta_sources(client,isolated):
    import json
    (isolated[0]/'data/brand-analysis.json').write_text(json.dumps({'scope':'local_references_only'}))
    cfg=config.settings();cfg.update(page_id='123',ig_id='456');config.save_settings(cfg)
    csv=store.snapshot('instagram','csv',{}, {},kind='csv')
    store.post('instagram','456',{'id':'csv-1','caption':'ความรัก'},csv)
    assert client.get('/api/brand').json()['channel_audit']['status']=='awaiting_connection'
    cfg['connection']={'status':'verified','checked_at':config.now()};config.save_settings(cfg)
    assert client.get('/api/brand').json()['channel_audit']['status']=='awaiting_content'
    source=store.snapshot('instagram','456/media',{}, {'data':[]})
    store.post('instagram','456',{'id':'real-1','caption':'ไพ่ความรัก','media_type':'IMAGE',
                 'media_url':'https://scontent.cdninstagram.com/image.jpg'},source)
    store.post('instagram','other',{'id':'unselected','caption':'ไม่ใช่ช่องที่เลือก'},source)
    audit=client.get('/api/brand').json()['channel_audit']
    assert audit['status']=='review_ready' and audit['post_count']==1
    assert len(audit['samples'])==1 and audit['samples'][0]['source_id']==source
    assert audit['samples'][0]['thumbnail_url'].endswith('image.jpg')

def test_stale_job_does_not_block_manual_recovery(client):
    with store.db() as c:
        c.execute('INSERT INTO jobs VALUES(?,?,?,?,?)',('crashed','2026-10-01',None,'running','old'))
    status=client.get('/api/status').json()
    assert not status['sync_running']
    assert status['jobs'][0]['status']=='partial'
    assert client.post('/api/report',headers=HEADERS).status_code==200

def test_invalid_connect_does_not_echo_secret(client):
    token='TEST-TOKEN-SECRET-987654321'
    response=client.post('/api/connect/discover',headers=HEADERS,json={'token':token,'api_version':'bad'})
    assert response.status_code==422 and token not in response.text

def test_select_rejects_other_instagram(client,monkeypatch,memory_secrets):
    cfg=config.settings();cfg['api_version']='v25.0';config.save_settings(cfg)
    memory_secrets.set('user','fake-user-token')
    def handler(r):
        if r.url.path.endswith('me/permissions'):return httpx.Response(200,json={'data':[]})
        if r.url.path.endswith('me/accounts'):return httpx.Response(200,json={'data':[
            {'id':'123','name':'Another','tasks':['ANALYZE'],'instagram_business_account':{'id':'456'}}]})
        return httpx.Response(200,json={'username':'wrong-account'})
    monkeypatch.setattr(appmodule,'Graph',lambda version,token,**kw:Graph(version,token,transport=httpx.MockTransport(handler),sleeper=lambda x:None))
    response=client.post('/api/connect/select',headers=HEADERS,json={'page_id':'123'})
    assert response.status_code==400
    assert memory_secrets.get('page') is None

def test_import_preview_mapping_and_source_inspection(client):
    raw=b'Post ID,Views,Publish time\np1,12,2026-10-01\n'
    preview=client.post('/api/import/preview',headers=HEADERS,files={'file':('export.csv',raw)})
    assert preview.json()['mapping']['views']=='Views'
    import json
    response=client.post('/api/import',headers=HEADERS,files={'file':('export.csv',raw)},
        data={'platform':'instagram','account_id':'a','mapping':json.dumps(preview.json()['mapping'])})
    assert response.status_code==200
    sid=response.json()['source_id']
    assert client.get('/api/source/'+sid).json()['snapshot']['kind']=='csv'
    assert client.get('/api/report/latest').status_code==200
    assert client.get('/api/content').json()['rows'][0]['ranking_value']==12
