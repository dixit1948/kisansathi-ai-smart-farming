"""Farms CRUD router."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.core.database import get_db
from app.api.deps import require_farmer
from app.models.user import User
from app.models.farm import Farm
from app.models.farmer import FarmerProfile

router = APIRouter()


class FarmCreate(BaseModel):
    name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    area_hectares: Optional[float] = None
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    notes: Optional[str] = None


@router.get("")
async def list_farms(db: AsyncSession = Depends(get_db), user: User = Depends(require_farmer)):
    res = await db.execute(
        select(FarmerProfile).where(FarmerProfile.user_id == user.id)
    )
    profile = res.scalar_one_or_none()
    if not profile:
        return {"farms": []}
    result = await db.execute(select(Farm).where(Farm.farmer_profile_id == profile.id))
    farms = result.scalars().all()
    return {
        "farms": [
            {
                "id": f.id, "name": f.name,
                "latitude": f.latitude, "longitude": f.longitude,
                "area_hectares": f.area_hectares,
                "soil_type": f.soil_type.value if f.soil_type else None,
                "irrigation_type": f.irrigation_type.value if f.irrigation_type else None,
            }
            for f in farms
        ]
    }


@router.post("", status_code=201)
async def create_farm(
    req: FarmCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_farmer),
):
    res = await db.execute(select(FarmerProfile).where(FarmerProfile.user_id == user.id))
    profile = res.scalar_one_or_none()
    if not profile:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "Complete onboarding first."})

    farm = Farm(farmer_profile_id=profile.id, **req.model_dump())
    db.add(farm)
    await db.commit()
    await db.refresh(farm)
@router.get("/overview")
async def get_farm_overview(db: AsyncSession = Depends(get_db)):
    """Farm overview summary endpoint."""
    return {
        "farmer_name": "Arjun Bhai Patel",
        "district": "Bardoli, Surat",
        "crop_name": "Cotton (કપાસ)",
        "crop_stage": "Vegetative (Day 45)",
        "sowing_date": "15 June 2024",
        "task_of_day": {
            "title": "Apply 1st Split Urea (30 kg/acre)",
            "description": "Vegetative peak stage requires nitrogen top-dressing. Water within 24 hours of application.",
            "completed": False,
        },
        "weather": {
            "location": "Bardoli, Surat (Gujarat)",
            "max_temp": 36,
            "min_temp": 25,
            "humidity": 68,
            "wind_kmh": 11,
            "rainfall_mm": 0,
            "irrigation_needed_mm": 40,
            "et0_deficit_mm": 38,
            "spray_window": "Safe spray window: Today 4:00 PM – 7:00 PM (Wind < 12 km/h)",
            "is_spray_safe": True,
            "forecast_7d": [
                {"date": "Today", "day": "Mon", "max_temp": 36, "min_temp": 25, "rain_mm": 0, "wind_kmh": 11},
                {"date": "Tue", "day": "Tue", "max_temp": 37, "min_temp": 26, "rain_mm": 0, "wind_kmh": 14},
                {"date": "Wed", "day": "Wed", "max_temp": 35, "min_temp": 24, "rain_mm": 8, "wind_kmh": 18},
                {"date": "Thu", "day": "Thu", "max_temp": 34, "min_temp": 24, "rain_mm": 12, "wind_kmh": 10},
                {"date": "Fri", "day": "Fri", "max_temp": 35, "min_temp": 25, "rain_mm": 2, "wind_kmh": 9},
                {"date": "Sat", "day": "Sat", "max_temp": 38, "min_temp": 26, "rain_mm": 0, "wind_kmh": 12},
                {"date": "Sun", "day": "Sun", "max_temp": 38, "min_temp": 27, "rain_mm": 0, "wind_kmh": 13},
            ],
        },
        "active_alerts_count": 2,
    }


@router.get("/{farm_id}")
async def get_farm(farm_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(require_farmer)):
    res = await db.execute(
        select(Farm).join(FarmerProfile).where(Farm.id == farm_id, FarmerProfile.user_id == user.id)
    )
    farm = res.scalar_one_or_none()
    if not farm:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "Farm not found."})
    return {
        "id": farm.id, "name": farm.name,
        "latitude": farm.latitude, "longitude": farm.longitude,
        "area_hectares": farm.area_hectares,
        "soil_type": farm.soil_type.value if farm.soil_type else None,
        "irrigation_type": farm.irrigation_type.value if farm.irrigation_type else None,
        "notes": farm.notes,
    }
