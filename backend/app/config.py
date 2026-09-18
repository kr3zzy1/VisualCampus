from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT/'.env', extra='ignore')
    request_timeout_seconds: float = 10
    allowed_origins: str = 'http://localhost:5174'
    gemini_api_key: str | None = None
    gemini_model: str = 'gemini-2.0-flash'
    serpapi_key: str | None = None  # Добавили поле для ключа SerpAPI
    university_data_path: Path = ROOT / 'backend' / 'data' / 'universities.json'

settings = Settings()