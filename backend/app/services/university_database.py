import json,re
from functools import lru_cache
from app.config import settings
from app.models.profile import University
@lru_cache(maxsize=1)
def records():
 with settings.university_data_path.open(encoding='utf-8') as f:return json.load(f)
def norm(s):return re.sub(r'[^a-z0-9]+',' ',s.lower()).strip()
def acronym(name):
 words=re.findall(r"[A-Za-z0-9]+",name);ignored={'of','the','and','for','at','in','de','la','university','college','school'}
 return ''.join(w[0] for w in words if w.lower() not in ignored).upper()
def university(r):
 return University(name=r['name'],country=r.get('country'),region=r.get('state-province'),website=(r.get('web_pages')or[None])[0],domain=(r.get('domains')or[None])[0])
def suggest(query,limit=8):
 q=norm(query);out=[]
 if len(q)<2:return out
 for r in records():
  n=norm(r['name']);abbr=acronym(r['name']).lower();domain=(r.get('domains')or[''])[0].split('.')[0].lower();score=100 if n==q else 99 if domain==q.replace(' ','') else 95 if abbr==q.replace(' ','') and len(q)>=2 else 70 if n.startswith(q) else 45 if q in n else 0
  if score:out.append((score,len(n),r))
 return [university(x[2]) for x in sorted(out,key=lambda x:(-x[0],x[1]))[:limit]]
def exact(query):
 candidates=suggest(query);q=norm(query);compact=q.replace(' ','')
 direct=next((u for u in candidates if norm(u.name)==q or (u.domain and u.domain.split('.')[0].lower()==compact)),None)
 return direct,candidates
