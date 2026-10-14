"""Alerts router."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.core.database import get_db
from app.api.deps import require_farmer
from app.models.user import User
from app.models.alert import Alert

router = APIRouter()


@router.get("")
async def list_alerts(
    unread_only: bool = Query(False),
    limit: int = Query(20),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_farmer),
):
    query = select(Alert).where(Alert.user_id == user.id)
    if unread_only:
        query = query.where(Alert.read_at.is_(None))
    query = query.order_by(Alert.created_at.desc()).limit(limit)
    result = await db.execute(query)
    alerts = result.scalars().all()
    return [
        {
            "id": a.id,
            "type": a.alert_type.value,
            "severity": a.severity.value,
            "title": a.title,
            "body": a.body,
            "read": a.read_at is not None,
            "created_at": a.created_at.isoformat(),
        }
        for a in alerts
    ]


@router.post("/{alert_id}/read")
async def mark_read(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_farmer),
):
    res = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = res.scalar_one_or_none()
    if not alert or alert.user_id != user.id:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "Alert not found."})
    alert.read_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": "Marked as read."}


@router.post("/read-all")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_farmer),
):
    await db.execute(
        update(Alert).where(Alert.user_id == user.id, Alert.read_at.is_(None))
        .values(read_at=datetime.now(timezone.utc))
    )
    await db.commit()
    return {"message": "All alerts marked as read."}


@router.get("/unread-count")
async def unread_count(db: AsyncSession = Depends(get_db), user: User = Depends(require_farmer)):
    from sqlalchemy import func
    result = await db.execute(
        select(func.count()).where(Alert.user_id == user.id, Alert.read_at.is_(None))
    )
    count = result.scalar() or 0
    return {"count": count}
