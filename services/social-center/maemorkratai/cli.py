import argparse
import json
from datetime import datetime
from .config import ROOT, TZ, settings, now
from . import store

def main():
    parser=argparse.ArgumentParser(description='แม่หมอกระต่าย — local social center')
    parser.add_argument('command',choices=['serve','init','sync','report'])
    parser.add_argument('--scheduled',action='store_true')
    parser.add_argument('--port',type=int,default=8787)
    args=parser.parse_args()
    store.init()
    if args.command=='init':
        from .vault import initialize
        initialize()
        print('สร้างโครงคลังแล้ว ยังไม่ได้เชื่อมข้อมูลจริง')
    elif args.command=='serve':
        import uvicorn
        uvicorn.run('maemorkratai.app:app',host='127.0.0.1',port=args.port,access_log=False)
    elif args.command=='report':
        from .report import write_report
        print(json.dumps(write_report(),ensure_ascii=False))
    else:
        cfg=settings()
        if args.scheduled:
            date=datetime.now(TZ)
            marker=ROOT/'data/last-scheduled.json'
            previous=json.loads(marker.read_text()) if marker.exists() else {}
            if date.hour<8 or previous.get('date')==str(date.date()) or not cfg['page_id']:
                print(f'{now()} — ข้ามรอบ: ยังไม่ถึงเวลา/ยังไม่เชื่อม/ทำแล้ววันนี้')
                return
        from .sync import run_sync
        from .report import write_report
        try:
            result=run_sync()
            result['report']=write_report()
        except ValueError as e:
            result={'status':'blocked','message':str(e)}
        if args.scheduled:
            marker.write_text(json.dumps({'date':str(date.date()),'status':result['status']}))
        print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':
    main()
