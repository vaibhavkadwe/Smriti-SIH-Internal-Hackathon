"""IP rate limiting — 100 req/min default (Phase 12).

Uses Redis when reachable so limits are shared across workers; falls back to an
in-process sliding window if Redis is down so a cache outage never takes the
API offline. Disabled outside production unless RATE_LIMIT_ENABLED=true.
"""
from __future__ import annotations

import logging
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import settings

logger = logging.getLogger(__name__)

_SKIP_PATHS = {"/health", "/docs", "/redoc", "/openapi.json", "/api/v1/language/status"}


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, per_minute: Optional[int] = None):
        super().__init__(app)
        self.per_minute = per_minute or settings.RATE_LIMIT_PER_MINUTE
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)
        self._redis = None
        self._redis_failed = False

    async def dispatch(self, request: Request, call_next) -> Response:
        if not settings.rate_limit_enabled:
            return await call_next(request)
        path = request.url.path
        if path in _SKIP_PATHS or path.endswith("/openapi.json"):
            return await call_next(request)

        ip = request.client.host if request.client else "unknown"
        allowed = await self._allow(ip)
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": f"Rate limit exceeded ({self.per_minute} requests/minute)"},
                headers={"Retry-After": "60"},
            )
        return await call_next(request)

    async def _allow(self, ip: str) -> bool:
        if not self._redis_failed:
            try:
                return await self._allow_redis(ip)
            except Exception:  # noqa: BLE001 — degrade to memory
                self._redis_failed = True
                logger.warning("Redis rate-limit unavailable; using in-process limiter")
        return self._allow_memory(ip)

    async def _allow_redis(self, ip: str) -> bool:
        if self._redis is None:
            import redis.asyncio as redis

            self._redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
        key = f"rl:{ip}"
        n = await self._redis.incr(key)
        if n == 1:
            await self._redis.expire(key, 60)
        return int(n) <= self.per_minute

    def _allow_memory(self, ip: str) -> bool:
        now = time.monotonic()
        window_start = now - 60
        bucket = self._hits[ip]
        while bucket and bucket[0] < window_start:
            bucket.popleft()
        if len(bucket) >= self.per_minute:
            return False
        bucket.append(now)
        return True
