"""
Router: /api/documents
CRUD + file upload + AI summary trigger
"""
import asyncio
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from config import get_settings
from database import get_db
from models import ActivityLog, AIQueryLog, Document, DocStatus
from schemas import DocumentList, DocumentOut, DocumentUpdate
from services import ai_service, storage_service

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/api/documents", tags=["documents"])


# ── Helpers ────────────────────────────────────────────────────────────────

def _log_activity(db: Session, icon: str, text: str) -> None:
    db.add(ActivityLog(icon=icon, text=text))
    db.commit()


def _log_ai(db: Session, doc_id: int | None, query_type: str, tokens: int) -> None:
    db.add(AIQueryLog(document_id=doc_id, query_type=query_type, tokens_used=tokens))
    db.commit()


def _get_doc_or_404(doc_id: int, db: Session) -> Document:
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Documento {doc_id} no encontrado")
    return doc


# ── Endpoints ──────────────────────────────────────────────────────────────

@router.get("", response_model=DocumentList)
def list_documents(
    module: str | None = Query(None, description="Filtrar por módulo"),
    status_filter: str | None = Query(None, alias="status"),
    search: str | None = Query(None, description="Buscar en nombre/descripción"),
    skip: int = 0,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    """List all documents with optional filters."""
    q = db.query(Document)
    if module:
        q = q.filter(Document.module == module)
    if status_filter:
        q = q.filter(Document.status == status_filter)
    if search:
        term = f"%{search}%"
        q = q.filter(
            Document.name.ilike(term) | Document.description.ilike(term)
        )
    total = q.count()
    items = q.order_by(Document.uploaded_at.desc()).offset(skip).limit(limit).all()
    return DocumentList(total=total, items=items)


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    module: str = Form("general"),
    description: str | None = Form(None),
    db: Session = Depends(get_db),
):
    """Upload a document, persist it, and trigger AI summarization."""
    # Validate mime type
    mime = file.content_type or "application/octet-stream"
    if not storage_service.is_allowed(mime):
        raise HTTPException(
            status_code=415,
            detail=f"Tipo de archivo no permitido: {mime}",
        )

    # Read & size check
    content = await file.read()
    if len(content) > settings.max_file_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Archivo demasiado grande (máx {settings.max_file_size_mb} MB)",
        )

    # Persist file
    file_path = await storage_service.save_file(content, mime, file.filename or "upload")

    # Create DB record
    doc = Document(
        name=file.filename or "sin_nombre",
        original_name=file.filename or "sin_nombre",
        mime_type=mime,
        size_bytes=len(content),
        file_path=file_path,
        module=module,
        description=description,
        status=DocStatus.processing,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    _log_activity(db, "📥", f"Subido: {doc.name} → {module.upper()}")
    logger.info("Document uploaded: id=%d name=%s", doc.id, doc.name)

    # Trigger AI summary in background (non-blocking)
    asyncio.create_task(_background_summarize(doc.id, file_path, mime, doc.name, module))

    return doc


async def _background_summarize(
    doc_id: int, file_path: str, mime: str, name: str, module: str
) -> None:
    """Run AI summarization without blocking the upload response."""
    from database import SessionLocal

    db = SessionLocal()
    try:
        doc = db.get(Document, doc_id)
        if not doc:
            return
        summary, tokens = ai_service.summarize_document(file_path, mime, name, module)
        doc.summary = summary
        doc.status = DocStatus.ready
        db.commit()
        _log_activity(db, "🤖", f"IA analizó: {name}")
        _log_ai(db, doc_id, "summary", tokens)
        logger.info("Summary done for doc %d (%d tokens)", doc_id, tokens)
    except Exception as exc:
        logger.error("Summary failed for doc %d: %s", doc_id, exc)
        if doc := db.get(Document, doc_id):
            doc.status = DocStatus.error
            db.commit()
    finally:
        db.close()


@router.get("/{doc_id}", response_model=DocumentOut)
def get_document(doc_id: int, db: Session = Depends(get_db)):
    """Get a single document by ID."""
    return _get_doc_or_404(doc_id, db)


@router.patch("/{doc_id}", response_model=DocumentOut)
def update_document(
    doc_id: int,
    payload: DocumentUpdate,
    db: Session = Depends(get_db),
):
    """Update module or description of a document."""
    doc = _get_doc_or_404(doc_id, db)
    if payload.module is not None:
        doc.module = payload.module
    if payload.description is not None:
        doc.description = payload.description
    db.commit()
    db.refresh(doc)
    _log_activity(db, "✏️", f"Actualizado: {doc.name}")
    return doc


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    """Delete a document and its physical file."""
    doc = _get_doc_or_404(doc_id, db)
    name = doc.name
    storage_service.delete_file(doc.file_path)
    db.delete(doc)
    db.commit()
    _log_activity(db, "🗑", f"Eliminado: {name}")


@router.get("/{doc_id}/download")
def download_document(doc_id: int, db: Session = Depends(get_db)):
    """Download the original file."""
    doc = _get_doc_or_404(doc_id, db)
    import os
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="Archivo físico no encontrado")
    return FileResponse(
        path=doc.file_path,
        media_type=doc.mime_type,
        filename=doc.original_name,
    )


@router.post("/{doc_id}/regenerate-summary", response_model=DocumentOut)
async def regenerate_summary(doc_id: int, db: Session = Depends(get_db)):
    """Force a new AI summary for a document."""
    doc = _get_doc_or_404(doc_id, db)
    doc.status = DocStatus.processing
    db.commit()
    asyncio.create_task(
        _background_summarize(doc.id, doc.file_path, doc.mime_type, doc.name, doc.module)
    )
    db.refresh(doc)
    return doc
