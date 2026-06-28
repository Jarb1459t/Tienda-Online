from datetime import datetime
from sqlalchemy import (
    String, Integer, Text, DateTime, ForeignKey, Enum as SAEnum, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
import enum


class DocStatus(str, enum.Enum):
    processing = "processing"
    ready      = "ready"
    error      = "error"


class ModuleID(str, enum.Enum):
    general = "general"
    m01 = "m01"
    m02 = "m02"
    m03 = "m03"
    m04 = "m04"
    m05 = "m05"
    m06 = "m06"
    m07 = "m07"
    m08 = "m08"


# ── Documents ────────────────────────────────────────────
class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int]         = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str]       = mapped_column(String(255), nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str]  = mapped_column(String(120), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    file_path: Mapped[str]  = mapped_column(String(500), nullable=False)

    module: Mapped[str]     = mapped_column(
        SAEnum(ModuleID, values_callable=lambda x: [e.value for e in x]),
        default="general", nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None]     = mapped_column(Text, nullable=True)
    status: Mapped[str]             = mapped_column(
        SAEnum(DocStatus, values_callable=lambda x: [e.value for e in x]),
        default="processing", nullable=False
    )

    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime]  = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # relationships
    chat_messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_documents_module", "module"),
        Index("ix_documents_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<Document id={self.id} name={self.name!r} module={self.module}>"


# ── Chat messages ─────────────────────────────────────────
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int]           = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[int]  = mapped_column(ForeignKey("documents.id"), nullable=False)
    role: Mapped[str]         = mapped_column(String(20), nullable=False)  # user | assistant
    content: Mapped[str]      = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    document: Mapped["Document"] = relationship(back_populates="chat_messages")

    __table_args__ = (
        Index("ix_chat_document_id", "document_id"),
    )


# ── Activity log ──────────────────────────────────────────
class ActivityLog(Base):
    __tablename__ = "activity_log"

    id: Mapped[int]         = mapped_column(Integer, primary_key=True, index=True)
    icon: Mapped[str]       = mapped_column(String(10), nullable=False)
    text: Mapped[str]       = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_activity_created", "created_at"),
    )


# ── AI query counter ──────────────────────────────────────
class AIQueryLog(Base):
    __tablename__ = "ai_query_log"

    id: Mapped[int]          = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[int | None] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )
    query_type: Mapped[str]  = mapped_column(String(50), nullable=False)  # summary|chat|report
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
