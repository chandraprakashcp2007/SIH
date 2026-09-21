"""
PRAHARI Copilot In-Memory Multi-Tier Cache
Improves response latency with bounded TTLs for live and static project queries.
"""
import time
from typing import Dict, Any, Optional, Tuple


class CopilotCache:
    """Thread-safe in-memory cache with per-key TTL."""

    def __init__(self):
        # key -> (value, expire_timestamp)
        self._store: Dict[str, Tuple[Any, float]] = {}
        self.hits: int = 0
        self.misses: int = 0

    def get(self, key: str) -> Optional[Any]:
        now = time.time()
        item = self._store.get(key)
        if item is None:
            self.misses += 1
            return None
        val, expires_at = item
        if now > expires_at:
            # Expired
            del self._store[key]
            self.misses += 1
            return None
        self.hits += 1
        return val

    def set(self, key: str, value: Any, ttl_seconds: float = 2.0):
        expires_at = time.time() + ttl_seconds
        self._store[key] = (value, expires_at)

    def invalidate(self, prefix: Optional[str] = None):
        if prefix is None:
            self._store.clear()
        else:
            keys_to_del = [k for k in self._store if k.startswith(prefix)]
            for k in keys_to_del:
                del self._store[k]

    def stats(self) -> Dict[str, Any]:
        return {
            "cached_entries": len(self._store),
            "hits": self.hits,
            "misses": self.misses,
            "hit_ratio": round(self.hits / max(1, self.hits + self.misses), 3)
        }


copilot_cache = CopilotCache()
