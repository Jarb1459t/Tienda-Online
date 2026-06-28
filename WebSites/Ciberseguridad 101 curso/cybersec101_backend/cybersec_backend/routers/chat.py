"""
Router: /api/documents/{doc_id}/chat
Multi-turn AI conversation about a specific document.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import ActivityLog, AIQueryLog, ChatMessage, Document
from schemas import AIResponse, ChatHistoryOut, ChatMessageIn, ChatMessageOut
from services import ai_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])


def _get_doc_or_404(doc_id: int, db: Session) -> Document:
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Documento {doc_id} no encontrado")
    return doc


@router.get("/api/documents/{doc_id}/chat", response_model=ChatHistoryOut)
def get_chat_history(doc_id: int, db: Session = Depends(get_db)):
    """Retrieve full chat history for a document."""
    _get_doc_or_404(doc_id, db)
    msgs = (
        db.query(ChatMessage)
        .filter(ChatMessage.document_id == doc_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return ChatHistoryOut(document_id=doc_id, messages=msgs)


@router.post("/api/documents/{doc_id}/chat", response_model=AIResponse)
def send_chat_message(
    doc_id: int,
    body: ChatMessageIn,
    db: Session = Depends(get_db),
):
    """Send a message and get an AI reply about the document."""
    doc = _get_doc_or_404(doc_id, db)

    # Persist user message
    user_msg = ChatMessage(document_id=doc_id, role="user", content=body.content)
    db.add(user_msg)
    db.commit()

    # Build history for context
    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.document_id == doc_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    history_dicts = [{"role": m.role, "content": m.content} for m in history]

    # Call AI (sync — FastAPI runs in threadpool for sync routes)
    try:
        reply_text, tokens = ai_service.chat_with_document(
            file_path=doc.file_path,
            mime_type=doc.mime_type,
            doc_name=doc.name,
            module=doc.module,
            history=history_dicts[:-1],  # history before current message
            user_message=body.content,
        )
    except Exception as exc:
        logger.error("Chat AI error for doc %d: %s", doc_id, exc)
        raise HTTPException(status_code=502, detail=f"Error de IA: {exc}")

    # Persist assistant reply
    ai_msg = ChatMessage(document_id=doc_id, role="assistant", content=reply_text)
    db.add(ai_msg)
    db.add(AIQueryLog(document_id=doc_id, query_type="chat", tokens_used=tokens))
    db.add(ActivityLog(icon="💬", text=f"Chat IA sobre: {doc.name}"))
    db.commit()

    return AIResponse(reply=reply_text, tokens_used=tokens)


@router.delete(
    "/api/documents/{doc_id}/chat",
    status_code=status.HTTP_204_NO_CONTENT,
)
def clear_chat_history(doc_id: int, db: Session = Depends(get_db)):
    """Delete all chat messages for a document."""
    _get_doc_or_404(doc_id, db)
    db.query(ChatMessage).filter(ChatMessage.document_id == doc_id).delete()
    db.commit()
