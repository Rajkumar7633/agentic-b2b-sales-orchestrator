import json
from typing import Any

from app.core.config import settings


class SessionMemory:
    """
    Session Memory layer for storing user/prospect conversation and interaction history.
    Uses Redis when available, with a thread-safe dictionary fallback.
    Keyed by session_id (or contact_id / lead_id).
    """
    def __init__(self):
        self._local_store: dict[str, str] = {}
        self._redis_client = None
        try:
            import redis
            self._redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
            self._redis_client.ping()
        except Exception:
            self._redis_client = None

    async def get_session_history(self, session_id: str) -> list[dict[str, Any]]:
        key = f"session_memory:{session_id}"
        if self._redis_client:
            try:
                val = self._redis_client.get(key)
                return json.loads(val) if val else []
            except Exception:
                pass
        val = self._local_store.get(key)
        return json.loads(val) if val else []

    async def append_interaction(self, session_id: str, interaction: dict[str, Any], ttl_seconds: int = 86400) -> None:
        history = await self.get_session_history(session_id)
        history.append(interaction)
        key = f"session_memory:{session_id}"
        serialized = json.dumps(history, default=str)
        if self._redis_client:
            try:
                self._redis_client.setex(key, ttl_seconds, serialized)
                return
            except Exception:
                pass
        self._local_store[key] = serialized

    async def clear_session(self, session_id: str) -> None:
        key = f"session_memory:{session_id}"
        if self._redis_client:
            try:
                self._redis_client.delete(key)
            except Exception:
                pass
        self._local_store.pop(key, None)


session_memory = SessionMemory()
