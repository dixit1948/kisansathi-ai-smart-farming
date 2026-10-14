"""Market prices router."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.database import get_db
from app.api.deps import get_optional_current_user, require_farmer
from app.models.user import User
from app.models.market import MarketPrice
from app.agents.market_insights import run_market_insights_agent

router = APIRouter()


@router.get("/prices")
async def get_market_prices(
    crop: str = Query("cotton"),
    district: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=30),
    language: str = Query("en"),
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_current_user),
):
    """Get price history + AI sell advice."""
    # Fetch from DB
    query = select(MarketPrice).where(MarketPrice.crop_name.ilike(f"%{crop}%"))
    if district:
        query = query.where(MarketPrice.district.ilike(f"%{district}%"))
    query = query.order_by(desc(MarketPrice.price_date)).limit(days * 3)
    result = await db.execute(query)
    prices = result.scalars().all()

    # Run market agent for AI advice
    agent_result = await run_market_insights_agent(crop=crop, district=district or "Gujarat", language=language)

    return {
        "crop": crop,
        "prices": [
            {
                "date": p.price_date.isoformat(),
                "mandi": p.mandi_name,
                "district": p.district,
                "min": p.min_price_inr,
                "modal": p.modal_price_inr,
                "max": p.max_price_inr,
                "unit": p.unit,
                "source": p.source,
            }
            for p in prices
        ],
        "ai_advice": agent_result.answer,
        "trend": agent_result.extra.get("trend") if agent_result.extra else None,
        "is_mock": agent_result.is_mock,
        "sources": [s.model_dump() for s in agent_result.sources],
    }


@router.get("/crops")
async def list_available_crops(db: AsyncSession = Depends(get_db), user: User = Depends(require_farmer)):
    """List crops available in market price DB."""
    from sqlalchemy import distinct
    result = await db.execute(select(distinct(MarketPrice.crop_name)).order_by(MarketPrice.crop_name))
    crops = [row[0] for row in result.all()]
    return {"crops": crops}
