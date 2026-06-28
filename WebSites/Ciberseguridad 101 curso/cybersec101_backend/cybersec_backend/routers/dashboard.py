"""
Router: /api/dashboard  |  /api/activity  |  /api/report
Stats, activity log and AI repository report.
"""
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import ActivityLog, AIQueryLog, Document
from schemas import ActivityOut, DashboardStats, ModuleStats, ReportOut
from services import ai_service, storage_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["dashboard"])

MODULE_NAMES: dict[str, str] = {
    "general": "Sin módulo específico",
    "m01": "Introducción a la Ciberseguridad",
    "m02": "Redes e Internet",
    "m03": "Amenazas y Tipos de Ataques",
    "m04": "Gestión de Identidad y Contraseñas",
    "m05": "Seguridad en Dispositivos y Sistemas",
    "m06": "Privacidad y Navegación Segura",
    "m07": "Respuesta a Incidentes",
    "m08": "Marco Legal y Rutas Profesionales",
}


def _fmt_size(b: int) -> str:
    if b < 1024:        return f"{b} B"
    if b < 1024 ** 2:   return f"{b/1024:.1f} KB"
    return f"{b/1024**2:.2f} MB"


@router.get("/api/dashboard", response_model=DashboardStats)
def get_dashboard(db: Session = Depends(get_db)):
    """Return aggregated statistics for the dashboard panel."""
    total_docs = db.query(func.count(Document.id)).scalar() or 0
    total_size = db.query(func.sum(Document.size_bytes)).scalar() or 0
    total_ai   = db.query(func.count(AIQueryLog.id)).scalar() or 0

    # Modules that have at least one document (excluding 'general')
    covered = (
        db.query(func.count(func.distinct(Document.module)))
        .filter(Document.module != "general")
        .scalar()
        or 0
    )

    # Docs per module
    rows = (
        db.query(Document.module, func.count(Document.id))
        .group_by(Document.module)
        .all()
    )
    by_module = [
        ModuleStats(
            module_id=mod,
            module_name=MODULE_NAMES.get(mod, mod),
            doc_count=cnt,
        )
        for mod, cnt in rows
    ]

    # Recent activity (last 10)
    activity = (
        db.query(ActivityLog)
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
        .all()
    )

    return DashboardStats(
        total_documents=total_docs,
        total_size_bytes=total_size,
        total_size_human=_fmt_size(total_size),
        modules_covered=covered,
        total_ai_queries=total_ai,
        documents_by_module=by_module,
        recent_activity=activity,
    )


@router.get("/api/activity", response_model=list[ActivityOut])
def get_activity(limit: int = 20, db: Session = Depends(get_db)):
    """Return the latest N activity log entries."""
    return (
        db.query(ActivityLog)
        .order_by(ActivityLog.created_at.desc())
        .limit(limit)
        .all()
    )


@router.post("/api/report", response_model=ReportOut)
def generate_report(db: Session = Depends(get_db)):
    """Generate an AI-powered coverage report for the document repository."""
    docs = db.query(Document).all()
    summaries = [
        {
            "name": d.name,
            "module": d.module,
            "size_human": _fmt_size(d.size_bytes),
            "summary": d.summary,
        }
        for d in docs
    ]

    try:
        report_text, tokens = ai_service.generate_repo_report(summaries)
    except Exception as exc:
        logger.error("Report generation failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Error de IA: {exc}")

    db.add(AIQueryLog(query_type="report", tokens_used=tokens))
    db.add(ActivityLog(icon="📊", text="Reporte IA del repositorio generado"))
    db.commit()

    return ReportOut(report=report_text, generated_at=datetime.utcnow())
