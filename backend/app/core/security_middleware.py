"""
Security middleware: headers, rate limiting, request ID injection.
"""
import time
import uuid
from collections import defaultdict
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = structlog.get_logger(__name__)

# In-memory rate limit store (replaced by Redis in production)
_rate_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW_SECONDS = 60


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(self), camera=(self), microphone=(self)"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        # CSP: allow self + watsonx CDN
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; "
            "connect-src 'self' https://api.open-meteo.com; "
            "font-src 'self' data:; "
            "frame-ancestors 'none';"
        )
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Clean old entries
        _rate_store[client_ip] = [t for t in _rate_store[client_ip] if now - t < RATE_LIMIT_WINDOW_SECONDS]

        if len(_rate_store[client_ip]) >= RATE_LIMIT_REQUESTS:
            logger.warning("Rate limit exceeded", ip=client_ip)
            return JSONResponse(
                status_code=429,
                content={"error": {"code": "RATE_LIMIT_EXCEEDED", "message": "Too many requests. Please slow down."}},
                headers={"Retry-After": "60"},
            )

        _rate_store[client_ip].append(now)
        return await call_next(request)
