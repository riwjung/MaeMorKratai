import csv
import io
import json
from datetime import datetime,timedelta
import pytest
from maemorkratai import store, analysis, importer, report
from maemorkratai.config import TZ

def csv_bytes(rows):
    out=io.StringIO()
    writer=csv.DictWriter(out,fieldnames=list(rows[0]))
    writer.writeheader(); writer.writerows(rows)
    return out.getvalue().encode()

def test_ten_posts_source_reconciliation_and_idempotence(isolated):
    records=[{'Post ID':f'item-{i}','Publish time':'2026-10-01','Description':f'ความรัก ไพ่ {i}',
              'Views':i*17,'Shares':i,'Post link':f'https://www.instagram.com/p/item{i}/'} for i in range(1,11)]
    raw=csv_bytes(records)
    result=importer.import_csv(raw,'instagram','ig-test')
    assert result['rows']==10
    assert importer.import_csv(raw,'instagram','ig-test')['status']=='unchanged'
    posts=analysis.content('instagram')
    assert len(posts)==10
    from maemorkratai.verify import verify_samples
    verification=verify_samples()['instagram']
    assert verification['posts_checked']==10 and verification['status']=='matched'
    for p in posts:
        expected=next(r for r in records if r['Post ID']==p['post_id'])
        assert p['metrics']['views']['value']==expected['Views']
        assert p['metrics']['shares']['value']==expected['Shares']
        assert p['metrics']['saves'] is None
        source=store.rows('SELECT * FROM sources WHERE id=?',(p['metrics']['views']['source_id'],))[0]
        payload=json.loads(open(source['path']).read())
        assert payload['kind']=='csv'
        assert payload['data']['rows'][int(p['post_id'].split('-')[1])-1]['Views']==str(expected['Views'])
    out=report.write_report()
    text=open(out['path']).read()
    assert 'ยอดดูสะสม' in text and '170' in text and 'สมมติฐาน' in text
    assert len(list((isolated[1]/'raw').glob('*.json')))==1
    report.write_report()
    assert len(list((isolated[1]/'raw').glob('*.json')))==2

def test_daily_windows_do_not_use_post_lifetime():
    at=datetime(2026,10,14,tzinfo=TZ)
    daily=[{'Date':str((at-timedelta(days=i)).date()),'Views':10 if i<=30 else 5,
            'Total interactions':1} for i in range(1,61)]
    importer.import_csv(csv_bytes(daily),'instagram','ig-test',kind='daily')
    importer.import_csv(csv_bytes([{'Post ID':'p','Views':999999,'Publish time':'2026-01-01'}]),'instagram','ig-test')
    overview=analysis.overview('instagram',at)
    views=next(c for c in overview['cards'] if c['metric']=='views')
    assert views['current']['value']==300
    assert views['previous']['value']==150
    assert views['change_pct']==100
    assert overview['cards'][0]['value'] is None

def test_missing_day_is_not_zero():
    at=datetime(2026,10,14,tzinfo=TZ)
    daily=[{'Date':str((at-timedelta(days=i)).date()),'Views':0} for i in range(1,30)]
    importer.import_csv(csv_bytes(daily),'facebook','page-test',kind='daily')
    card=analysis.overview('facebook',at)['cards'][1]
    assert card['current']['value'] is None
    assert card['current']['days']==29

def test_follower_snapshots_use_measurement_date_not_import_order():
    at=datetime(2026,10,14,tzinfo=TZ)
    daily=[{'Date':str((at-timedelta(days=i)).date()),'Followers':200-i} for i in range(60,0,-1)]
    importer.import_csv(csv_bytes(daily),'instagram','a',kind='daily')
    overview=analysis.overview('instagram',at)
    assert overview['cards'][0]['value']==199
    assert overview['cards'][0]['measured_at'].startswith('2026-10-13')
    assert overview['follower_growth_30d']==30

def test_follower_trend_keeps_missing_days_and_window():
    at=datetime(2026,10,14,tzinfo=TZ)
    rows=[{'Date':'2026-10-13','Followers':50},{'Date':'2026-10-03','Followers':40},
          {'Date':'2026-01-01','Followers':2}]
    importer.import_csv(csv_bytes(rows),'instagram','a',kind='daily')
    trend=analysis.overview('instagram',at)['follower_trend']
    assert len(trend)==90
    assert [r['date'] for r in trend]==sorted(r['date'] for r in trend)
    assert sum(r['value'] is not None for r in trend)==2
    assert next(r for r in trend if r['date']=='2026-10-12')['value'] is None

def test_exact_range_and_not_mixed_with_lifetime():
    at=datetime(2026,10,14,tzinfo=TZ)
    sid=store.snapshot('instagram','test',{},{} )
    store.account('instagram','a','test','',None,sid)
    store.metric('instagram','a','a','views','views','total_over_range',
                 '2026-09-14T00:00:00+07:00','2026-10-14T00:00:00+07:00',123,sid)
    assert analysis.overview('instagram',at)['cards'][1]['current']['value']==123
    importer.import_csv(csv_bytes([{'Post ID':'p','Views':44}]),'instagram','a',
                        period='total_over_range',start='2026-10-01',end='2026-10-14')
    assert analysis.content('instagram')[0]['metrics']['views'] is None
    assert analysis.content('instagram')[0]['ranged_metrics'][0]['value']==44

def test_duplicate_native_metrics_do_not_double_total():
    at=datetime(2026,10,14,tzinfo=TZ)
    sid=store.snapshot('instagram','test',{},{} )
    store.account('instagram','a','test','',None,sid)
    for i in range(1,31):
        s=at-timedelta(days=i); e=s+timedelta(days=1)
        for native in ('views','total_views'):
            store.metric('instagram','a','a','views',native,'day',s.isoformat(),e.isoformat(),2,sid)
    assert analysis.overview('instagram',at)['cards'][1]['current']['value']==60

def test_validate_csv_before_writing_and_reject_secrets():
    for raw in (b'Post ID,Views\na,10\nb,wrong\n', b'Post ID,Views,access_token\na,10,secret\n'):
        with pytest.raises(ValueError): importer.import_csv(raw,'instagram','a')
    assert not store.rows('SELECT * FROM posts')
    assert not store.rows('SELECT * FROM sources')

def test_ambiguous_dates_are_not_guessed():
    with pytest.raises(ValueError,match='กำกวม'):
        importer.import_csv(b'Post ID,Views,Date\np,3,10/11/2026\n','instagram','a')
    assert not store.rows('SELECT * FROM posts')

def test_comment_report_aggregate_only():
    importer.import_csv(csv_bytes([{'Post ID':'p','Comment ID':'c','Text':'ความรัก confidential-person'}]),
                        'instagram','a',kind='comments')
    out=report.write_report()
    assert analysis.findings('instagram')['comment_themes']=={'ความรัก':1}
    assert 'confidential-person' not in open(out['path']).read()
    assert 'confidential-person' not in ''.join(p.read_text() for p in out_path(out).parents[2].rglob('*.json'))

def out_path(out):
    from pathlib import Path
    return Path(out['path'])
def test_media_migration_preserves_posts_and_rejects_credential_urls():
    from maemorkratai import store
    source=store.snapshot('instagram','media',{}, {})
    store.post('instagram','123',{'id':'1','caption':'original','media_type':'IMAGE',
        'media_url':'https://scontent.cdninstagram.com/a.jpg'},source)
    store.init()
    store.post('instagram','123',{'id':'1','caption':'updated'},source)
    found=store.rows('SELECT * FROM posts')[0]
    assert found['text']=='updated' and found['media_url'].endswith('a.jpg')
    assert found['thumbnail_url'].endswith('a.jpg')
    assert store.media_url('https://cdninstagram.com/a.jpg?access_token=secret')==''
    assert store.media_url('https://cdninstagram.com.evil.example/a.jpg')==''
    assert store.media_url('https://user:pass@cdninstagram.com/a.jpg')==''  # public-release: synthetic URL rejection fixture
