"""
Authentication middleware
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
from api.core.config import settings

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Simple API key authentication middleware
    """
    
    # Public endpoints that don't require authentication
    PUBLIC_ENDPOINTS = [
        "/",
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/api/v1/sources"
    ]
    
    async def dispatch(self, request: Request, call_next):
        # Check if endpoint is public
        path = request.url.path
        if any(path.startswith(endpoint) for endpoint in self.PUBLIC_ENDPOINTS):
            return await call_next(request)
        
        # Get API key from header
        api_key = request.headers.get(settings.API_KEY_NAME)
        
        # Validate API key
        if not api_key:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Authentication required",
                    "message": f"Missing {settings.API_KEY_NAME} header",
                    "timestamp": time.time()
                }
            )
        
        if settings.API_KEYS and api_key not in settings.API_KEYS:
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Invalid API key",
                    "message": "The provided API key is not valid",
                    "timestamp": time.time()
                }
            )
        
        # Continue with request
        response = await call_next(request)
        return response

