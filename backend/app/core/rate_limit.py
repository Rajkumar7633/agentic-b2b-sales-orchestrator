import time
from collections import defaultdict

from fastapi import Request, status
from fastapi.responses import JSONResponse


class RateLimiter:
    """
    Sliding-window rate limiter enforcing request limits per client IP.
    Default limit: 60 requests per 60-second window.
    """
    def __init__(self, requests_per_minute: int = 120):
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
        self._history: dict[str, list[float]] = defaultdict(list)

    def is_rate_limited(self, client_ip: str) -> bool:
        now = time.time()
        cutoff = now - self.window_seconds
        # Clean up old timestamps
        timestamps = [t for t in self._history[client_ip] if t > cutoff]
        self._history[client_ip] = timestamps

        if len(timestamps) >= self.requests_per_minute:
            return True

        self._history[client_ip].append(now)
        return False


rate_limiter = RateLimiter(requests_per_minute=120)


async def rate_limit_middleware(request: Request, call_next):
    # Exempt health checks and OpenAPI docs
    if request.url.path in ["/health", "/docs", "/openapi.json", "/redoc", "/"]:
        return await call_next(request)

    client_ip = request.client.host if request.client else "127.0.0.1"
    if rate_limiter.is_rate_limited(client_ip):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded. Maximum 120 requests per minute allowed."}
        )

    return await call_next(request)
