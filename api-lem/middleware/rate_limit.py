"""LEM Engine rate limiting"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import ORJSONResponse
import time
from collections import defaultdict
from typing import Dict
import asyncio

from api_lem.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = None, window_size: int = None):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute or settings.RATE_LIMIT_REQUESTS
        self.window_size = window_size or settings.RATE_LIMIT_WINDOW
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = asyncio.Lock()

    async def dispatch(self, request, call_next):
        client_id = getattr(request.client, "host", "unknown") if request.client else "unknown"
        api_key = request.headers.get("X-API-Key")
        if api_key:
            client_id = api_key
        now = time.time()
        async with self.lock:
            self.requests[client_id] = [t for t in self.requests[client_id] if now - t < self.window_size]
            if len(self.requests) > 1000:
                self.requests = {k: v for k, v in self.requests.items() if v}
            if len(self.requests[client_id]) >= self.requests_per_minute:
                return ORJSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "retry_after": self.window_size,
                        "timestamp": now,
                    },
                    headers={"Retry-After": str(self.window_size)},
                )
            self.requests[client_id].append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(self.requests_per_minute - len(self.requests[client_id]))
        return response
