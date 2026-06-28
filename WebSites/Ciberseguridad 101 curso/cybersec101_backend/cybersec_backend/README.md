# CiberSec 101 — Document Management Backend

Backend en Python/FastAPI para la plataforma de ciberseguridad.  
Gestión de documentos con persistencia en SQLite, almacenamiento de archivos en disco y análisis IA con Anthropic.

---

## Arquitectura

```
cybersec_backend/
├── main.py                  ← Entrada FastAPI, CORS, lifespan
├── config.py                ← Settings con pydantic-settings (.env)
├── database.py              ← SQLAlchemy engine + session
├── models.py                ← Tablas: Document, ChatMessage, ActivityLog, AIQueryLog
├── schemas.py               ← Pydantic schemas (request/response)
├── routers/
│   ├── documents.py         ← CRUD + upload + descarga de archivos
│   ├── chat.py              ← Chat IA multi-turno por documento
│   └── dashboard.py         ← Estadísticas + actividad + reporte IA
├── services/
│   ├── ai_service.py        ← Anthropic: resumen, chat, reporte
│   └── storage_service.py   ← Guardar/eliminar archivos en disco
├── storage/files/           ← Archivos subidos (gitignored)
├── cybersec101.db           ← SQLite (auto-creado)
├── requirements.txt
└── .env.example
```

---

## Instalación rápida

```bash
# 1. Clonar / entrar al directorio
cd cybersec_backend

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env y poner tu ANTHROPIC_API_KEY

# 5. Correr el servidor
python main.py
# → http://localhost:8000
# → http://localhost:8000/docs  (Swagger UI)
```

---

## API Reference

### Documentos

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET`  | `/api/documents` | Listar (filtros: module, status, search) |
| `POST` | `/api/documents` | Subir archivo (multipart/form-data) |
| `GET`  | `/api/documents/{id}` | Obtener documento por ID |
| `PATCH`| `/api/documents/{id}` | Actualizar módulo / descripción |
| `DELETE`| `/api/documents/{id}` | Eliminar documento y archivo |
| `GET`  | `/api/documents/{id}/download` | Descargar archivo original |
| `POST` | `/api/documents/{id}/regenerate-summary` | Regenerar resumen IA |

### Chat IA

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET`  | `/api/documents/{id}/chat` | Historial de conversación |
| `POST` | `/api/documents/{id}/chat` | Enviar mensaje, obtener respuesta IA |
| `DELETE`| `/api/documents/{id}/chat` | Limpiar historial |

### Dashboard

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET`  | `/api/dashboard` | Estadísticas generales |
| `GET`  | `/api/activity` | Log de actividad reciente |
| `POST` | `/api/report` | Generar reporte IA del repositorio |

### Módulos válidos

`general` · `m01` · `m02` · `m03` · `m04` · `m05` · `m06` · `m07` · `m08`

---

## Tipos de archivo aceptados

`PDF` · `TXT` · `MD` · `CSV` · `JPEG` · `PNG` · `GIF` · `WEBP` · `DOC` · `DOCX`

---

## Ejemplo: subir un documento con curl

```bash
curl -X POST http://localhost:8000/api/documents \
  -F "file=@apuntes_modulo1.pdf" \
  -F "module=m01" \
  -F "description=Apuntes clase introductoria"
```

## Ejemplo: chat con documento

```bash
# Enviar pregunta
curl -X POST http://localhost:8000/api/documents/1/chat \
  -H "Content-Type: application/json" \
  -d '{"content": "¿Cuál es la idea principal de este documento?"}'
```

## Ejemplo: dashboard

```bash
curl http://localhost:8000/api/dashboard
```

---

## Variables de entorno (.env)

| Variable | Descripción | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Clave de API de Anthropic | — |
| `DATABASE_URL` | URL de la base de datos | `sqlite:///./cybersec101.db` |
| `STORAGE_PATH` | Ruta de almacenamiento de archivos | `./storage/files` |
| `MAX_FILE_SIZE_MB` | Tamaño máximo por archivo | `20` |
| `CORS_ORIGINS` | Orígenes permitidos (CORS) | `http://localhost:3000,...` |

---

## Integración con el frontend

El frontend HTML puede conectarse al backend cambiando la constante `API_BASE`:

```javascript
const API_BASE = "http://localhost:8000";

// Subir documento
const form = new FormData();
form.append("file", fileInput.files[0]);
form.append("module", "m03");
const res = await fetch(`${API_BASE}/api/documents`, { method: "POST", body: form });

// Chat con documento
const res = await fetch(`${API_BASE}/api/documents/5/chat`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ content: "¿Qué es el phishing?" })
});

// Dashboard
const stats = await fetch(`${API_BASE}/api/dashboard`).then(r => r.json());
```

---

## Stack

- **FastAPI** — Framework web async
- **SQLAlchemy 2.0** — ORM con Mapped columns
- **SQLite** — Base de datos embebida (reemplazable por PostgreSQL)
- **Anthropic SDK** — Claude Sonnet para resúmenes y chat
- **aiofiles** — I/O asíncrono de archivos
- **Pydantic v2** — Validación de esquemas
- **Uvicorn** — Servidor ASGI

---

## Producción

Para usar PostgreSQL en lugar de SQLite:

```env
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/cybersec101
```

```bash
pip install psycopg2-binary
```

Para correr con múltiples workers:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```
