from pathlib import Path
from fastapi import FastAPI,HTTPException
from fastapi.responses import FileResponse
import uvicorn
ROOT=Path(__file__).resolve().parent
app=FastAPI(docs_url=None,redoc_url=None,openapi_url=None)
@app.get('/')
def home(): return FileResponse(ROOT/'preview.html')
@app.get('/{name:path}')
def asset(name:str):
    allowed={'index.html','preview.html','renders/MaeMorKratai_end_credit_v1.mp4'}
    p=(ROOT/name).resolve()
    if not p.is_relative_to(ROOT) or not p.is_file() or not (name in allowed or (name.startswith('assets/') and p.suffix in ('.jpg','.svg','.js','.ttf'))):raise HTTPException(404)
    return FileResponse(p)
if __name__=='__main__':uvicorn.run(app,host='127.0.0.1',port=3003,access_log=False)
