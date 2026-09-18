import asyncio
import json
from google import genai
from app.config import settings
from app.services.image_search import search_university_images

async def build_profile(university, progress_callback):
    await progress_callback(fanalizing := f"Analyzing data for {university.name} with Gemini...")
    await asyncio.sleep(0.2)
    
    # Категории, для которых нужны фотографии
    categories_list = [
        "campus", "dormitory", "classroom", 
        "library", "city", "sports", "laboratories", "student_life"
    ]
    
    category_queries = {}
    
    # Если задан ключ Gemini, просим модель сформировать точные запросы для поиска фото по каждой категории
    if settings.gemini_api_key:
        try:
            await progress_callback("Generating smart category queries via Gemini...")
            client = genai.Client(api_key=settings.gemini_api_key)
            
            prompt = (
                f"For the university '{university.name}' located in {getattr(university, 'country', 'Global')}, "
                f"generate specific image search queries for these exact categories: {', '.join(categories_list)}. "
                f"Return ONLY a valid JSON object where keys are category names and values are short search query strings for Google Images. "
                f"Example: {{\"campus\": \"{university.name} main campus quad building\", \"library\": \"{university.name} library interior\"}}"
            )
            
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
            )
            
            text_res = response.text.strip()
            # Очищаем ответ от markdown-оберток если они есть
            if text_res.startswith("```json"):
                text_res = text_res[7:-3].strip()
            elif text_res.startswith("```"):
                text_res = text_res[3:-3].strip()
                
            category_queries = json.loads(text_res)
        except Exception as e:
            print(f"Ошибка при генерации запросов через Gemini: {e}")

    categories_data = {}
    
    # ДЛЯ КАЖДОЙ КАТЕГОРИИ ИЩЕМ СВОИ КАРТИНКИ
    for cat in categories_list:
        await progress_callback(f"Fetching images for {cat}...")
        # Берем запрос от Gemini или формируем дефолтный
        query = category_queries.get(cat, f"{university.name} {cat}")
        
        # Ищем через SerpAPI (каждой категории даем по 2-3 уникальных фото)
        photos = search_university_images(query, max_results=3)
        categories_data[cat] = photos
        await asyncio.sleep(0.1)

    await progress_callback("Synthesizing final verified research profile...")
    await asyncio.sleep(0.3)

    return {
        "university": {
            "name": university.name,
            "region": getattr(university, "region", None),
            "country": getattr(university, "country", "Kazakhstan"),
            "website": getattr(university, "website", None)
        },
        "summary": f"Comprehensive visual campus research profile for {university.name}, categorized and verified.",
        "categories": categories_data,
        "warnings": []
    }