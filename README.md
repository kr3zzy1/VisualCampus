# LOCUS Visual Campus

Working MVP for LOCUS Startup Hackathon 2026 Case 01: a university name becomes a source-linked visual profile. It deliberately favors fewer verifiable images over attractive but unsupported results.

## What it does

The search bar accepts official names and common initial-based abbreviations generated from the local directory (for example, `MIT`, `KBTU`).

When a Gemini key is configured, the backend uses Google Search grounding to corroborate the university context and Gemini Vision to assess Wikimedia candidates. Gemini never invents photo URLs: it only accepts/rejects traceable Wikimedia results.

1. Resolves a real university entity using the Wikidata API. If Wikidata cannot find it and Gemini is configured, the app uses Gemini with Google Search grounding as a source-backed fallback (not model memory).
2. Searches each category concurrently through a pluggable image-search provider (Wikimedia Commons is enabled by default, so no key is required).
3. Retains source page, file URL, title, domain and available metadata for every item.
4. Filters by university/category evidence, gives each result an explainable confidence score, and excludes low-confidence candidates.
   When `GEMINI_API_KEY` is configured, a bounded server-side Gemini vision check adds or removes confidence; an unavailable vision call never improves an image's score.
5. Removes URL-level exact duplicates and normalized-title visual candidates. The deduplication service is isolated for safe future bounded-download pHash/embedding support.
6. Caches completed profiles in-memory with a configurable TTL, reports progress, supports ambiguous choices, timeouts and honest errors.

## Architecture

```
frontend/                 React + TypeScript + Vite UI
backend/app/
  services/               resolution, provider, verification, confidence, deduplication, generation
  models/                 API models
  utils/cache.py          TTL cache boundary (replaceable with Redis/SQLite)
```

`POST /api/search` creates a job; `GET /api/search/{id}` exposes status, progress and the profile. `POST /api/search/{id}/select` continues an ambiguous resolution.

## Setup

Copy `.env.example` to `.env`. The default provider needs no secret:

```powershell
Copy-Item .env.example .env
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8010
```

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The Vite proxy keeps the API key boundary on the backend.

## Environment variables

| Variable | Purpose |
| --- | --- |
| `SEARCH_PROVIDER` | `wikimedia` by default; provider abstraction supports SerpAPI extension |
| `SERPAPI_KEY` | Reserved for a future SerpAPI adapter; never sent to the browser |
| `OPENAI_API_KEY` | Reserved for optional AI visual verification |
| `GEMINI_API_KEY` | Optional Gemini API key for server-side visual verification |
| `GEMINI_MODEL` | Gemini model name, default `gemini-2.0-flash` |
| `CACHE_TTL_SECONDS` | Cache lifetime, default 3600 |
| `REQUEST_TIMEOUT_SECONDS` | Per-provider HTTP timeout |
| `ALLOWED_ORIGINS` | CORS origin list |

## Confidence and sources

The score is evidence, not a claim of visual certainty: title/query university match, category context, and traceable-source metadata contribute reasons displayed by the API. A score below 55 is excluded. Every card links to its actual Wikimedia Commons file page. Dates are `null` where metadata cannot safely be normalized; the UI never invents one.

## Safety and limitations

- The default provider searches only public Commons material, so coverage varies greatly by university/category.
- Current MVP uses URL exact hashes and normalized filename/title similarity. For production pHash, use the existing deduplication boundary with an allowlist and strict byte/media limits before downloading remote media; do not indiscriminately fetch arbitrary image URLs.
- Wikimedia/Wikidata entity records may not include city, country or official website in this compact MVP. Enrich these via Wikidata entity claims in the next iteration.
- No fake records, images, sources or successful fallback responses are generated. A provider outage returns an error.

## Testing and verification

```powershell
cd backend
pytest
curl http://localhost:8000/health
```

Manual scenarios: search `Harvard University`, `Qatar University`, an unknown university, an empty query, and a short ambiguous query. Expect the API to expose ambiguity when it cannot safely choose an entity.

## Docker

```powershell
docker compose up --build
```

## External services and libraries

Wikidata and Wikimedia Commons APIs, FastAPI, HTTPX, Pydantic, React, Vite and TypeScript. The deduplication boundary is designed for future secure bounded-download pHash implementation.

## Team roles

Frontend/product UI, backend/search integration, and verification/data-quality can work independently through the service boundaries above.
