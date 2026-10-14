"""Officer analytics router."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.api.deps import require_officer
from app.models.user import User, UserRole
from app.models.farmer import FarmerProfile
from app.models.farm import Farm
from app.models.scan import Scan, ScanSeverity
from app.models.alert import Alert

router = APIRouter()


@router.get("/farmers")
async def list_farmers_map(
    district: str = Query(None),
    crop: str = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_officer),
):
    """Map data: all farmers with location and last scan severity."""
    query = (
        select(User.id, User.phone, FarmerProfile.full_name, FarmerProfile.district,
               FarmerProfile.taluka, Farm.latitude, Farm.longitude, Farm.area_hectares)
        .join(FarmerProfile, FarmerProfile.user_id == User.id, isouter=True)
        .join(Farm, Farm.farmer_profile_id == FarmerProfile.id, isouter=True)
        .where(User.role == UserRole.FARMER, User.deleted_at.is_(None))
    )
    if district:
        query = query.where(FarmerProfile.district.ilike(f"%{district}%"))

    result = await db.execute(query)
    rows = result.all()

    return {
        "farmers": [
            {
                "id": row[0],
                "name": row[2] or "Unknown",
                "district": row[3],
                "taluka": row[4],
                "latitude": row[5],
                "longitude": row[6],
                "area_hectares": row[7],
            }
            for row in rows
        ],
        "total": len(rows),
    }


@router.get("/stats")
async def officer_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_officer),
):
    """Summary statistics for officer dashboard."""
    farmer_count = await db.execute(select(func.count()).select_from(User).where(User.role == UserRole.FARMER, User.deleted_at.is_(None)))
    scan_count = await db.execute(select(func.count()).select_from(Scan))
    critical_scans = await db.execute(select(func.count()).select_from(Scan).where(Scan.severity == ScanSeverity.CRITICAL))
    unread_alerts = await db.execute(select(func.count()).select_from(Alert).where(Alert.read_at.is_(None)))

    return {
        "total_farmers": farmer_count.scalar() or 0,
        "total_scans": scan_count.scalar() or 0,
        "critical_disease_alerts": critical_scans.scalar() or 0,
        "unread_alerts": unread_alerts.scalar() or 0,
    }


@router.get("/outbreaks")
async def outbreak_clusters(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_officer),
):
    """Recent disease scan clusters (disease + location)."""
    result = await db.execute(
        select(Scan.predicted_label, func.count(Scan.id).label("count"))
        .where(Scan.severity.in_([ScanSeverity.HIGH, ScanSeverity.CRITICAL]))
        .group_by(Scan.predicted_label)
        .order_by(func.count(Scan.id).desc())
        .limit(10)
    )
    clusters = result.all()
    return {"clusters": [{"disease": r[0], "count": r[1]} for r in clusters]}
