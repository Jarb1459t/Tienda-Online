"""
AI Service — wraps Anthropic API for:
  - Document summarization
  - Contextual chat over documents
  - Repository coverage reports
"""
import base64
import logging
from pathlib import Path

import anthropic

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 1024

SYSTEM_TUTOR = (
    "Eres un tutor experto en ciberseguridad que asiste a estudiantes del curso "
    "'CiberSec 101 — Fundamentos de Ciberseguridad'. "
    "Responde siempre en español, de forma clara, pedagógica y concisa. "
    "Cuando analices documentos, enfócate en cómo el contenido aplica a los "
    "conceptos del módulo correspondiente."
)

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


def _get_client() -> anthropic.Anthropic:
    if not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY no configurada en .env")
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def _build_doc_block(file_path: str, mime_type: str) -> dict | None:
    """Build a document/image content block for the Anthropic API."""
    path = Path(file_path)
    if not path.exists():
        return None

    if mime_type == "application/pdf":
        data = base64.standard_b64encode(path.read_bytes()).decode()
        return {
            "type": "document",
            "source": {"type": "base64", "media_type": "application/pdf", "data": data},
        }

    if mime_type.startswith("image/"):
        data = base64.standard_b64encode(path.read_bytes()).decode()
        return {
            "type": "image",
            "source": {"type": "base64", "media_type": mime_type, "data": data},
        }

    # Plain text / markdown / csv — read and embed as text
    if mime_type in ("text/plain", "text/markdown", "text/csv"):
        text = path.read_text(errors="replace")[:8000]  # cap at 8 000 chars
        return {"type": "text", "text": f"[Contenido del archivo]\n{text}"}

    return None


# ── Public API ────────────────────────────────────────────────────────────────

def summarize_document(
    file_path: str,
    mime_type: str,
    doc_name: str,
    module: str,
) -> tuple[str, int]:
    """
    Generate a 3-sentence executive summary for the document.
    Returns (summary_text, tokens_used).
    """
    client = _get_client()
    mod_name = MODULE_NAMES.get(module, module)

    doc_block = _build_doc_block(file_path, mime_type)
    if doc_block is None:
        return (
            f"Resumen no disponible para el tipo de archivo '{mime_type}'.",
            0,
        )

    user_content = [
        doc_block,
        {
            "type": "text",
            "text": (
                f"Analiza el documento '{doc_name}' correspondiente al módulo "
                f"'{mod_name}' del curso CiberSec 101. "
                "Genera un resumen ejecutivo en español de exactamente 3 oraciones: "
                "qué contiene, su relevancia para el módulo y un punto clave."
            ),
        },
    ]

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_TUTOR,
        messages=[{"role": "user", "content": user_content}],
    )

    text = response.content[0].text if response.content else "—"
    tokens = response.usage.input_tokens + response.usage.output_tokens
    logger.info("Summary generated for '%s' (%d tokens)", doc_name, tokens)
    return text, tokens


def chat_with_document(
    file_path: str,
    mime_type: str,
    doc_name: str,
    module: str,
    history: list[dict],   # [{"role": "user"|"assistant", "content": str}]
    user_message: str,
) -> tuple[str, int]:
    """
    Continue a multi-turn conversation about a document.
    Returns (reply_text, tokens_used).
    """
    client = _get_client()
    mod_name = MODULE_NAMES.get(module, module)

    doc_block = _build_doc_block(file_path, mime_type)

    # Build messages: inject doc block on first user turn only
    messages: list[dict] = []
    for i, msg in enumerate(history):
        if i == 0 and msg["role"] == "user" and doc_block:
            messages.append({
                "role": "user",
                "content": [doc_block, {"type": "text", "text": msg["content"]}],
            })
        else:
            messages.append({"role": msg["role"], "content": msg["content"]})

    # Append current user message
    if not messages or messages[-1]["role"] != "user":
        if doc_block and not messages:
            messages.append({
                "role": "user",
                "content": [doc_block, {"type": "text", "text": user_message}],
            })
        else:
            messages.append({"role": "user", "content": user_message})

    system = (
        f"{SYSTEM_TUTOR}\n\n"
        f"Documento activo: '{doc_name}' (módulo: {mod_name})."
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=messages[-20:],  # keep last 20 turns to stay within context
    )

    text = response.content[0].text if response.content else "—"
    tokens = response.usage.input_tokens + response.usage.output_tokens
    return text, tokens


def generate_repo_report(doc_summaries: list[dict]) -> tuple[str, int]:
    """
    Generate a coverage report for the entire document repository.
    doc_summaries: list of {"name", "module", "size_human", "summary"}
    Returns (report_text, tokens_used).
    """
    client = _get_client()

    if not doc_summaries:
        doc_list = "No hay documentos cargados aún."
    else:
        lines = [
            f"- {d['name']} ({MODULE_NAMES.get(d['module'], d['module'])}, "
            f"{d['size_human']}): {d.get('summary') or 'sin resumen'}"
            for d in doc_summaries
        ]
        doc_list = "\n".join(lines)

    prompt = (
        f"Soy instructor del curso 'CiberSec 101' de ciberseguridad básica (8 módulos).\n"
        f"Tengo {len(doc_summaries)} documento(s) cargados en el repositorio:\n\n"
        f"{doc_list}\n\n"
        "Genera un reporte en español con:\n"
        "1. Análisis de cobertura del curso (qué módulos tienen material)\n"
        "2. Módulos que necesitan más recursos\n"
        "3. Recomendaciones concretas de materiales adicionales para los módulos sin documentos\n"
        "Sé conciso, directo y usa formato con secciones claras."
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text if response.content else "—"
    tokens = response.usage.input_tokens + response.usage.output_tokens
    return text, tokens
