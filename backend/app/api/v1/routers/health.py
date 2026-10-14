"""Health check endpoints."""
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/healthz", tags=["health"])
async def liveness():
    return {"status": "ok", "service": "kisansathi-api"}


@router.get("/readyz", tags=["health"])
async def readiness(response: Response, db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    if not db_ok:
        response.status_code = 503
    return {
        "status": "ready" if db_ok else "degraded",
        "database": "ok" if db_ok else "error",
        "mock_mode": settings.USE_MOCK_LLM,
    }
