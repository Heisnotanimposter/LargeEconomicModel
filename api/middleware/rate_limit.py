"""
Rate limiting middleware
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
from collections import defaultdict
from typing import Dict
import asyncio

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm
    """
    
    def __init__(self, app, requests_per_minute: int = 100, window_size: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_size = window_size
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = asyncio.Lock()
    
    async def dispatch(self, request: Request, call_next):
        # Get client identifier (IP address or API key)
        client_id = request.client.host
        api_key = request.headers.get("X-API-Key")
        if api_key:
            client_id = api_key
        
        current_time = time.time()
        
        async with self.lock:
            # Clean old requests outside the window
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if current_time - req_time < self.window_size
            ]
            
            # Check rate limit
            if len(self.requests[client_id]) >= self.requests_per_minute:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "message": f"Maximum {self.requests_per_minute} requests per {self.window_size} seconds",
                        "retry_after": self.window_size,
                        "timestamp": current_time
                    },
                    headers={
                        "Retry-After": str(self.window_size),
                        "X-RateLimit-Limit": str(self.requests_per_minute),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(current_time + self.window_size))
                    }
                )
            
            # Add current request
            self.requests[client_id].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.requests_per_minute - len(self.requests[client_id])
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_size))
        
        return response

