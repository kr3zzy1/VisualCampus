from serpapi import GoogleSearch
from app.config import settings

def search_university_images(query: str, max_results: int = 6) -> list[dict]:
    """
    Ищет фотографии через SerpAPI (Google Images) с использованием ключа из settings.
    """
    image_urls = []
    
    if settings.serpapi_key:
        try:
            params = {
                "engine": "google_images",
                "q": query,
                "api_key": settings.serpapi_key,
                "hl": "en",
                "gl": "us"
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            images_results = results.get("images_results", [])
            for img in images_results[:max_results]:
                if "original" in img:
                    image_urls.append(img["original"])
                    
        except Exception as e:
            print(f"Ошибка при запросе через SerpAPI: {e}")
            
    # Резервные картинки, если ключ не указан или поиск пуст
    fallback_photos = [
        "https://images.unsplash.com/photo-1523050854058-8df90110c9f1",
        "https://images.unsplash.com/photo-1541339907198-e08756dedf3f",
        "https://images.unsplash.com/photo-1562774053-701939374585",
        "https://images.unsplash.com/photo-1498243691581-b145c3f54a5a",
        "https://images.unsplash.com/photo-1590012314607-c99d9837f15ef"
    ]

    urls = image_urls if image_urls else fallback_photos

    # Форматируем в объекты, которые ожидает фронтенд
    formatted_photos = [
        {"id": f"img_{i}", "url": url, "source": "SerpAPI / Google Images"}
        for i, url in enumerate(urls)
    ]
    
    return formatted_photos