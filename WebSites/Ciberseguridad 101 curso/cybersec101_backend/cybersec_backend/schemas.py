from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# ── Document schemas ──────────────────────────────────────

class DocumentBase(BaseModel):
    module: str = "general"
    description: str | None = None


class DocumentCreate(DocumentBase):
    pass  # file comes via UploadFile


class DocumentUpdate(BaseModel):
    module: str | None = None
    description: str | None = None


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    original_name: str
    mime_type: str
    size_bytes: int
    module: str
    description: str | None
    summary: str | None
    status: str
    uploaded_at: datetime
    updated_at: datetime

    @property
    def size_human(self) -> str:
        b = self.size_bytes
        if b < 1024:        return f"{b} B"
        if b < 1024**2:     return f"{b/1024:.1f} KB"
        return f"{b/1024**2:.2f} MB"


class DocumentList(BaseModel):
    total: int
    items: list[DocumentOut]


# ── Chat schemas ──────────────────────────────────────────

class ChatMessageIn(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int
    role: str
    content: str
    created_at: datetime


class ChatHistoryOut(BaseModel):
    document_id: int
    messages: list[ChatMessageOut]


class AIResponse(BaseModel):
    reply: str
    tokens_used: int = 0


# ── Activity schemas ──────────────────────────────────────

class ActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    icon: str
    text: str
    created_at: datetime


# ── Stats schema ──────────────────────────────────────────

class ModuleStats(BaseModel):
    module_id: str
    module_name: str
    doc_count: int


class DashboardStats(BaseModel):
    total_documents: int
    total_size_bytes: int
    total_size_human: str
    modules_covered: int
    total_ai_queries: int
    documents_by_module: list[ModuleStats]
    recent_activity: list[ActivityOut]


# ── Report schema ─────────────────────────────────────────

class ReportOut(BaseModel):
    report: str
    generated_at: datetime
