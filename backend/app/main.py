import asyncio,uuid
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.models.profile import Job,SearchRequest,University
from app.services.university_database import suggest,exact,records
from app.services.commons import build_profile
app=FastAPI(title='Visual Campus API');app.add_middleware(CORSMiddleware,allow_origins=settings.allowed_origins.split(','),allow_methods=['*'],allow_headers=['*']);jobs={}
@app.get('/health')
async def health():return {'ok':True,'universities':len(records()),'gemini_configured':bool(settings.gemini_api_key)}
@app.get('/api/universities/suggest',response_model=list[University])
async def suggestions(query:str=''):return suggest(query)
@app.post('/api/search',response_model=Job)
async def search(body:SearchRequest):
 u,c=exact(body.query);jid=str(uuid.uuid4())
 if not c:raise HTTPException(404,'University not found in the local directory. Try a different spelling.')
 if not u:jobs[jid]=Job(id=jid,status='ambiguous',candidates=c,progress=['Select an official university name']);return jobs[jid]
 jobs[jid]=Job(id=jid,status='processing',progress=[f'Found {u.name} in the local directory']);asyncio.create_task(run(jid,u));return jobs[jid]
@app.post('/api/search/{jid}/select',response_model=Job)
async def select(jid:str,u:University):
 if jid not in jobs:raise HTTPException(404,'Search expired')
 jobs[jid]=Job(id=jid,status='processing',progress=[f'Selected {u.name}']);asyncio.create_task(run(jid,u));return jobs[jid]
@app.get('/api/search/{jid}',response_model=Job)
async def status(jid:str):
 if jid not in jobs:raise HTTPException(404,'Search expired')
 return jobs[jid]
async def run(jid,u):
 async def progress(x):jobs[jid].progress.append(x)
 try:jobs[jid].profile=await asyncio.wait_for(build_profile(u,progress),29);jobs[jid].status='completed'
 except Exception:jobs[jid].status='failed';jobs[jid].error='Image provider is unavailable. No fake results were created.'
