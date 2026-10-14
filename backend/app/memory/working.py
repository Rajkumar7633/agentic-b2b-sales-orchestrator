import json
from typing import Any

from app.core.config import settings


class WorkingMemory:
    """
    Working Memory layer for active agent workflow state.
    Uses Redis when available, with a thread-safe dict fallback.
    """
    def __init__(self):
        self._local_store: dict[str, str] = {}
        self._redis_client = None
        # Attempt connecting to Redis if configured
        try:
            import redis
            self._redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
            self._redis_client.ping()
        except Exception:
            self._redis_client = None

    async def get_state(self, correlation_id: str) -> dict[str, Any] | None:
        key = f"working_memory:{correlation_id}"
        if self._redis_client:
            try:
                val = self._redis_client.get(key)
                return json.loads(val) if val else None
            except Exception:
                pass
        val = self._local_store.get(key)
        return json.loads(val) if val else None

    async def set_state(self, correlation_id: str, state: dict[str, Any], ttl_seconds: int = 3600) -> None:
        key = f"working_memory:{correlation_id}"
        serialized = json.dumps(state, default=str)
        if self._redis_client:
            try:
                self._redis_client.setex(key, ttl_seconds, serialized)
                return
            except Exception:
                pass
        self._local_store[key] = serialized

    async def delete_state(self, correlation_id: str) -> None:
        key = f"working_memory:{correlation_id}"
        if self._redis_client:
            try:
                self._redis_client.delete(key)
            except Exception:
                pass
        self._local_store.pop(key, None)


working_memory = WorkingMemory()
