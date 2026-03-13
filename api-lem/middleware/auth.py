"""LEM Engine authentication"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import ORJSONResponse
import time

from api_lem.core.config import settings


PUBLIC_PATHS = ["/", "/health", "/docs", "/openapi.json", "/redoc", "/api/v1/sources"]


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = request.url.path
        if any(path == p or path.startswith(p.rstrip("/") + "/") for p in PUBLIC_PATHS if p != "/"):
            return await call_next(request)
        if path == "/":
            return await call_next(request)
        api_key = request.headers.get(settings.API_KEY_NAME)
        if not api_key:
            return ORJSONResponse(
                status_code=401,
                content={"error": "Authentication required", "timestamp": time.time()},
            )
        if settings.API_KEYS and api_key not in settings.API_KEYS:
            return ORJSONResponse(
                status_code=403,
                content={"error": "Invalid API key", "timestamp": time.time()},
            )
        return await call_next(request)
