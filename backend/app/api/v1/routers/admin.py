"""Admin router."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.api.deps import require_admin
from app.models.user import User

router = APIRouter()


@router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
    limit: int = 50,
    offset: int = 0,
):
    result = await db.execute(
        select(User).where(User.deleted_at.is_(None))
        .order_by(User.created_at.desc()).limit(limit).offset(offset)
    )
    users = result.scalars().all()
    return [
        {
            "id": u.id, "phone": u.phone, "email": u.email,
            "role": u.role.value, "is_active": u.is_active,
            "created_at": u.created_at.isoformat(),
        }
        for u in users
    ]


@router.get("/stats")
async def admin_stats(db: AsyncSession = Depends(get_db), user: User = Depends(require_admin)):
    from app.models.scan import Scan
    from app.models.conversation import Conversation
    users = await db.execute(select(func.count()).select_from(User).where(User.deleted_at.is_(None)))
    scans = await db.execute(select(func.count()).select_from(Scan))
    convs = await db.execute(select(func.count()).select_from(Conversation))
    return {
        "total_users": users.scalar() or 0,
        "total_scans": scans.scalar() or 0,
        "total_conversations": convs.scalar() or 0,
    }
