"""
main.py — Ponto de entrada da API assíncrona.

Projeto: Async Blog API — DIO Bootcamp 2026
Módulo:  Manipulação de Dados com FastAPI Assíncrono

Arquitetura:
  main.py
  ├── config.py          — variáveis de ambiente (pydantic-settings)
  ├── database.py        — engine e sessão assíncrona (SQLAlchemy 2.0)
  ├── models.py          — tabelas do banco (User, Post)
  ├── schemas.py         — contratos da API (Pydantic v2)
  ├── crud/
  │   ├── users.py       — operações CRUD assíncronas para usuários
  │   └── posts.py       — operações CRUD assíncronas para posts
  └── routers/
      ├── users.py       — endpoints /users
      └── posts.py       — endpoints /posts

Como executar:
  uvicorn main:app --reload --port 8002

Documentação automática:
  http://localhost:8002/docs   ← Swagger UI
  http://localhost:8002/redoc  ← ReDoc
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from database import init_db
from routers import users_router, posts_router

# Logging estruturado — sem stack trace exposto ao cliente (OWASP A09)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle assíncrono: startup e shutdown da aplicação."""
    logger.info("Iniciando Async Blog API...")
    await init_db()   # cria tabelas se não existirem
    logger.info("Banco de dados inicializado.")
    yield
    logger.info("Encerrando aplicação.")


app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description="API RESTful assíncrona com FastAPI + SQLAlchemy async — DIO Bootcamp 2026",
    docs_url="/docs",
    redoc_url="/redoc",
    # Em produção: desabilitar docs (OWASP A05)
    openapi_url="/openapi.json" if not settings.is_production else None,
    lifespan=lifespan,
)


# ── Middleware de CORS ────────────────────────────────────────────────────────
# NUNCA usar allow_origins=["*"] em produção (OWASP A05)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)


# ── Handler global de exceções ────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Captura exceções não tratadas.
    Loga o detalhe internamente, retorna mensagem genérica ao cliente.
    Previne exposição de stack trace (OWASP A09).
    """
    logger.exception(f"Exceção não tratada: {request.method} {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor. Tente novamente mais tarde."},
    )


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(users_router)
app.include_router(posts_router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/", tags=["health"])
async def root():
    """Health check — verifica se a API está rodando."""
    return {
        "status": "ok",
        "app": settings.app_title,
        "version": settings.app_version,
        "env": settings.app_env,
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
async def health():
    """Health check detalhado para monitoramento."""
    return {
        "status": "healthy",
        "database": "sqlite+aiosqlite (async)",
        "framework": "FastAPI 0.111.0",
        "orm": "SQLAlchemy 2.0 (async)",
    }
