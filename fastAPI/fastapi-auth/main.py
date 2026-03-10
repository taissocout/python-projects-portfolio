"""
main.py — Ponto de entrada da API de autenticação.

Projeto : fastapi-auth — DIO Bootcamp 2026
Módulo  : Autenticação e Autorização em FastAPI

Arquitetura:
  main.py
  ├── config.py              — configurações via pydantic-settings
  ├── database.py            — engine e sessão assíncrona
  ├── models.py              — User + RefreshToken (SQLAlchemy 2.0)
  ├── schemas.py             — contratos Pydantic v2
  ├── dependencies.py        — get_current_user, get_current_superuser
  ├── services/
  │   └── auth_service.py    — hash, JWT, CRUD de user/token
  └── routers/
      └── auth.py            — /auth/* (register, login, refresh, logout, me)

Como executar:
  uvicorn main:app --reload --port 8003

Documentação:
  http://localhost:8003/docs
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from database import init_db
from routers import auth_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando fastapi-auth...")
    await init_db()
    logger.info("Banco de dados inicializado.")
    yield
    logger.info("Encerrando aplicação.")


app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description="API de Autenticação com JWT — DIO Bootcamp 2026",
    docs_url="/docs",
    redoc_url="/redoc",
    # Em produção: sem docs expostos (OWASP A05)
    openapi_url="/openapi.json" if not settings.is_production else None,
    lifespan=lifespan,
)

# CORS — nunca allow_origins=["*"] em produção (OWASP A05)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Captura exceções não tratadas. Sem stack trace ao cliente (OWASP A09)."""
    logger.exception(f"Não tratado: {request.method} {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno. Tente novamente mais tarde."},
    )


app.include_router(auth_router)


@app.get("/", tags=["health"])
async def root():
    return {
        "status": "ok",
        "app": settings.app_title,
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
async def health():
    return {"status": "healthy", "auth": "JWT + bcrypt", "tokens": "access + refresh"}
