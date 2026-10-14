"""Farmers profile router."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.core.database import get_db
from app.api.deps import require_farmer
from app.models.user import User
from app.models.farmer import FarmerProfile

router = APIRouter()


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    village: Optional[str] = None
    taluka: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None


class OnboardingRequest(BaseModel):
    language: str
    full_name: str
    village: Optional[str] = None
    taluka: Optional[str] = None
    district: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    area_hectares: Optional[float] = None
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    crop_names: Optional[list[str]] = None


@router.get("/profile")
async def get_profile(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_farmer),
):
    res = await db.execute(select(FarmerProfile).where(FarmerProfile.user_id == user.id))
    profile = res.scalar_one_or_none()
    if not profile:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "Profile not found."})
    return {
        "id": profile.id,
        "full_name": profile.full_name,
        "village": profile.village,
        "taluka": profile.taluka,
        "district": profile.district,
        "state": profile.state,
        "onboarding_completed": profile.onboarding_completed,
    }


@router.patch("/profile")
async def update_profile(
    req: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_farmer),
):
    res = await db.execute(select(FarmerProfile).where(FarmerProfile.user_id == user.id))
    profile = res.scalar_one_or_none()
    if not profile:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "Profile not found."})
    for field, val in req.model_dump(exclude_none=True).items():
        setattr(profile, field, val)
    await db.commit()
    return {"message": "Profile updated."}


@router.post("/onboarding")
async def complete_onboarding(
    req: OnboardingRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_farmer),
):
    """Complete 4-step onboarding wizard."""
    res = await db.execute(select(FarmerProfile).where(FarmerProfile.user_id == user.id))
    profile = res.scalar_one_or_none()
    if not profile:
        profile = FarmerProfile(user_id=user.id, full_name=req.full_name)
        db.add(profile)

    profile.full_name = req.full_name
    profile.village = req.village
    profile.taluka = req.taluka
    profile.district = req.district
    profile.onboarding_completed = True
    user.preferred_language = req.language
    await db.commit()

    # Create default farm if location provided
    if req.latitude and req.longitude:
        from app.models.farm import Farm
        existing = await db.execute(select(Farm).where(Farm.farmer_profile_id == profile.id))
        if not existing.scalar_one_or_none():
            farm = Farm(
                farmer_profile_id=profile.id,
                name=f"{profile.full_name}'s Farm",
                latitude=req.latitude,
                longitude=req.longitude,
                area_hectares=req.area_hectares,
                soil_type=req.soil_type,
                irrigation_type=req.irrigation_type,
            )
            db.add(farm)
            await db.commit()

    return {"message": "Onboarding complete!", "onboarding_completed": True}
