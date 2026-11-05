import json
import httpx
import pytest
from maemorkratai import store
from maemorkratai.meta import Graph, MetaError, discovery, ingest_insight
from maemorkratai.sync import collect

TOKEN='TEST-SECRET-DO-NOT-PERSIST-12345'

def make(handler,budget=20):
    return Graph('v25.0',TOKEN,transport=httpx.MockTransport(handler),sleeper=lambda x:None,budget=budget)

def test_pagination_cursor_and_redaction(isolated):
    requests=[]
    def handler(r):
        requests.append(r)
        assert r.url.host=='graph.facebook.com'
        assert r.headers['Authorization']=='Bearer '+TOKEN
        if r.url.params.get('after')=='cursor-a':
            return httpx.Response(200,json={'data':[{'id':'b'}]})
        return httpx.Response(200,json={'data':[{'id':'a','access_token':TOKEN}],
             'paging':{'cursors':{'after':'cursor-a'},'next':'https://untrusted.example/?access_token='+TOKEN}})
    graph=make(handler)
    collected=[]
    collect(graph,'instagram','a','a/media','id',lambda item,s:collected.append(item['id']),'key')
    assert collected==['a','b']
    assert store.checkpoint('key')['complete']==1
    assert len(requests)==2
    for p in (isolated[0]/'data/snapshots').glob('*.json'):
        assert TOKEN not in p.read_text()
        assert 'access_token":' not in p.read_text()
    graph.close()

def test_resume_after_rate_limit():
    def handler(r):
        if r.url.params.get('after'):
            return httpx.Response(429,json={'error':{'code':4,'message':TOKEN}})
        return httpx.Response(200,json={'data':[{'id':'a'}],
                     'paging':{'cursors':{'after':'cursor-a'},'next':'https://graph.facebook.com/a'}})
    graph=make(handler)
    with pytest.raises(MetaError,match='จำกัดการเรียก'):
        list(graph.pages('a/media',key='k'))
    assert store.checkpoint('k')['cursor']=='cursor-a'
    resumed=make(lambda r:httpx.Response(200,json={'data':[{'id':'b'}]}))
    assert list(resumed.pages('a/media',key='k'))[0][0]==[{'id':'b'}]
    assert store.checkpoint('k')['complete']==1

def test_expired_token_is_safe():
    graph=make(lambda r:httpx.Response(400,json={'error':{'code':190,'message':TOKEN}}))
    with pytest.raises(MetaError) as e: graph.get('me')
    assert e.value.category=='expired' and TOKEN not in str(e.value)

def test_unsupported_metric_is_not_zero():
    graph=make(lambda r:httpx.Response(400,json={'error':{'code':100,'message':'invalid metric'}}))
    with pytest.raises(MetaError) as e: graph.get('a/insights',{'metric':'old_metric'})
    assert e.value.category=='unsupported'
    assert not store.rows('SELECT * FROM metrics')

def test_discovery_all_pages_and_linked_ig():
    def handler(r):
        if r.url.path.endswith('me/permissions'):
            return httpx.Response(200,json={'data':[{'permission':'pages_show_list','status':'granted'}]})
        if r.url.path.endswith('me/accounts'):
            return httpx.Response(200,json={'data':[{'id':'123','name':'แม่หมอกระต่าย','tasks':['ANALYZE'],
                                         'instagram_business_account':{'id':'456'}}]})
        return httpx.Response(200,json={'id':'456','username':'maemorkratai'})
    result=discovery(make(handler))
    assert result['pages'][0]['ig_username']=='maemorkratai'
    assert result['permissions']==['pages_show_list']

def test_request_budget_does_not_silently_finish():
    graph=make(lambda r:httpx.Response(200,json={'data':[]}),budget=1)
    graph.get('me')
    with pytest.raises(MetaError) as e: graph.get('me')
    assert e.value.category=='budget'

def test_no_external_endpoint_and_no_repeat_cursor():
    graph=make(lambda r:httpx.Response(200,json={'data':[],
                           'paging':{'cursors':{'after':'same'},'next':'x'}}))
    with pytest.raises(ValueError): graph.get('https://other.example/')
    with pytest.raises(MetaError): list(graph.pages('a/media'))

def test_watch_time_native_units():
    sid=store.snapshot('instagram','test',{},{} )
    ingest_insight('instagram','a','p','ig_reels_avg_watch_time',{'data':[
        {'name':'ig_reels_avg_watch_time','period':'lifetime','values':[{'value':2400}]}]},sid)
    row=store.rows('SELECT * FROM metrics')[0]
    assert row['metric']=='watch_time' and row['unit']=='milliseconds' and row['value']==2400
