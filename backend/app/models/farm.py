"""Farm and FarmCrop models."""
import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Float, Date, DateTime, ForeignKey, Text, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class SoilType(str, enum.Enum):
    CLAY = "clay"
    LOAM = "loam"
    SANDY = "sandy"
    SILTY = "silty"
    BLACK = "black"


class IrrigationType(str, enum.Enum):
    DRIP = "drip"
    FLOOD = "flood"
    SPRINKLER = "sprinkler"
    RAINFED = "rainfed"
    CANAL = "canal"


class CropStage(str, enum.Enum):
    LAND_PREP = "land_prep"
    SOWING = "sowing"
    GERMINATION = "germination"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    MATURITY = "maturity"
    HARVEST = "harvest"
    POST_HARVEST = "post_harvest"


class Farm(Base):
    __tablename__ = "farms"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmer_profile_id: Mapped[str] = mapped_column(String(36), ForeignKey("farmer_profiles.id"))
    name: Mapped[str] = mapped_column(String(200))
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    area_hectares: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    soil_type: Mapped[Optional[SoilType]] = mapped_column(SAEnum(SoilType), nullable=True)
    irrigation_type: Mapped[Optional[IrrigationType]] = mapped_column(SAEnum(IrrigationType), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    farmer_profile: Mapped["FarmerProfile"] = relationship(back_populates="farms")  # noqa: F821
    farm_crops: Mapped[list["FarmCrop"]] = relationship(back_populates="farm")


class Crop(Base):
    __tablename__ = "crops"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name_en: Mapped[str] = mapped_column(String(100))
    name_hi: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    name_gu: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    botanical_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    farm_crops: Mapped[list["FarmCrop"]] = relationship(back_populates="crop")


class FarmCrop(Base):
    __tablename__ = "farm_crops"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id: Mapped[str] = mapped_column(String(36), ForeignKey("farms.id"))
    crop_id: Mapped[str] = mapped_column(String(36), ForeignKey("crops.id"))
    sowing_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expected_harvest_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    current_stage: Mapped[Optional[CropStage]] = mapped_column(SAEnum(CropStage), nullable=True)
    area_hectares: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    farm: Mapped["Farm"] = relationship(back_populates="farm_crops")
    crop: Mapped["Crop"] = relationship(back_populates="farm_crops")
