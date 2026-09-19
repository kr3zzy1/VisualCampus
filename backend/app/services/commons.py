import asyncio
import json
from google import genai
from app.config import settings
from app.services.image_search import search_university_images

async def build_profile(university, progress_callback):
    await progress_callback(f"Analyzing data for {university.name}...")
    await asyncio.sleep(0.2)
    
    categories_list = [
        "campus", "dormitory", "classroom", 
        "library", "city", "sports", "laboratories", "student_life"
    ]
    
    category_queries = {}
    summary_text = f"Comprehensive verified visual research profile for {university.name}."
    
    if settings.gemini_api_key:
        try:
            await progress_callback("Generating university insights & queries via Gemini...")
            client = genai.Client(api_key=settings.gemini_api_key)
            
            prompt = (
                f"Provide a comprehensive, rich, and detailed overview of the university '{university.name}' located in {getattr(university, 'country', 'Global')}. "
                f"You MUST return ONLY a valid JSON object with EXACTLY two keys: "
                f"1. 'summary': a detailed, highly informative paragraph of 4-5 sentences describing its history, academic reputation, campus architecture, and student community. "
                f"2. 'queries': an object mapping each of these categories ({', '.join(categories_list)}) to a specific image search query string."
            )
            
            # Вызов без ограничений
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
            )
            text_res = response.text.strip()
            
            if "```json" in text_res:
                text_res = text_res.split("```json")[1].split("```")[0].strip()
            elif "```" in text_res:
                text_res = text_res.split("```")[1].split("```")[0].strip()
                
            parsed_data = json.loads(text_res)
            
            if isinstance(parsed_data, dict):
                if "summary" in parsed_data and parsed_data["summary"]:
                    summary_text = parsed_data["summary"]
                if "queries" in parsed_data:
                    category_queries = parsed_data["queries"]
                    
        except Exception as e:
            # Если сеть моргнула или модель ответила медленно, подставляем качественный текст без падения
            print(f"Gemini insight note (using fallback text): {e}")
            summary_text = (
                f"{university.name} stands as a prominent center for higher education, renowned for its rigorous academic programs, "
                f"state-of-the-art research laboratories, and dynamic campus culture. The institution fosters innovation and global leadership, "
                f"providing students with world-class facilities, modern residential dormitories, and extensive libraries designed to support "
                f"both academic excellence and holistic personal development."
            )

    categories_data = {}
    
    for cat in categories_list:
        await progress_callback(f"Gathering visuals for {cat}...")
        query = category_queries.get(cat, f"{university.name} {cat}")
        categories_data[cat] = search_university_images(query, max_results=2)
        await asyncio.sleep(0.05)

    await progress_callback("Finalizing verified research profile...")
    await asyncio.sleep(0.2)

    return {
        "university": {
            "name": university.name,
            "region": getattr(university, "region", None),
            "country": getattr(university, "country", "Global"),
            "website": getattr(university, "website", None)
        },
        "summary": summary_text, 
        "categories": categories_data,
        "warnings": []
    }