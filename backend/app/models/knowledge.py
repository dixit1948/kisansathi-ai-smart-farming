"""Knowledge base and chunk models for RAG."""
import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import String, Text, DateTime, JSON, Integer, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(500))
    source_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    language: Mapped[str] = mapped_column(String(5), default="en")
    crop_tags: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)  # list of crop names
    topic_tags: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    is_sample: Mapped[bool] = mapped_column(default=True)  # flag sample/demo data
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(String(36))
    chroma_id: Mapped[str] = mapped_column(String(100), unique=True)
    content: Mapped[str] = mapped_column(Text)
    chunk_index: Mapped[int] = mapped_column(Integer)
    token_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
