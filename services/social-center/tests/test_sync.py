from datetime import datetime,timedelta
import httpx
from maemorkratai import config,store,sync
from maemorkratai.meta import Graph
from maemorkratai.config import TZ

def configure(memory_secrets):
    cfg=config.settings()
    cfg.update(api_version='v25.0',page_id='123',ig_id='456',
        facebook_account_metrics=['page_media_view'],facebook_post_metrics=['post_media_view'],
        instagram_account_metrics=['views'],instagram_post_metrics=['views'])
    config.save_settings(cfg)
    memory_secrets.set('page','synthetic-keychain-token')

def test_full_two_platform_sync_and_rerun(monkeypatch,memory_secrets):
    configure(memory_secrets)
    def handler(r):
        path=r.url.path.split('/v25.0/')[1]
        assert r.method=='GET'
        if path in ('123','456'):
            return httpx.Response(200,json={'id':path,'name':'test','username':'maemorkratai','followers_count':22})
        if path.endswith('/insights'):
            name=r.url.params['metric'];start=r.url.params.get('since');end=r.url.params.get('until')
            values=[]
            if start:
                date=datetime.fromisoformat(start)
                while date<datetime.fromisoformat(end):
                    values.append({'value':3,'end_time':(date+timedelta(days=1)).isoformat()})
                    date+=timedelta(days=1)
            else:values=[{'value':33}]
            return httpx.Response(200,json={'data':[{'name':name,'period':'day' if start else 'lifetime','values':values}]})
        if path.endswith('/published_posts'):
            return httpx.Response(200,json={'data':[{'id':'123_9','created_time':datetime.now(TZ).isoformat(),
                    'message':'ไพ่ความรัก','permalink_url':'https://www.facebook.com/123/posts/9',
                    'full_picture':'https://scontent.fbcdn.net/fb.jpg',
                    'comments':{'summary':{'total_count':1}}}]})
        if path.endswith('/video_reels'):
            return httpx.Response(200,json={'data':[{'id':'9','created_time':datetime.now(TZ).isoformat(),
                    'description':'ไพ่ความรัก','permalink_url':'https://www.facebook.com/123/posts/9'}]})
        if path.endswith('/media'):
            return httpx.Response(200,json={'data':[{'id':'media-1','timestamp':datetime.now(TZ).isoformat(),
                    'caption':'การงาน','media_product_type':'REELS','like_count':7,'comments_count':1,
                    'thumbnail_url':'https://scontent.cdninstagram.com/ig.jpg',
                    'media_url':'https://scontent.cdninstagram.com/ig.mp4'}]})
        if path in ('123_9/comments','media-1/comments'):
            return httpx.Response(200,json={'data':[{'id':path.split('/')[0]+'-comment','text':'ความรัก',
                                                   'timestamp':datetime.now(TZ).isoformat()}]})
        return httpx.Response(200,json={'data':[]})
    monkeypatch.setattr(sync,'Graph',lambda v,t,p,b:Graph(v,t,p,b,transport=httpx.MockTransport(handler),sleeper=lambda x:None))
    assert sync.run_sync(memory_secrets)['status']=='complete'
    assert len(store.rows('SELECT * FROM posts'))==2
    assert len(store.rows('SELECT * FROM comments'))==2
    assert store.rows("SELECT thumbnail_url FROM posts WHERE platform='facebook'")[0]['thumbnail_url'].endswith('fb.jpg')
    assert store.rows("SELECT media_url FROM posts WHERE platform='instagram'")[0]['media_url'].endswith('ig.mp4')
    from maemorkratai.analysis import overview
    assert overview('instagram')['cards'][1]['current']['value']==90
    assert sync.run_sync(memory_secrets)['status']=='complete'
    assert len(store.rows('SELECT * FROM posts'))==2
    assert len(store.rows('SELECT * FROM comments'))==2

def test_job_marks_expired_and_preserves_data(monkeypatch,memory_secrets):
    configure(memory_secrets)
    handler=lambda r:httpx.Response(400,json={'error':{'code':190,'message':'synthetic-keychain-token'}})
    monkeypatch.setattr(sync,'Graph',lambda v,t,p,b:Graph(v,t,p,b,transport=httpx.MockTransport(handler),sleeper=lambda x:None))
    result=sync.run_sync(memory_secrets)
    assert result['status']=='reconnect'
    assert 'synthetic-keychain-token' not in str(store.rows('SELECT * FROM jobs'))

def test_optional_media_fields_fallback_keeps_posts():
    from maemorkratai.meta import MetaError
    class OptionalFieldsGraph:
        def pages(self,endpoint,params,key=None):
            if 'thumbnail_url' in params['fields']:
                raise MetaError('unsupported')
            yield [{'id':'one','caption':'ไพ่'}],store.snapshot('instagram',endpoint,params,{'data':[]})
    sync.collect(OptionalFieldsGraph(),'instagram','123','123/media','id,thumbnail_url',
        lambda item,source:store.post('instagram','123',item,source),'key','id')
    assert len(store.rows('SELECT * FROM posts'))==1
    assert store.rows("SELECT status FROM coverage WHERE metric='media_preview'")[0]['status']=='unsupported'
