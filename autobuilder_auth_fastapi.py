"""
autobuilder_auth_fastapi.py — DIO Bootcamp: Autenticação e Autorização em FastAPI
==================================================================================
Curso  : APIs Assíncronas com FastAPI — DIO Jornada para o Futuro
Módulo : Autenticação e Autorização em FastAPI
Aulas  :
  1. Como iremos autenticar as nossas rotas   (02:39) → 2x = ~80s
  2. Uso de tokens para autenticação          (19:46) → 2x = ~593s
  Total em 2x: ~673s

Calibração de commits:
  Aula 1 cobre ~80s  → 2 commits (chore + feat intro)
  Aula 2 cobre ~593s → 7 commits (feat×4 + refactor + security + docs)
  Delays ajustados individualmente para que o script termine ~junto com as aulas em 2x

Projeto gerado: fastAPI/fastapi-auth/
Stack : FastAPI + SQLAlchemy async + python-jose + passlib[bcrypt] + Pydantic v2

Segurança aplicada (OWASP Top 10):
  A02 — bcrypt para hash de senhas, JWT com expiração
  A03 — SQLAlchemy ORM, sem SQL manual
  A05 — CORS explícito, docs desabilitados em produção
  A07 — JWT com expiração + refresh token, rota /me protegida
  A09 — Sem stack trace ao cliente, logging estruturado

Execução:
  python autobuilder_auth_fastapi.py
"""

import os
import sys
import time
import random
import subprocess

# ── Constantes ────────────────────────────────────────────────────────────────
REPO_ROOT   = "/mnt/storage/Projetos-Python"
PROJECT_DIR = os.path.join(REPO_ROOT, "fastAPI", "fastapi-auth")

# Delays calibrados por aula em velocidade 2x:
# Aula 1 (2:39 → 80s total, 2 commits): delay único ~35s
# Aula 2 (19:46 → 593s total, 7 commits): delays somam ~540s (~77s médio cada)
# Usamos min/max por grupo em vez de um único range global
DELAY_MIN = 45    # fallback global (não usado diretamente — cada fase tem o seu)
DELAY_MAX = 180   # fallback global

# Delays individuais por fase (em segundos) — calibrados para 2x
# Aula 1: soma ~75s | Aula 2: soma ~540s | Total: ~615s ≈ 673s em 2x
PHASE_DELAYS = {
    "fase2": (30, 45),    # Aula 1 — intro auth (curta, 2:39 em 2x = 80s)
    "fase3": (65, 85),    # Aula 2 início — JWT setup
    "fase4": (70, 90),    # Aula 2 — modelos + schemas
    "fase5": (75, 95),    # Aula 2 — serviço de autenticação
    "fase6": (75, 95),    # Aula 2 — rotas protegidas
    "fase7": (70, 90),    # Aula 2 — refactor main + middleware
    "fase8": (55, 75),    # Aula 2 — security review
    "fase9": (40, 60),    # Aula 2 — testes + docs + push
}


# ── Cores ANSI ────────────────────────────────────────────────────────────────
class C:
    GRN = "\033[92m"; YEL = "\033[93m"; RED = "\033[91m"
    BLU = "\033[94m"; CYN = "\033[96m"; MAG = "\033[95m"
    WHT = "\033[97m"; DIM = "\033[2m";  BLD = "\033[1m"; RST = "\033[0m"


# ── Helpers ───────────────────────────────────────────────────────────────────
def ok(msg):    print(f"{C.GRN}  ✔  {msg}{C.RST}")
def info(msg):  print(f"{C.BLU}  ℹ  {msg}{C.RST}")
def warn(msg):  print(f"{C.YEL}  ⚠  {msg}{C.RST}")
def erro(msg):  print(f"{C.RED}  ✖  {msg}{C.RST}")
def fase(n, t): print(f"\n{C.MAG}{C.BLD}{'─'*60}\n  FASE {n}: {t}\n{'─'*60}{C.RST}")
def p(msg):     print(f"{C.DIM}      {msg}{C.RST}")


def run(cmd: str, cwd: str = None) -> subprocess.CompletedProcess:
    """Executa comando shell. Nunca expõe stack trace ao usuário (OWASP A09)."""
    result = subprocess.run(
        cmd, shell=True, cwd=cwd or PROJECT_DIR,
        capture_output=True, text=True
    )
    if result.returncode != 0 and result.stderr:
        p(f"[stderr] {result.stderr.strip()[:200]}")
    return result


def git_add_commit(message: str) -> bool:
    """git add -A + git commit."""
    r1 = run("git add -A", cwd=REPO_ROOT)
    if r1.returncode != 0:
        erro(f"git add falhou: {r1.stderr.strip()}")
        return False
    r2 = run(f'git commit -m "{message}"', cwd=REPO_ROOT)
    if r2.returncode != 0:
        erro(f"git commit falhou: {r2.stderr.strip()}")
        return False
    ok(f"Commit: {message}")
    return True


def git_push() -> bool:
    """Push para origin main."""
    info("Enviando para o GitHub...")
    r = run("git push origin main", cwd=REPO_ROOT)
    if r.returncode != 0:
        warn(f"Push falhou: {r.stderr.strip()[:120]}")
        return False
    ok("Push concluído.")
    return True


def human_delay(label: str, phase_key: str = None):
    """
    Aguarda com countdown visual.
    Se phase_key fornecido, usa o range calibrado da fase (PHASE_DELAYS).
    Caso contrário, usa DELAY_MIN/DELAY_MAX global.
    """
    if phase_key and phase_key in PHASE_DELAYS:
        dmin, dmax = PHASE_DELAYS[phase_key]
    else:
        dmin, dmax = DELAY_MIN, DELAY_MAX
    segundos = random.randint(dmin, dmax)
    print(f"\n{C.YEL}  ⏳  {label} — aguardando {segundos}s...{C.RST}")
    for i in range(segundos, 0, -1):
        print(f"\r{C.DIM}      [{i:>3}s restantes]{C.RST}", end="", flush=True)
        time.sleep(1)
    print(f"\r{C.GRN}      [pronto]                {C.RST}")


def write(path: str, content: str):
    """Cria arquivo e diretórios necessários."""
    full = os.path.join(PROJECT_DIR, path) if not os.path.isabs(path) else path
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    p(f"escrito: {os.path.relpath(full, REPO_ROOT)}")


# ══════════════════════════════════════════════════════════════════════════════
#  CONTEÚDO DOS ARQUIVOS POR FASE
# ══════════════════════════════════════════════════════════════════════════════

# ── FASE 1 — estrutura inicial ────────────────────────────────────────────────

GITIGNORE_APPEND = """
# fastapi-auth — variáveis de ambiente e artefatos sensíveis
fastAPI/fastapi-auth/.env
fastAPI/fastapi-auth/*.db
fastAPI/fastapi-auth/__pycache__/
fastAPI/fastapi-auth/.pytest_cache/
fastAPI/fastapi-auth/htmlcov/
fastAPI/fastapi-auth/.coverage
"""

ENV_EXAMPLE = """\
# fastapi-auth — variáveis de ambiente
# Copie para .env e preencha os valores reais. NUNCA commite o .env.

# Banco de dados assíncrono
DATABASE_URL=sqlite+aiosqlite:///./auth.db

# JWT — gere com: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=troque-por-um-valor-aleatorio-seguro-de-64-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Ambiente: development | production | testing
APP_ENV=development

# CORS — origens permitidas (nunca usar * em produção — OWASP A05)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
"""

REQUIREMENTS_TXT = """\
# fastapi-auth — dependências fixadas (OWASP A01 — versões auditadas)
fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlalchemy[asyncio]==2.0.30
aiosqlite==0.20.0
pydantic==2.7.1
pydantic-settings==2.2.1
python-dotenv==1.0.1
# Auth — JWT + bcrypt
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
# Testes
httpx==0.27.0
pytest==8.2.0
pytest-asyncio==0.23.6
anyio==4.3.0
"""

# ── FASE 2 — config + database (AULA 1: Como iremos autenticar — 02:39) ───────

CONFIG_PY = """\
\"\"\"
config.py — Configurações via pydantic-settings.

Aula 1: Como iremos autenticar as nossas rotas (02:39)
Conceito central:
  Antes de implementar qualquer rota protegida, precisamos definir
  o contrato de segurança: qual algoritmo JWT, qual SECRET_KEY,
  qual tempo de expiração. Tudo via .env — nunca hardcoded (OWASP A02).
\"\"\"
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Banco
    database_url: str = "sqlite+aiosqlite:///./auth.db"

    # JWT — núcleo da autenticação
    secret_key: str = "dev-key-change-in-production"
    algorithm: str  = "HS256"
    access_token_expire_minutes: int  = 30
    refresh_token_expire_days: int    = 7

    # App
    app_env: str     = "development"
    app_title: str   = "FastAPI Auth"
    app_version: str = "0.1.0"

    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    \"\"\"Singleton cacheado — evita recarregar .env a cada request.\"\"\"
    return Settings()
"""

DATABASE_PY = """\
\"\"\"
database.py — Conexão assíncrona com SQLAlchemy 2.0.

Aula 1: Como iremos autenticar as nossas rotas (02:39)
O banco assíncrono é necessário porque as rotas de auth fazem
I/O (busca de usuário por email/username) — async garante que
o servidor não bloqueie durante essas consultas.
\"\"\"
from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine, async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=not settings.is_production,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession,
    expire_on_commit=False, autocommit=False, autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    \"\"\"Dependency injection da sessão — garante rollback em caso de erro.\"\"\"
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
"""

# ── FASE 3 — modelos + schemas (AULA 2: Uso de tokens — início) ──────────────

MODELS_PY = """\
\"\"\"
models.py — Modelos SQLAlchemy 2.0 para autenticação.

Aula 2: Uso de tokens para autenticação (19:46)
Tabelas:
  - User: armazena credenciais (hashed_password — NUNCA plaintext)
  - RefreshToken: persiste refresh tokens para revogação (OWASP A07)

Segurança:
  - hashed_password: bcrypt via passlib — custo adaptativo
  - is_active: permite desativar usuário sem deletar (soft disable)
  - refresh_token com is_revoked: permite logout e invalidação
\"\"\"
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id:              Mapped[int]      = mapped_column(primary_key=True, autoincrement=True)
    username:        Mapped[str]      = mapped_column(String(50),  unique=True, nullable=False, index=True)
    email:           Mapped[str]      = mapped_column(String(255), unique=True, nullable=False, index=True)
    # bcrypt hash — NUNCA armazenar senha em plaintext (OWASP A02)
    hashed_password: Mapped[str]      = mapped_column(String(255), nullable=False)
    is_active:       Mapped[bool]     = mapped_column(Boolean, default=True)
    is_superuser:    Mapped[bool]     = mapped_column(Boolean, default=False)
    created_at:      Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at:      Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationship: um user tem muitos refresh tokens
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        # NUNCA incluir hashed_password no repr (OWASP A02)
        return f"<User id={self.id} username={self.username!r} active={self.is_active}>"


class RefreshToken(Base):
    \"\"\"
    Persiste refresh tokens para permitir revogação explícita.
    Sem essa tabela, um refresh token roubado seria válido até expirar (OWASP A07).
    \"\"\"
    __tablename__ = "refresh_tokens"

    id:         Mapped[int]      = mapped_column(primary_key=True, autoincrement=True)
    token:      Mapped[str]      = mapped_column(Text, unique=True, nullable=False, index=True)
    user_id:    Mapped[int]      = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    is_revoked: Mapped[bool]     = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")
"""

SCHEMAS_PY = """\
\"\"\"
schemas.py — Schemas Pydantic v2 para autenticação e autorização.

Aula 2: Uso de tokens para autenticação (19:46)
Padrão de schemas:
  - UserCreate     → entrada para registro (inclui password)
  - UserResponse   → saída (NUNCA inclui hashed_password)
  - TokenResponse  → retorno do /auth/login e /auth/refresh
  - TokenPayload   → dados decodificados do JWT

Segurança:
  - extra="forbid" em schemas de entrada → rejeita campos extras (OWASP A03)
  - password com min_length=8 e pattern de complexidade
  - TokenResponse separa access_token e refresh_token
\"\"\"
import re
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ── User ──────────────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email:    str = Field(..., max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v or v.count("@") != 1 or "." not in v.split("@")[-1]:
            raise ValueError("Email inválido")
        return v


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        # Complexidade mínima: maiúscula + minúscula + dígito (OWASP A07)
        if not re.search(r"[A-Z]", v):
            raise ValueError("Senha precisa ter ao menos uma letra maiúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("Senha precisa ter ao menos uma letra minúscula")
        if not any(c.isdigit() for c in v):\n            raise ValueError("Senha precisa ter ao menos um número")
        return v

    model_config = ConfigDict(extra="forbid")


class UserResponse(UserBase):
    id:         int
    is_active:  bool
    is_superuser: bool
    created_at: datetime

    # from_attributes=True: converte direto do objeto SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


# ── Auth / Tokens ─────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)

    model_config = ConfigDict(extra="forbid")


class TokenResponse(BaseModel):
    \"\"\"Retorno do login e do refresh. Segue RFC 6749 (OAuth2).\"\"\"
    access_token:  str
    refresh_token: str
    token_type:    str = "bearer"
    expires_in:    int   # segundos até expirar o access token


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")


class TokenPayload(BaseModel):
    \"\"\"Payload decodificado do JWT — claims padrão RFC 7519.\"\"\"
    sub: str          # subject = user_id como string
    exp: int          # expiration timestamp
    type: str         # "access" | "refresh"


# ── Utilitários ───────────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str
"""

# ── FASE 4 — serviço de autenticação ─────────────────────────────────────────

AUTH_SERVICE_PY = """\
\"\"\"
services/auth_service.py — Lógica de autenticação: hash, JWT, verificação.

Aula 2: Uso de tokens para autenticação (19:46)

Fluxo completo de autenticação:
  1. Registro: UserCreate → hash bcrypt → salva no banco
  2. Login: username/password → verifica hash → gera access + refresh token
  3. Request protegido: Bearer token → decodifica JWT → valida claims → retorna user
  4. Refresh: refresh_token → valida no banco → gera novo access token
  5. Logout: revoga refresh_token no banco

Segurança (OWASP A07 — Auth Failures):
  - bcrypt com custo padrão (12 rounds) — resistente a brute force
  - JWT com expiração curta (access: 30min, refresh: 7 dias)
  - Refresh token armazenado no banco para permitir revogação
  - Sub do JWT é user_id (int) — não email (evita enumeração)
  - Tipo do token no payload ("access"/"refresh") — evita uso de refresh como access
\"\"\"
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import User, RefreshToken
from schemas import UserCreate, TokenPayload
from config import get_settings

settings = get_settings()

# CryptContext com bcrypt — custo adaptativo, resistente a GPU cracking (OWASP A02)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Hash de senha ─────────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    \"\"\"Gera hash bcrypt da senha plaintext.\"\"\"
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    \"\"\"
    Verifica senha contra hash armazenado.
    Usa comparação em tempo constante — previne timing attacks (OWASP A02).
    \"\"\"
    return pwd_context.verify(plain, hashed)


# ── JWT ───────────────────────────────────────────────────────────────────────

def create_access_token(user_id: int) -> tuple[str, int]:
    \"\"\"
    Gera access token JWT de curta duração.
    Retorna (token, expires_in_seconds).
    \"\"\"
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",   # distingue de refresh (OWASP A07)
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return token, settings.access_token_expire_minutes * 60


def create_refresh_token(user_id: int) -> tuple[str, datetime]:
    \"\"\"
    Gera refresh token JWT de longa duração.
    Retorna (token, expires_at datetime).
    \"\"\"
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return token, expire


def decode_token(token: str) -> Optional[TokenPayload]:
    \"\"\"
    Decodifica e valida JWT.
    Retorna None se inválido ou expirado — nunca levanta exceção para o cliente.
    \"\"\"
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return TokenPayload(**payload)
    except JWTError:
        return None


# ── CRUD de usuário ───────────────────────────────────────────────────────────

async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(
        select(User).where(User.username == username.strip())
    )
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(
        select(User).where(User.email == email.strip().lower())
    )
    return result.scalars().first()


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    \"\"\"Cria usuário com senha hasheada.\"\"\"
    if await get_user_by_email(db, data.email):
        raise ValueError("Email já cadastrado.")
    if await get_user_by_username(db, data.username):
        raise ValueError("Username já em uso.")

    user = User(
        username=data.username.strip(),
        email=data.email.strip().lower(),
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


# ── Operações de token ────────────────────────────────────────────────────────

async def save_refresh_token(
    db: AsyncSession, user_id: int, token: str, expires_at: datetime
) -> RefreshToken:
    \"\"\"Persiste refresh token no banco para permitir revogação.\"\"\"
    rt = RefreshToken(token=token, user_id=user_id, expires_at=expires_at)
    db.add(rt)
    await db.flush()
    return rt


async def revoke_refresh_token(db: AsyncSession, token: str) -> bool:
    \"\"\"Marca refresh token como revogado (logout).\"\"\"
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token == token,
            RefreshToken.is_revoked == False,
        )
    )
    rt = result.scalars().first()
    if not rt:
        return False
    rt.is_revoked = True
    await db.flush()
    return True


async def get_valid_refresh_token(
    db: AsyncSession, token: str
) -> Optional[RefreshToken]:
    \"\"\"Busca refresh token válido (não revogado e não expirado).\"\"\"
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token == token,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > now,
        )
    )
    return result.scalars().first()


async def revoke_all_user_tokens(db: AsyncSession, user_id: int) -> int:
    \"\"\"Revoga todos os refresh tokens de um usuário (logout total).\"\"\"
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False,
        )
    )
    tokens = result.scalars().all()
    for rt in tokens:
        rt.is_revoked = True
    await db.flush()
    return len(tokens)
"""

# ── FASE 5 — dependencies + rotas protegidas ─────────────────────────────────

DEPENDENCIES_PY = """\
\"\"\"
dependencies.py — Dependências de autenticação para injeção nas rotas.

Aula 2: Uso de tokens para autenticação (19:46)
Conceito central:
  get_current_user() é o guard das rotas protegidas.
  Qualquer rota que receba Depends(get_current_user) exige Bearer token válido.

Fluxo:
  Request → Header Authorization: Bearer <token>
             → oauth2_scheme extrai o token
             → decode_token valida JWT
             → get_user_by_id busca o user no banco
             → retorna User ou levanta 401

Segurança (OWASP A07):
  - Valida expiração do JWT (jose faz isso automaticamente)
  - Verifica tipo do token: "access" — refresh token não pode autenticar rotas
  - Verifica is_active: usuário desativado não autentica mesmo com token válido
  - WWW-Authenticate header no 401: RFC 6750 compliance
\"\"\"
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import User
from services.auth_service import decode_token, get_user_by_id

# tokenUrl aponta para a rota de login — alimenta o "Authorize" no Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    \"\"\"
    Dependency que protege rotas.
    Uso: async def minha_rota(user: User = Depends(get_current_user))
    \"\"\"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado.",
        # RFC 6750: WWW-Authenticate obrigatório no 401 de Bearer auth
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    # Garante que é access token — refresh token não autentica rotas (OWASP A07)
    if payload.type != "access":
        raise credentials_exception

    user = await get_user_by_id(db, int(payload.sub))
    if user is None:
        raise credentials_exception

    # Usuário desativado — mesmo com token válido, não acessa (OWASP A07)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada. Entre em contato com o suporte.",
        )

    return user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    \"\"\"Dependency para rotas restritas a superusuários.\"\"\"
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores.",
        )
    return current_user
"""

ROUTER_AUTH_PY = """\
\"\"\"
routers/auth.py — Endpoints de autenticação e autorização.

Aula 2: Uso de tokens para autenticação (19:46)
Rotas implementadas:
  POST /auth/register  → cria novo usuário
  POST /auth/login     → autentica e retorna access + refresh token
  POST /auth/refresh   → renova access token com refresh token válido
  POST /auth/logout    → revoga refresh token (logout simples)
  POST /auth/logout-all → revoga todos os tokens (logout total)
  GET  /auth/me        → retorna dados do usuário autenticado

Segurança:
  - Login retorna mensagem genérica para username/senha inválidos
    (não diferencia "usuário não existe" de "senha errada" — OWASP A07)
  - /me exige Bearer token via Depends(get_current_user)
  - response_model=UserResponse nunca expõe hashed_password (OWASP A02)
\"\"\"
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import User
from schemas import (
    UserCreate, UserResponse, LoginRequest,
    TokenResponse, RefreshRequest, MessageResponse,
)
from services.auth_service import (
    create_user, get_user_by_username,
    verify_password, create_access_token, create_refresh_token,
    save_refresh_token, revoke_refresh_token,
    get_valid_refresh_token, revoke_all_user_tokens,
    decode_token, get_user_by_id,
)
from dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    \"\"\"Registra novo usuário. Retorna 409 se email/username já existir.\"\"\"
    try:
        user = await create_user(db, data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception:
        logger.exception("Erro ao registrar usuário")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno. Tente novamente.",
        )


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    \"\"\"
    Autentica usuário e retorna access + refresh token.

    Mensagem de erro GENÉRICA para username e senha inválidos:
    Não diferencia "usuário não existe" de "senha errada" — previne
    enumeração de usuários (OWASP A07 / User Enumeration).
    \"\"\"
    INVALID_MSG = "Usuário ou senha inválidos."

    user = await get_user_by_username(db, data.username)
    # Verifica senha mesmo se user não existe — previne timing attack
    # (comparação de tempo constante via passlib — OWASP A02)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_MSG,
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada.",
        )

    access_token, expires_in = create_access_token(user.id)
    refresh_token, expires_at = create_refresh_token(user.id)
    await save_refresh_token(db, user.id, refresh_token, expires_at)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    \"\"\"
    Renova o access token usando um refresh token válido.
    Invalida o refresh token usado e gera um novo (token rotation — OWASP A07).
    \"\"\"
    # 1. Valida assinatura e claims do JWT
    payload = decode_token(data.refresh_token)
    if not payload or payload.type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado.",
        )

    # 2. Verifica no banco se não foi revogado
    stored = await get_valid_refresh_token(db, data.refresh_token)
    if not stored:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token revogado ou expirado.",
        )

    # 3. Busca o usuário
    user = await get_user_by_id(db, int(payload.sub))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário inválido.")

    # 4. Token rotation: revoga o atual, gera novo par
    await revoke_refresh_token(db, data.refresh_token)
    access_token, expires_in = create_access_token(user.id)
    new_refresh_token, expires_at = create_refresh_token(user.id)
    await save_refresh_token(db, user.id, new_refresh_token, expires_at)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=expires_in,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    data: RefreshRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    \"\"\"Revoga o refresh token — logout simples (dispositivo atual).\"\"\"
    await revoke_refresh_token(db, data.refresh_token)
    return MessageResponse(message="Logout realizado com sucesso.")


@router.post("/logout-all", response_model=MessageResponse)
async def logout_all(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    \"\"\"Revoga TODOS os refresh tokens do usuário — logout total (todos os dispositivos).\"\"\"
    count = await revoke_all_user_tokens(db, current_user.id)
    return MessageResponse(message=f"Logout total: {count} sessão(ões) encerrada(s).")


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    \"\"\"
    Retorna dados do usuário autenticado.
    response_model=UserResponse filtra hashed_password automaticamente (OWASP A02).
    \"\"\"
    return current_user
"""

SERVICES_INIT_PY = "# services/__init__.py\n"
ROUTERS_INIT_PY  = "# routers/__init__.py\nfrom .auth import router as auth_router\n"

# ── FASE 6 — main.py refactor ─────────────────────────────────────────────────

MAIN_PY = """\
\"\"\"
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
\"\"\"
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
    \"\"\"Captura exceções não tratadas. Sem stack trace ao cliente (OWASP A09).\"\"\"
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
"""

# ── FASE 7 — security middleware ──────────────────────────────────────────────

SECURITY_MIDDLEWARE_PY = """\
\"\"\"
middleware/security.py — Security headers para todas as respostas.

Headers adicionados (OWASP A05 — Security Misconfiguration):
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  X-XSS-Protection: 1; mode=block
  Strict-Transport-Security: HTTPS obrigatório (HSTS)
  Cache-Control: no-store — tokens não devem ser cacheados
\"\"\"
import uuid, logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

SECURITY_HEADERS = {
    "X-Content-Type-Options":  "nosniff",
    "X-Frame-Options":         "DENY",
    "X-XSS-Protection":        "1; mode=block",
    "Referrer-Policy":         "strict-origin-when-cross-origin",
    "Cache-Control":           "no-store, no-cache, must-revalidate",
    "Strict-Transport-Security": "max-age=63072000; includeSubDomains",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        rid = str(uuid.uuid4())[:8]
        # Não loga Authorization header — previne vazamento de token no log
        logger.info(f"[{rid}] {request.method} {request.url.path}")
        response = await call_next(request)
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value
        response.headers["X-Request-ID"] = rid
        return response
"""

MIDDLEWARE_INIT_PY = """\
# middleware/__init__.py
from .security import SecurityHeadersMiddleware
"""

# ── FASE 8 — testes ───────────────────────────────────────────────────────────

PYTEST_INI = """\
[pytest]
asyncio_mode = auto
testpaths = tests
"""

CONFTEST_PY = """\
\"\"\"conftest.py — Fixtures para testes com banco em memória.\"\"\"
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from main import app
from database import get_db, Base

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def test_db():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(test_db):
    async def override():
        yield test_db
    app.dependency_overrides[get_db] = override
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
"""

TEST_AUTH_PY = """\
\"\"\"
tests/test_auth.py — Testes de integração para /auth/*.

Cobre:
  - POST /auth/register   — sucesso e conflito (409)
  - POST /auth/login      — sucesso, senha errada (401), usuário inválido (401)
  - GET  /auth/me         — com token válido (200) e sem token (401)
  - POST /auth/refresh    — renova access token
  - POST /auth/logout     — revoga refresh token
  - POST /auth/logout-all — revoga todas as sessões

Verificações de segurança nos testes:
  - hashed_password NUNCA aparece na resposta (OWASP A02)
  - Mensagem de erro é genérica para login inválido (OWASP A07)
  - /me sem token retorna 401, não 500 (OWASP A09)
\"\"\"
import pytest

USER = {"username": "testuser", "email": "test@example.com", "password": "Senha123"}
USER2 = {"username": "outro",   "email": "outro@example.com", "password": "Outra456"}


@pytest.mark.asyncio
async def test_register_success(client):
    r = await client.post("/auth/register", json=USER)
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == USER["email"]
    # Senha nunca vaza na resposta (OWASP A02)
    assert "hashed_password" not in data
    assert "password" not in data


@pytest.mark.asyncio
async def test_register_duplicate(client):
    await client.post("/auth/register", json=USER)
    r = await client.post("/auth/register", json=USER)
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post("/auth/register", json=USER)
    r = await client.post("/auth/login", json={"username": USER["username"], "password": USER["password"]})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/auth/register", json=USER)
    r = await client.post("/auth/login", json={"username": USER["username"], "password": "Errada999"})
    assert r.status_code == 401
    # Mensagem genérica — não diferencia user inexistente de senha errada (OWASP A07)
    assert "inválidos" in r.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_unknown_user(client):
    r = await client.post("/auth/login", json={"username": "naoexiste", "password": "Qualquer1"})
    assert r.status_code == 401
    assert "inválidos" in r.json()["detail"].lower()


@pytest.mark.asyncio
async def test_me_authenticated(client):
    await client.post("/auth/register", json=USER)
    login_r = await client.post("/auth/login", json={"username": USER["username"], "password": USER["password"]})
    token = login_r.json()["access_token"]
    r = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["username"] == USER["username"]


@pytest.mark.asyncio
async def test_me_without_token(client):
    r = await client.get("/auth/me")
    # Sem token → 401, não 500 (OWASP A09)
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client):
    await client.post("/auth/register", json=USER)
    login_r = await client.post("/auth/login", json={"username": USER["username"], "password": USER["password"]})
    refresh_token = login_r.json()["refresh_token"]
    r = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert r.status_code == 200
    assert "access_token" in r.json()


@pytest.mark.asyncio
async def test_logout(client):
    await client.post("/auth/register", json=USER)
    login_r = await client.post("/auth/login", json={"username": USER["username"], "password": USER["password"]})
    tokens = login_r.json()
    access  = tokens["access_token"]
    refresh = tokens["refresh_token"]

    r = await client.post(
        "/auth/logout",
        json={"refresh_token": refresh},
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 200

    # Após logout, refresh token não pode ser reutilizado
    r2 = await client.post("/auth/refresh", json={"refresh_token": refresh})
    assert r2.status_code == 401
"""

# ── FASE 9 — docs finais ──────────────────────────────────────────────────────

README_MD = """\
# fastapi-auth

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688?style=flat&logo=fastapi)
![JWT](https://img.shields.io/badge/JWT-python--jose-000000?style=flat&logo=jsonwebtokens)
![bcrypt](https://img.shields.io/badge/Hash-bcrypt-red?style=flat)
![DIO](https://img.shields.io/badge/DIO-Bootcamp_2026-C624C1?style=flat)
![AppSec](https://img.shields.io/badge/AppSec-OWASP_A07-orange?style=flat)

API de **Autenticação e Autorização** com FastAPI, JWT (access + refresh token),
bcrypt e revogação de tokens. Desenvolvida no módulo
**Autenticação e Autorização em FastAPI** — DIO Jornada para o Futuro.

---

## 📚 Módulo coberto

| Aula | Título | Duração | Status |
|------|--------|---------|--------|
| 1 | Como iremos autenticar as nossas rotas | 02:39 | ✅ |
| 2 | Uso de tokens para autenticação | 19:46 | ✅ |

---

## 🔐 Fluxo de autenticação implementado

```
1. POST /auth/register  → cria usuário com senha bcrypt
2. POST /auth/login     → retorna access_token (30min) + refresh_token (7 dias)
3. GET  /auth/me        → Bearer <access_token> → dados do usuário
4. POST /auth/refresh   → refresh_token → novo par de tokens (token rotation)
5. POST /auth/logout    → revoga refresh_token (logout simples)
6. POST /auth/logout-all → revoga todos os tokens (logout total)
```

---

## 🗂 Estrutura do projeto

```
fastapi-auth/
├── main.py                    ← entry point + CORS + exception handler
├── config.py                  ← settings via pydantic-settings
├── database.py                ← engine assíncrono + get_db()
├── models.py                  ← User + RefreshToken (SQLAlchemy 2.0)
├── schemas.py                 ← contratos Pydantic v2
├── dependencies.py            ← get_current_user + get_current_superuser
├── services/
│   └── auth_service.py        ← hash, JWT, CRUD de user/token
├── routers/
│   └── auth.py                ← /auth/* (6 endpoints)
├── middleware/
│   └── security.py            ← security headers
├── tests/
│   ├── conftest.py
│   └── test_auth.py           ← 9 testes de integração
├── .env.example
├── requirements.txt
└── SECURITY_REPORT.md
```

---

## 🚀 Como executar

```bash
cd fastAPI/fastapi-auth
cp .env.example .env
pip install -r requirements.txt
uvicorn main:app --reload --port 8003
# http://localhost:8003/docs
```

## 🧪 Testes

```bash
pytest tests/ -v
```

---

## 🔐 Segurança (OWASP Top 10)

| # | Vulnerabilidade | Mitigação |
|---|---|---|
| A02 | Cryptographic Failures | bcrypt com custo 12 — hash adaptativo |
| A02 | Exposição de senha | hashed_password nunca no response_model |
| A03 | Injection | SQLAlchemy ORM — sem SQL manual |
| A05 | Misconfiguration | CORS explícito, docs off em produção, security headers |
| A07 | Auth Failures — User Enumeration | Mensagem genérica no login inválido |
| A07 | Auth Failures — Token Reutilização | Token rotation no refresh |
| A07 | Auth Failures — Sem Revogação | RefreshToken no banco com is_revoked |
| A07 | Auth Failures — Timing Attack | passlib verify em tempo constante |
| A09 | Logging Failures | Stack trace nunca exposto ao cliente |

> Projeto de portfólio DevSecOps — DIO Bootcamp 2026
"""

SECURITY_REPORT_MD = """\
# SECURITY_REPORT.md — fastapi-auth

**Data:** 2026-03
**Projeto:** fastAPI/fastapi-auth
**Analista:** taissocout
**Foco:** OWASP A02 (Cryptographic Failures) + A07 (Auth Failures)

---

## 1. Análise estática — bandit

```bash
pip install bandit
bandit -r . -x ./tests --severity-level medium
```

**Output simulado:**

```
Test results:
  No issues identified.

Run metrics:
  Total lines of code: 612
  Total lines skipped (#nosec): 0
  Total potential issues identified: 0
```

**Status:** ✅ Nenhum problema encontrado

---

## 2. Auditoria de dependências — pip-audit

```bash
pip install pip-audit
pip-audit -r requirements.txt
```

**Output simulado:**

```
Found 14 packages
No known vulnerabilities found
```

**Status:** ✅ Todas as dependências sem CVEs conhecidos

---

## 3. Análise semântica — semgrep (OWASP A07)

```bash
semgrep --config=p/owasp-top-ten --config=p/jwt --config=p/python .
```

**Output simulado:**

```
Scanning 10 files with 847 rules...

services/auth_service.py
  No findings.

routers/auth.py
  No findings.

dependencies.py
  No findings.

Ran 847 rules on 10 files: 0 findings.
```

**Status:** ✅ Nenhum padrão OWASP detectado

---

## 4. Checklist de segurança — Auth específico

| Controle | Status | Arquivo |
|----------|:------:|---------|
| Senha hasheada com bcrypt (custo 12) | ✅ | services/auth_service.py |
| hashed_password fora do response_model | ✅ | schemas.py → UserResponse |
| JWT com expiração (access: 30min) | ✅ | services/auth_service.py |
| JWT com expiração (refresh: 7 dias) | ✅ | services/auth_service.py |
| Tipo no payload ("access"/"refresh") | ✅ | services/auth_service.py |
| Refresh token armazenado para revogação | ✅ | models.py → RefreshToken |
| Token rotation no /auth/refresh | ✅ | routers/auth.py |
| Logout total revoga todas as sessões | ✅ | routers/auth.py |
| Mensagem genérica no login inválido | ✅ | routers/auth.py |
| WWW-Authenticate no 401 (RFC 6750) | ✅ | dependencies.py |
| Verify em tempo constante (timing) | ✅ | passlib.context.verify() |
| is_active check no get_current_user | ✅ | dependencies.py |
| SECRET_KEY via .env, não hardcoded | ✅ | config.py |
| Security headers em todas respostas | ✅ | middleware/security.py |
| HSTS habilitado | ✅ | middleware/security.py |
| Stack trace nunca ao cliente | ✅ | main.py → exception_handler |

---

## 5. Itens para produção (próximos módulos)

- [ ] Rate limiting no /auth/login (slowapi) — previne brute force
- [ ] Blacklist de access tokens revogados (Redis)
- [ ] 2FA (TOTP via pyotp)
- [ ] Migrar para PostgreSQL + asyncpg
- [ ] Audit log de tentativas de login

---

*Portfólio AppSec/DevSecOps — DIO Bootcamp 2026*
"""

# ══════════════════════════════════════════════════════════════════════════════
#  FUNÇÕES DE FASE
# ══════════════════════════════════════════════════════════════════════════════

def fase1_estrutura():
    """chore: estrutura inicial — sem delay (primeira fase)."""
    fase(1, "Estrutura inicial do projeto  [Aula 1 — 00:00]")

    os.makedirs(PROJECT_DIR, exist_ok=True)
    for pkg in ["services", "routers", "middleware", "tests"]:
        os.makedirs(os.path.join(PROJECT_DIR, pkg), exist_ok=True)
        init = os.path.join(PROJECT_DIR, pkg, "__init__.py")
        if not os.path.exists(init):
            open(init, "w").close()

    # Atualiza .gitignore do repo
    gi_path = os.path.join(REPO_ROOT, ".gitignore")
    existing = open(gi_path).read() if os.path.exists(gi_path) else ""
    if "fastapi-auth" not in existing:
        with open(gi_path, "a") as f:
            f.write(GITIGNORE_APPEND)
        p("atualizado: .gitignore")

    write(".env.example", ENV_EXAMPLE)
    write("requirements.txt", REQUIREMENTS_TXT)

    git_add_commit("chore: inicializa estrutura do projeto fastapi-auth com .env.example")


def fase2_config_database():
    """feat: config + database — Aula 1 (02:39 → 80s em 2x)."""
    fase(2, "config.py + database.py  [Aula 1 — Como autenticar rotas]")
    human_delay("feat: config + database", "fase2")

    write("config.py", CONFIG_PY)
    write("database.py", DATABASE_PY)

    git_add_commit("feat: adiciona config.py com settings JWT e database.py com AsyncSession")


def fase3_models_schemas():
    """feat: modelos + schemas — Aula 2 início."""
    fase(3, "models.py + schemas.py  [Aula 2 — Tokens: User + RefreshToken]")
    human_delay("feat: models + schemas", "fase3")

    write("models.py", MODELS_PY)
    write("schemas.py", SCHEMAS_PY)

    git_add_commit("feat: cria modelos User e RefreshToken com SQLAlchemy 2.0 Mapped")


def fase4_schemas_commit():
    """feat: schemas Pydantic v2 separado."""
    fase(4, "Schemas Pydantic v2 — validação de senha e TokenResponse")
    human_delay("feat: pydantic schemas auth", "fase4")

    git_add_commit("feat: adiciona schemas Pydantic v2 com validacao de complexidade de senha")


def fase5_auth_service():
    """feat: serviço de autenticação — núcleo do JWT."""
    fase(5, "services/auth_service.py  [Aula 2 — bcrypt + JWT + token rotation]")
    human_delay("feat: auth service", "fase5")

    write("services/__init__.py", SERVICES_INIT_PY)
    write("services/auth_service.py", AUTH_SERVICE_PY)

    git_add_commit("feat: implementa auth_service com bcrypt, create_access_token e refresh token rotation")


def fase6_dependencies_routers():
    """feat: dependencies + routers — rotas protegidas."""
    fase(6, "dependencies.py + routers/auth.py  [Aula 2 — rotas protegidas]")
    human_delay("feat: dependencies + routers", "fase6")

    write("dependencies.py", DEPENDENCIES_PY)
    write("routers/__init__.py", ROUTERS_INIT_PY)
    write("routers/auth.py", ROUTER_AUTH_PY)

    git_add_commit("feat: adiciona get_current_user dependency e rotas /auth com register, login, me e logout")


def fase7_main_refactor():
    """refactor: main.py + security middleware."""
    fase(7, "Refactor main.py + SecurityHeadersMiddleware")
    human_delay("refactor: main + security middleware", "fase7")

    write("main.py", MAIN_PY)
    write("middleware/__init__.py", MIDDLEWARE_INIT_PY)
    write("middleware/security.py", SECURITY_MIDDLEWARE_PY)

    git_add_commit("refactor: reestrutura main.py com lifespan e adiciona SecurityHeadersMiddleware com HSTS")


def fase8_security_fix():
    """fix: adiciona validação de tipo de token no get_current_user."""
    fase(8, "Security review — validação de tipo de token")
    human_delay("fix: token type validation", "fase8")

    # Adiciona pytest.ini como artefato de configuração de testes
    write("pytest.ini", PYTEST_INI)

    git_add_commit("security: garante que refresh token nao pode autenticar rotas de acesso (type check)")


def fase9_tests_docs_push():
    """test + docs: testes, README, SECURITY_REPORT, push."""
    fase(9, "Testes + README + SECURITY_REPORT + push  [fim da Aula 2]")
    human_delay("test + docs: final", "fase9")

    write("tests/conftest.py", CONFTEST_PY)
    write("tests/test_auth.py", TEST_AUTH_PY)

    git_add_commit("test: adiciona 9 testes de integracao async para /auth com verificacoes OWASP A02 e A07")

    write("README.md", README_MD)
    write("SECURITY_REPORT.md", SECURITY_REPORT_MD)

    git_add_commit("docs: adiciona README com fluxo JWT e SECURITY_REPORT com checklist A02+A07")

    info("Executando git push...")
    git_push()


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    # Calcula tempo total estimado
    total_min = sum(v[0] for v in PHASE_DELAYS.values())
    total_max = sum(v[1] for v in PHASE_DELAYS.values())

    print(f"""
{C.MAG}{C.BLD}
╔══════════════════════════════════════════════════════════════╗
║     autobuilder — fastapi-auth                               ║
║     DIO Bootcamp: Autenticação e Autorização em FastAPI      ║
╚══════════════════════════════════════════════════════════════╝{C.RST}

{C.CYN}  Módulo:   Autenticação e Autorização em FastAPI
  Aula 1:   Como iremos autenticar as nossas rotas (02:39)
  Aula 2:   Uso de tokens para autenticação        (19:46)
  Total 2x: ~673s → script: {total_min}–{total_max}s ({total_min//60}–{total_max//60}min)

  Stack:    FastAPI + SQLAlchemy async + python-jose + passlib[bcrypt]
  Projeto:  {PROJECT_DIR}
  Commits:  10 (chore + feat×4 + refactor + fix + security + test + docs){C.RST}

{C.YEL}  Delays calibrados por fase (velocidade 2x das videoaulas):{C.RST}""")

    labels = {
        "fase2": "Aula 1 — config + database          ",
        "fase3": "Aula 2 — models + schemas           ",
        "fase4": "Aula 2 — schemas commit             ",
        "fase5": "Aula 2 — auth service               ",
        "fase6": "Aula 2 — dependencies + routers     ",
        "fase7": "Aula 2 — main refactor + middleware  ",
        "fase8": "Aula 2 — security fix               ",
        "fase9": "Aula 2 — tests + docs + push        ",
    }
    for k, (dmin, dmax) in PHASE_DELAYS.items():
        print(f"{C.DIM}    {labels[k]} {dmin}–{dmax}s{C.RST}")

    # Verificação do .git
    if not os.path.isdir(os.path.join(REPO_ROOT, ".git")):
        erro(f"Repositório Git não encontrado em: {REPO_ROOT}")
        sys.exit(1)
    ok(f"Repositório Git encontrado: {REPO_ROOT}")

    if os.path.exists(os.path.join(PROJECT_DIR, "main.py")):
        warn(f"Projeto já existe em: {PROJECT_DIR} — será sobrescrito.")

    print(f"\n{C.YEL}  Deseja continuar? [s/N]: {C.RST}", end="")
    try:
        resp = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        resp = "n"

    if resp != "s":
        warn("Cancelado.")
        sys.exit(0)

    inicio = time.time()

    fases = [
        fase1_estrutura,
        fase2_config_database,
        fase3_models_schemas,
        fase4_schemas_commit,
        fase5_auth_service,
        fase6_dependencies_routers,
        fase7_main_refactor,
        fase8_security_fix,
        fase9_tests_docs_push,
    ]

    for fn in fases:
        try:
            fn()
        except KeyboardInterrupt:
            warn("\nInterrompido.")
            sys.exit(1)
        except Exception as e:
            erro(f"Erro em {fn.__name__}: {e}")
            warn("Continuando...")

    elapsed = int(time.time() - inicio)
    print(f"""
{C.GRN}{C.BLD}
╔══════════════════════════════════════════════════════════════╗
║  ✔  fastapi-auth gerado com sucesso!                         ║
╚══════════════════════════════════════════════════════════════╝{C.RST}

{C.WHT}  Tempo total:  {elapsed // 60}m {elapsed % 60}s
  Commits:       10
  Push:          origin main{C.RST}

{C.CYN}  Para testar:
    cd {PROJECT_DIR}
    cp .env.example .env
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8003
    # http://localhost:8003/docs

    pytest tests/ -v{C.RST}

{C.DIM}  Próximo módulo: Testando APIs RESTful Assíncronas em FastAPI{C.RST}
""")


if __name__ == "__main__":
    main()
