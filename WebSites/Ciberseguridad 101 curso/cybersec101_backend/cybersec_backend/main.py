"""
CiberSec 101 — Document Management Backend
FastAPI + SQLAlchemy + Anthropic AI
"""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

import models
from config import get_settings
from database import engine
from routers import chat, dashboard, documents

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)
settings = get_settings()


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables if they don't exist
    models.Base.metadata.create_all(bind=engine)
    os.makedirs(settings.storage_path, exist_ok=True)
    logger.info("✔  Database ready: %s", settings.database_url)
    logger.info("✔  Storage ready:  %s", settings.storage_path)
    logger.info("🚀 CiberSec 101 backend started — http://localhost:8000")
    yield
    logger.info("Backend shutdown.")


# ── App ────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="CiberSec 101 — Document Backend",
    description=(
        "Backend de gestión de documentos para el curso de ciberseguridad. "
        "Incluye CRUD de archivos, análisis IA y chat contextual."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ───────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins + ["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(dashboard.router)


# ── Health & Info ──────────────────────────────────────────────────────────
@app.get("/", tags=["meta"])
def root():
    return {
        "app":     settings.app_name,
        "version": settings.app_version,
        "docs":    "/docs",
        "status":  "online",
    }


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}


# ── Global error handler ───────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor", "error": str(exc)},
    )


# ── Dev server entry ───────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_excludes=["storage/*", "*.db"],
    )
