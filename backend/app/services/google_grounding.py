"""Google Search grounding enriches a profile with cited web pages, never invented image URLs."""
import httpx
from app.config import settings
from app.models.profile import University,WebSource
async def sources_for(university:University)->list[WebSource]:
 if not settings.gemini_api_key:return []
 prompt=f"Find official or authoritative web pages about {university.name} campus, facilities, student life and location. Use Google Search."
 payload={'contents':[{'parts':[{'text':prompt}]}],'tools':[{'google_search':{}}],'generationConfig':{'temperature':0,'maxOutputTokens':180}}
 try:
  async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as c:r=await c.post('https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent',headers={'x-goog-api-key':settings.gemini_api_key},json=payload);r.raise_for_status()
  chunks=((r.json().get('candidates')or[{}])[0].get('groundingMetadata',{}).get('groundingChunks',[]));seen=set();out=[]
  for chunk in chunks:
   web=chunk.get('web')or{};url=web.get('uri');title=web.get('title')or url
   if url and url.startswith('http') and url not in seen:seen.add(url);out.append(WebSource(title=title,url=url))
  return out[:6]
 except Exception:return []
