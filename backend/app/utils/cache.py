import time
from typing import Any

class TTLCache:
    def __init__(self): self.items: dict[str, tuple[float, Any]] = {}
    def get(self, key: str):
        value = self.items.get(key)
        if value and value[0] > time.time(): return value[1]
        self.items.pop(key, None); return None
    def set(self, key: str, value: Any, ttl: int): self.items[key] = (time.time() + ttl, value)

cache = TTLCache()
