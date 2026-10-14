"""User model — auth, roles, OTP."""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    FARMER = "farmer"
    OFFICER = "officer"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True, index=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.FARMER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    preferred_language: Mapped[str] = mapped_column(String(5), default="en")
    otp_code: Mapped[Optional[str]] = mapped_column(String(6), nullable=True)
    otp_expiry: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    otp_attempts: Mapped[int] = mapped_column(default=0)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    consent_given_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    farmer_profile: Mapped[Optional["FarmerProfile"]] = relationship(back_populates="user", uselist=False)  # noqa: F821
    conversations: Mapped[list["Conversation"]] = relationship(back_populates="user")  # noqa: F821
    alerts: Mapped[list["Alert"]] = relationship(back_populates="user")  # noqa: F821
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user")  # noqa: F821
