"""Weather router."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_optional_current_user
from app.models.user import User
from app.agents.weather_irrigation import run_weather_irrigation_agent

router = APIRouter()


@router.get("/forecast")
async def get_weather_forecast(
    lat: float = Query(21.17, description="Latitude"),
    lon: float = Query(72.83, description="Longitude"),
    soil_type: str = Query("loam"),
    irrigation_type: str = Query("drip"),
    crop: Optional[str] = Query(None),
    language: str = Query("en"),
    user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await run_weather_irrigation_agent(
        lat=lat, lon=lon, soil_type=soil_type,
        irrigation_type=irrigation_type, crop=crop, language=language,
    )
    return {
        "answer": result.answer,
        "confidence": result.confidence,
        "forecast": result.extra.get("raw_forecast", []) if result.extra else [],
        "sources": [s.model_dump() for s in result.sources],
        "is_mock": result.is_mock,
        "latency_ms": round(result.latency_ms),
    }
