"""Farmer profile and farm models."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.farm import Farm


class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True)
    full_name: Mapped[str] = mapped_column(String(200))
    village: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    taluka: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    district: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    state: Mapped[str] = mapped_column(String(100), default="Gujarat")
    onboarding_completed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="farmer_profile")
    farms: Mapped[list["Farm"]] = relationship(back_populates="farmer_profile")
