"""Market prices model."""
import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Float, Date, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class MarketPrice(Base):
    __tablename__ = "market_prices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    mandi_name: Mapped[str] = mapped_column(String(200))
    district: Mapped[str] = mapped_column(String(200))
    state: Mapped[str] = mapped_column(String(100), default="Gujarat")
    crop_name: Mapped[str] = mapped_column(String(100))
    price_date: Mapped[date] = mapped_column(Date)
    min_price_inr: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_price_inr: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    modal_price_inr: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    unit: Mapped[str] = mapped_column(String(20), default="quintal")
    source: Mapped[str] = mapped_column(String(100), default="sample_csv")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_market_prices_crop_date", "crop_name", "price_date"),
        Index("ix_market_prices_mandi", "mandi_name"),
    )
