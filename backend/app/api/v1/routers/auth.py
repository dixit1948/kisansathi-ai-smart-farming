"""Authentication router — register, login, OTP, refresh, logout."""
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, field_validator
import structlog

from app.core.config import settings
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token, generate_otp
from app.models.user import User
from app.api.deps import get_current_user

logger = structlog.get_logger(__name__)
router = APIRouter()

COOKIE_OPTS = {"httponly": True, "secure": False, "samesite": "lax"}


class RegisterRequest(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    password: str
    full_name: str
    preferred_language: str = "en"
    consent_given: bool = False

    @field_validator("password")
    @classmethod
    def strong_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    password: str


class OTPRequest(BaseModel):
    phone: str


class OTPVerifyRequest(BaseModel):
    phone: str
    otp: str


@router.post("/register", status_code=201)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if not req.phone and not req.email:
        raise HTTPException(400, detail={"code": "MISSING_IDENTIFIER", "message": "Phone or email required."})
    if not req.consent_given:
        raise HTTPException(400, detail={"code": "CONSENT_REQUIRED", "message": "Consent required for data processing."})

    # Check duplicate
    existing = None
    if req.phone:
        res = await db.execute(select(User).where(User.phone == req.phone))
        existing = res.scalar_one_or_none()
    if not existing and req.email:
        res = await db.execute(select(User).where(User.email == req.email))
        existing = res.scalar_one_or_none()
    if existing:
        raise HTTPException(409, detail={"code": "USER_EXISTS", "message": "Account already exists."})

    user = User(
        phone=req.phone,
        email=req.email,
        hashed_password=hash_password(req.password),
        preferred_language=req.preferred_language,
        consent_given_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Create farmer profile
    from app.models.farmer import FarmerProfile
    profile = FarmerProfile(user_id=user.id, full_name=req.full_name)
    db.add(profile)
    await db.commit()

    logger.info("User registered", user_id=user.id)
    return {"id": user.id, "message": "Registration successful. Please complete onboarding."}


@router.post("/login")
async def login(req: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    user = None
    if req.phone:
        res = await db.execute(select(User).where(User.phone == req.phone, User.deleted_at.is_(None)))
        user = res.scalar_one_or_none()
    if not user and req.email:
        res = await db.execute(select(User).where(User.email == req.email, User.deleted_at.is_(None)))
        user = res.scalar_one_or_none()

    if not user or not user.hashed_password or not verify_password(req.password, user.hashed_password):
        raise HTTPException(401, detail={"code": "INVALID_CREDENTIALS", "message": "Invalid phone/email or password."})

    if not user.is_active:
        raise HTTPException(403, detail={"code": "ACCOUNT_DISABLED", "message": "Account is disabled."})

    access_token = create_access_token({"sub": user.id, "role": user.role.value})
    refresh_token = create_refresh_token(user.id)

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    response.set_cookie("access_token", access_token, max_age=900, **COOKIE_OPTS)
    response.set_cookie("refresh_token", refresh_token, max_age=86400 * 30, **COOKIE_OPTS)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "role": user.role.value, "language": user.preferred_language},
    }


@router.post("/refresh")
async def refresh(response: Response, db: AsyncSession = Depends(get_db), refresh_token: Optional[str] = None):
    if not refresh_token:
        raise HTTPException(401, detail={"code": "NO_REFRESH_TOKEN", "message": "Refresh token required."})
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("Not a refresh token")
        user_id = payload["sub"]
    except Exception:
        raise HTTPException(401, detail={"code": "INVALID_REFRESH", "message": "Invalid or expired refresh token."})

    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(401, detail={"code": "USER_NOT_FOUND", "message": "User not found."})

    new_access = create_access_token({"sub": user.id, "role": user.role.value})
    new_refresh = create_refresh_token(user.id)
    response.set_cookie("access_token", new_access, max_age=900, **COOKIE_OPTS)
    response.set_cookie("refresh_token", new_refresh, max_age=86400 * 30, **COOKIE_OPTS)
    return {"access_token": new_access, "token_type": "bearer"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out."}


@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "phone": user.phone,
        "email": user.email,
        "role": user.role.value,
        "language": user.preferred_language,
        "onboarding_done": False,  # Will be populated from profile
    }


@router.post("/otp/send")
async def send_otp(req: OTPRequest, db: AsyncSession = Depends(get_db)):
    """Send OTP to phone (mock in dev — logs to console)."""
    res = await db.execute(select(User).where(User.phone == req.phone))
    user = res.scalar_one_or_none()
    if not user:
        if settings.APP_ENV in ("development", "test") or settings.DEBUG or settings.USE_MOCK_LLM:
            user = User(
                phone=req.phone,
                preferred_language="en",
                consent_given_at=datetime.now(timezone.utc),
            )
            db.add(user)
            await db.flush()
        else:
            # Don't leak existence; still return 200
            return {"message": "If this number is registered, you will receive an OTP."}

    otp, expiry = generate_otp()
    user.otp_code = otp
    user.otp_expiry = expiry
    user.otp_attempts = 0
    await db.commit()
    logger.info("OTP generated (dev: logged)", phone=req.phone, otp=otp)  # In prod: send via SMS
    return {"message": "OTP sent (dev: check server logs)."}


@router.post("/otp/verify")
async def verify_otp(req: OTPVerifyRequest, response: Response, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).where(User.phone == req.phone))
    user = res.scalar_one_or_none()
    if not user or not user.otp_code:
        raise HTTPException(400, detail={"code": "INVALID_OTP", "message": "Invalid OTP."})

    if user.otp_attempts >= 5:
        raise HTTPException(429, detail={"code": "OTP_RATE_LIMIT", "message": "Too many OTP attempts."})

    if user.otp_expiry:
        expiry = user.otp_expiry.replace(tzinfo=timezone.utc) if user.otp_expiry.tzinfo is None else user.otp_expiry
        if expiry < datetime.now(timezone.utc):
            raise HTTPException(400, detail={"code": "OTP_EXPIRED", "message": "OTP expired."})

    if user.otp_code != req.otp:
        user.otp_attempts += 1
        await db.commit()
        raise HTTPException(400, detail={"code": "INVALID_OTP", "message": "Incorrect OTP."})

    user.otp_code = None
    user.otp_expiry = None
    user.otp_attempts = 0
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    access_token = create_access_token({"sub": user.id, "role": user.role.value})
    refresh_token = create_refresh_token(user.id)
    response.set_cookie("access_token", access_token, max_age=900, **COOKIE_OPTS)
    response.set_cookie("refresh_token", refresh_token, max_age=86400 * 30, **COOKIE_OPTS)
    return {"access_token": access_token, "token_type": "bearer", "message": "OTP verified."}
