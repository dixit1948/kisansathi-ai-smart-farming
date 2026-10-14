"""Farmer context service — get farm details for agent context injection."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.farmer import FarmerProfile
from app.models.farm import Farm


async def get_farmer_context(user_id: str, db: AsyncSession) -> Optional[dict]:
    """Return farm context dict for agent injection."""
    profile_res = await db.execute(select(FarmerProfile).where(FarmerProfile.user_id == user_id))
    profile = profile_res.scalar_one_or_none()
    if not profile:
        return None

    farm_res = await db.execute(
        select(Farm).where(Farm.farmer_profile_id == profile.id).limit(1)
    )
    farm = farm_res.scalar_one_or_none()
    if not farm:
        return {"district": profile.district, "state": profile.state}

    return {
        "district": profile.district,
        "state": profile.state,
        "latitude": farm.latitude,
        "longitude": farm.longitude,
        "area": farm.area_hectares,
        "soil_type": farm.soil_type.value if farm.soil_type else None,
        "irrigation_type": farm.irrigation_type.value if farm.irrigation_type else None,
    }
