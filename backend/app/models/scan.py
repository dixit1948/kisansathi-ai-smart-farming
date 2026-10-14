"""Scan (disease/pest detection) model."""
import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import String, Float, DateTime, ForeignKey, JSON, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class ScanSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    farm_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("farms.id"), nullable=True)
    image_path: Mapped[str] = mapped_column(String(500))  # relative path, outside web root
    original_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    predicted_label: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    severity: Mapped[Optional[ScanSeverity]] = mapped_column(SAEnum(ScanSeverity), nullable=True)
    treatment_steps: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    prevention_tips: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    sources: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    model_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_mock: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship()  # noqa: F821
