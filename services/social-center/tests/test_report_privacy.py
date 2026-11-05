from maemorkratai import store,report

def test_thread_ids_not_exported(isolated):
    sid=store.snapshot('instagram','test',{},{} )
    store.account('instagram','a','test','',None,sid)
    store.coverage('instagram','a','private-comment-id-123/replies','permission','อ่านไม่ได้')
    out=report.write_report()
    exported=''.join(p.read_text() for p in isolated[1].rglob('*') if p.is_file())
    assert 'private-comment-id-123' not in exported
    assert 'content-or-thread/replies' in open(out['path']).read()
