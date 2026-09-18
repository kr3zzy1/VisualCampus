"""Optional, server-only Gemini grounding and vision checks.

Gemini never supplies image URLs: Wikimedia remains the traceable image source.
"""
import base64
from urllib.parse import urlsplit
import httpx
from app.config import settings

API='https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
ALLOWED_HOSTS={'upload.wikimedia.org','commons.wikimedia.org'}

async def call(payload:dict)->str|None:
    if not settings.gemini_api_key:return None
    try:
        async with httpx.AsyncClient(timeout=12) as client:
            r=await client.post(API.format(model=settings.gemini_model),headers={'x-goog-api-key':settings.gemini_api_key},json=payload)
            r.raise_for_status()
        return r.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception:return None

async def ground_university(name:str,domain:str|None)->bool:
    text=(f"Use Google Search to confirm that {name} is a university" + (f" with official domain {domain}" if domain else '') + ". Answer only YES or NO.")
    result=await call({'contents':[{'parts':[{'text':text}]}],'tools':[{'google_search':{}}],'generationConfig':{'temperature':0,'maxOutputTokens':5}})
    return bool(result and result.upper().startswith('YES'))

async def vision_match(image_url:str,name:str,category:str)->bool|None:
    parsed=urlsplit(image_url)
    if parsed.scheme!='https' or parsed.hostname not in ALLOWED_HOSTS:return None
    try:
        async with httpx.AsyncClient(timeout=7,follow_redirects=False) as client:
            async with client.stream('GET',image_url) as response:
                if response.status_code!=200 or int(response.headers.get('content-length','0'))>1_500_000:return None
                data=bytearray()
                async for chunk in response.aiter_bytes():
                    data.extend(chunk)
                    if len(data)>1_500_000:return None
        mime=response.headers.get('content-type','image/jpeg').split(';')[0]
        prompt=f"Does this image plausibly show {category.replace('_',' ')} at or directly related to {name}? Answer only YES or NO. If uncertain, answer NO."
        result=await call({'contents':[{'parts':[{'text':prompt},{'inline_data':{'mime_type':mime,'data':base64.b64encode(data).decode()}}]}],'generationConfig':{'temperature':0,'maxOutputTokens':5}})
        if result is None:return None
        return result.upper().startswith('YES')
    except Exception:return None
