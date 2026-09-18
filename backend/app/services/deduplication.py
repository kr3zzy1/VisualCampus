import hashlib
from urllib.parse import urlsplit, urlunsplit

def exact_deduplicate(items: list[dict]) -> list[dict]:
    seen=set(); result=[]
    for item in items:
        key=hashlib.sha256(urlunsplit((*urlsplit(item["url"])[:3],"","")).encode()).hexdigest()
        if key not in seen: seen.add(key); result.append(item)
    return result

# Network-safe MVP: URL exact matching is always available. pHash is applied only after
# explicitly bounded image download; omitted here so arbitrary hosts are never fetched.
def visual_deduplicate(items: list[dict]) -> list[dict]:
    seen_titles=set(); result=[]
    for item in items:
        normalized="".join(c.lower() for c in item["title"] if c.isalnum())
        if normalized not in seen_titles: seen_titles.add(normalized); result.append(item)
    return result
