from datetime import datetime, timedelta
from typing import Any, Dict

class Cache:
    def __init__(self, default_ttl_seconds: int = 300):  # Default TTL of 5 minutes
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl_seconds = default_ttl_seconds

    def get(self, key: str) -> Any:
        if key in self._cache:
            entry = self._cache[key]
            if datetime.now() < entry["expiry"]:
                return entry["value"]
            else:
                del self._cache[key]  # Expired
        return None

    def set(self, key: str, value: Any, ttl_seconds: int = None):
        if ttl_seconds is None:
            ttl_seconds = self.default_ttl_seconds
        expiry = datetime.now() + timedelta(seconds=ttl_seconds)
        self._cache[key] = {"value": value, "expiry": expiry}

cache = Cache()
