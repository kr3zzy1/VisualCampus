"""Optional Gemini vision verifier. It fails closed: provider trouble never raises confidence."""
import base64
from urllib.parse import urlsplit
import httpx
from app.config import settings

ALLOWED_IMAGE_HOSTS = {"upload.wikimedia.org", "commons.wikimedia.org"}

async def verify_with_gemini(image_url: str, university: str, category: str) -> tuple[bool | None, str]:
    if not settings.gemini_api_key:
        return None, "Gemini visual verification is not configured"
    parsed = urlsplit(image_url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_IMAGE_HOSTS:
        return None, "Image host is not on the verification allowlist"
    try:
        async with httpx.AsyncClient(timeout=8, follow_redirects=False) as client:
            async with client.stream("GET", image_url) as download:
                if download.status_code != 200 or int(download.headers.get("content-length", "0")) > 2_000_000:
                    return None, "Image is unavailable or exceeds verification limit"
                content = bytearray()
                async for part in download.aiter_bytes():
                    content.extend(part)
                    if len(content) > 2_000_000: return None, "Image exceeds verification limit"
        mime = "image/jpeg" if image_url.lower().endswith((".jpg", ".jpeg")) else "image/png"
        prompt = (f"Is this image plausibly a {category.replace('_', ' ')} associated with {university}? "
                  "Answer ONLY JSON: {\"match\": true|false, \"reason\": \"short reason\"}. "
                  "If you cannot verify it, use false.")
        payload={"contents":[{"parts":[{"text":prompt},{"inline_data":{"mime_type":mime,"data":base64.b64encode(content).decode()}}]}],"generationConfig":{"temperature":0,"maxOutputTokens":80,"responseMimeType":"application/json"}}
        endpoint=f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent"
        async with httpx.AsyncClient(timeout=12) as client:
            response=await client.post(endpoint, params={"key":settings.gemini_api_key}, json=payload); response.raise_for_status()
        import json
        text=response.json()["candidates"][0]["content"]["parts"][0]["text"]
        result=json.loads(text)
        return bool(result.get("match")), "Gemini vision: " + str(result.get("reason", "no explanation"))[:180]
    except Exception:
        return None, "Gemini could not verify this image"
