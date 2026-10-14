"""Auth dependency — decode JWT and load current user."""
from typing import Optional
from fastapi import Depends, HTTPException, status, Cookie, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole
import structlog

logger = structlog.get_logger(__name__)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
    access_token: Optional[str] = Cookie(default=None),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "INVALID_TOKEN", "message": "Could not validate credentials."},
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
    elif access_token:
        token = access_token

    if not token:
        raise credentials_exception

    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise credentials_exception
        sub = payload.get("sub")
        if not sub:
            raise credentials_exception
        user_id = str(sub)
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id, User.deleted_at.is_(None)))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise credentials_exception
    return user


async def get_optional_current_user(
    db: AsyncSession = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
    access_token: Optional[str] = Cookie(default=None),
) -> Optional[User]:
    """Optional user dependency for guest-accessible routes."""
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
    elif access_token:
        token = access_token

    if not token:
        return None

    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        sub = payload.get("sub")
        if not sub:
            return None
        user_id = str(sub)
        result = await db.execute(select(User).where(User.id == user_id, User.deleted_at.is_(None)))
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            return None
        return user
    except Exception:
        return None


def require_role(*roles: UserRole):
    async def _check(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "Insufficient permissions."},
            )
        return user
    return _check


require_farmer = require_role(UserRole.FARMER, UserRole.OFFICER, UserRole.ADMIN)
require_officer = require_role(UserRole.OFFICER, UserRole.ADMIN)
require_admin = require_role(UserRole.ADMIN)
