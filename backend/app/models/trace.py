"""Agent trace and audit log models."""
import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import String, DateTime, JSON, Float, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class AgentTrace(Base):
    __tablename__ = "agent_traces"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("conversations.id"), nullable=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    supervisor_intent: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    agents_invoked: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)  # list of agent names
    agent_outputs: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)  # full outputs
    total_latency_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_tokens: Mapped[Optional[int]] = mapped_column(nullable=True)
    is_mock: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(200))
    resource_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    details: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[Optional["User"]] = relationship(back_populates="audit_logs")  # noqa: F821


class WeatherCache(Base):
    __tablename__ = "weather_cache"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cache_key: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    data: Mapped[Any] = mapped_column(JSON)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
