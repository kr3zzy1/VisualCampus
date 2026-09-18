import json
import httpx
from app.config import settings
from app.models.profile import University

WIKIDATA = "https://www.wikidata.org/w/api.php"
async def _labels(client: httpx.AsyncClient, ids: list[str]) -> dict[str, str]:
    if not ids: return {}
    r=await client.get(WIKIDATA,params={"action":"wbgetentities","ids":"|".join(ids),"props":"labels","languages":"en","format":"json"}); r.raise_for_status()
    return {qid: entity.get("labels",{}).get("en",{}).get("value","") for qid,entity in r.json().get("entities",{}).items()}

def _claim_id(entity: dict, prop: str) -> str | None:
    claim=(entity.get("claims",{}).get(prop) or [{}])[0]
    return claim.get("mainsnak",{}).get("datavalue",{}).get("value",{}).get("id")

def _claim_text(entity: dict, prop: str) -> str | None:
    claim=(entity.get("claims",{}).get(prop) or [{}])[0]
    value=claim.get("mainsnak",{}).get("datavalue",{}).get("value")
    return value if isinstance(value,str) else None

async def suggest_universities(query: str) -> list[University]:
    params = {"action":"wbsearchentities", "search":query, "language":"en", "format":"json", "limit":5, "type":"item"}
    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds, headers={"User-Agent":"LocusVisualProfile/1.0"}) as client:
        response = await client.get(WIKIDATA, params=params); response.raise_for_status()
    results=[]
    for item in response.json().get("search", []):
        description=item.get("description", "")
        if "universit" not in description.lower() and "college" not in description.lower(): continue
        results.append(University(name=item["label"]))
    return results

async def resolve_university(query: str) -> list[University]:
    results = await suggest_universities(query)
    if results:
        # Enrich only the top match: suggestions intentionally expose no Wikidata IDs.
        try:
            async with httpx.AsyncClient(timeout=settings.request_timeout_seconds, headers={"User-Agent":"LocusVisualProfile/1.0"}) as client:
                search=await client.get(WIKIDATA,params={"action":"wbsearchentities","search":results[0].name,"language":"en","format":"json","limit":1,"type":"item"}); search.raise_for_status()
                top_id=(search.json().get("search") or [{}])[0].get("id")
                if not top_id: return results
                entity_response=await client.get(WIKIDATA,params={"action":"wbgetentities","ids":top_id,"props":"claims","format":"json"}); entity_response.raise_for_status()
                entity=entity_response.json().get("entities",{}).get(top_id,{})
                city_id,country_id=_claim_id(entity,"P131"),_claim_id(entity,"P17")
                names=await _labels(client,[x for x in [city_id,country_id] if x])
                results[0]=University(name=results[0].name,city=names.get(city_id),country=names.get(country_id),website=_claim_text(entity,"P856"))
        except Exception:
            pass
        return results
    return await resolve_with_gemini_search(query)

async def resolve_with_gemini_search(query: str) -> list[University]:
    """Fallback only: Google-grounded Gemini lookup, never model memory alone."""
    if not settings.gemini_api_key:
        return []
    prompt=("Find the university intended by this user query using Google Search: " + query +
            ". Return only JSON with one object: {\"name\": string, \"city\": string|null, "
            "\"country\": string|null, \"website\": string|null}. If it is ambiguous or not a university, return {}. "
            "Use an official university website only; do not guess.")
    payload={"contents":[{"parts":[{"text":prompt}]}],"tools":[{"google_search":{}}],
             "generationConfig":{"temperature":0,"responseMimeType":"application/json"}}
    endpoint=f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent"
    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response=await client.post(endpoint,headers={"x-goog-api-key":settings.gemini_api_key},json=payload)
            response.raise_for_status()
        text=response.json()["candidates"][0]["content"]["parts"][0]["text"]
        data=json.loads(text)
        if not isinstance(data,dict) or not isinstance(data.get("name"),str) or not data["name"].strip(): return []
        website=data.get("website")
        if website and not (website.startswith("https://") or website.startswith("http://")): website=None
        return [University(name=data["name"].strip(),city=data.get("city"),country=data.get("country"),website=website)]
    except Exception:
        return []
