"""
KisanSathi Backend — Application Entry Point
"""
from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import init_db
from app.core.security_middleware import SecurityHeadersMiddleware, RateLimitMiddleware
from app.api.v1.routers import (
    auth, farmers, farms, chat, scan, weather,
    market, alerts, officer, admin, webhook, health
)
from app.services.scheduler import start_scheduler, stop_scheduler

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    setup_logging()
    logger.info("KisanSathi API starting", env=settings.APP_ENV, mock=settings.USE_MOCK_LLM)
    if settings.USE_MOCK_LLM:
        logger.warning("[MOCK] USE_MOCK_LLM=true — all LLM calls return deterministic mock responses")
    await init_db()
    start_scheduler()
    yield
    stop_scheduler()
    logger.info("KisanSathi API shutting down")


app = FastAPI(
    title="KisanSathi API",
    description="AI Multi-Agent Smart Farming Advisor — IBM Granite powered",
    version="1.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────────
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
PREFIX = "/api/v1"
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix=f"{PREFIX}/auth", tags=["auth"])
app.include_router(farmers.router, prefix=f"{PREFIX}/farmers", tags=["farmers"])
app.include_router(farms.router, prefix=f"{PREFIX}/farms", tags=["farms"])
app.include_router(chat.router, prefix=f"{PREFIX}/chat", tags=["chat"])
app.include_router(scan.router, prefix=f"{PREFIX}/scan", tags=["scan"])
app.include_router(weather.router, prefix=f"{PREFIX}/weather", tags=["weather"])
app.include_router(market.router, prefix=f"{PREFIX}/market", tags=["market"])
app.include_router(alerts.router, prefix=f"{PREFIX}/alerts", tags=["alerts"])
app.include_router(officer.router, prefix=f"{PREFIX}/officer", tags=["officer"])
app.include_router(admin.router, prefix=f"{PREFIX}/admin", tags=["admin"])
app.include_router(webhook.router, prefix=f"{PREFIX}/webhook", tags=["webhook"])


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    import uuid
    request_id = str(uuid.uuid4())
    logger.error("Unhandled exception", exc=str(exc), path=request.url.path, request_id=request_id)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred.", "request_id": request_id}},
    )
