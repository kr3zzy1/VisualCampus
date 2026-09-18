import asyncio, uuid
from datetime import datetime
from app.models.profile import Profile, ImageItem, University
from app.services.image_search import search_all
from app.services.deduplication import exact_deduplicate, visual_deduplicate
from app.services.confidence import score_image
from app.services.image_verification import verify_with_gemini

async def build_profile(university: University, update):
    await update("Searching real images from Wikimedia Commons…")
    raw=await search_all(university.name); total=sum(map(len,raw.values())); await update(f"Found {total} candidate images")
    await update("Checking metadata relevance and source context…")
    categories={}
    verified=[]
    for category, rows in raw.items():
        unique=visual_deduplicate(exact_deduplicate(rows)); selected=[]
        for r in unique:
            score,reasons=score_image(r['title'],r['search_query'],university.name,category,r['source_domain'])
            vision_match, vision_reason = await verify_with_gemini(r['thumbnail_url'], university.name, category)
            if vision_match is True:
                score=min(95, score + 10); reasons.append(vision_reason)
            elif vision_match is False:
                score=max(0, score - 25); reasons.append(vision_reason)
            else:
                reasons.append(vision_reason)
            status="verified" if score>=70 else "partial" if score>=55 else "unverified"
            # Low-confidence items are intentionally excluded from primary profile.
            if score < 55: continue
            selected.append(ImageItem(id=str(uuid.uuid4()),url=r['url'],thumbnail_url=r['thumbnail_url'],source_url=r['source_url'],source_domain=r['source_domain'],title=r['title'],category=category,university=university.name,city=university.city,confidence=score,verification_status=status,confidence_reasons=reasons,published_date=None,category_confidence=min(score,85)))
        categories[category]=selected[:4]; verified.extend(selected)
    await update(f"Kept {len(verified)} relevant, unique images")
    warnings=[]
    if not verified: warnings.append("No sufficiently verified images were found. Try a more specific university name or configure an additional search provider.")
    missing=[k for k,v in categories.items() if not v]
    if missing: warnings.append("No sufficiently verified images for: "+", ".join(missing)+".")
    overall=(sum(x.confidence for x in verified)/len(verified)/100) if verified else 0
    await update("Generating profile complete")
    return Profile(university=university, summary=f"A source-linked visual profile of {university.name}. Each included image passed metadata and query-context checks; low-confidence candidates were excluded.", categories=categories, overall_confidence=round(overall,2), warnings=warnings)
