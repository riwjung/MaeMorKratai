"""Reconcile ten posts per platform against their immutable source responses."""
import json
import math
from pathlib import Path
from . import analysis, store
from .importer import number

def source_values(source, post, metric):
    payload = json.loads(Path(source['path']).read_text())
    native = metric['native_metric']
    if payload['kind']=='csv':
        mapping = payload['parameters']['mapping']
        values = []
        for row in payload['data']['rows']:
            ident = row.get(mapping.get('post_id',''))
            link = row.get(mapping.get('permalink',''))
            if ident==post['post_id'] or (link and link==post['permalink']):
                value = number(row.get(native))
                if value is not None:
                    values.append(value)
        return values
    values = []
    for item in payload['data'].get('data',[]):
        if item.get('name')==native:
            values += [v['value'] for v in item.get('values',[]) if isinstance(v.get('value'),(int,float))]
            value = item.get('total_value',{}).get('value')
            if isinstance(value,(int,float)):
                values.append(value)
        if str(item.get('id'))==post['post_id']:
            value = item.get(native)
            if isinstance(value,dict):
                value = value.get('count',value.get('summary',{}).get('total_count'))
            if isinstance(value,(int,float)):
                values.append(value)
    return values

def verify_samples():
    results = {}
    for platform in ('facebook','instagram'):
        content = analysis.content(platform)
        posts = [p for p in content if any(p['metrics'].values())][:10]
        checks = []
        for p in posts:
            compared = []
            for name,m in p['metrics'].items():
                if not m:
                    continue
                sources = store.rows('SELECT * FROM sources WHERE id=?',(m['source_id'],))
                values = source_values(sources[0],p,m) if sources else []
                compared.append({'metric':name,'source_id':m['source_id'],
                    'status':('matched' if any(math.isclose(v,m['value'],rel_tol=1e-9) for v in values)
                              else 'mismatch' if values else 'not_comparable')})
            checks.append({'post_id':p['post_id'],'permalink':p['permalink'],'metrics':compared})
        statuses = [m['status'] for p in checks for m in p['metrics']]
        results[platform] = {'posts_checked':len(checks),'required':min(10,len(content)),
            'status':'mismatch' if 'mismatch' in statuses else 'matched' if statuses and all(s=='matched' for s in statuses) and len(checks)>=min(10,len(content))
                     else 'pending' if not statuses else 'incomplete', 'checks':checks,
            'basis':'เทียบ snapshot ต้นทางของช่วงวัดเดียวกัน ไม่ใช่การตรวจย้อนหลังจากหน้าจอ Meta'}
    return results
