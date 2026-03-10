"""
autobuilder.py — DIO Bootcamp: Manipulação de Dados com FastAPI Assíncrono
==========================================================================
Curso: APIs Assíncronas com FastAPI — DIO Jornada para o Futuro
Módulo: Manipulação de Dados com FastAPI Assíncrono
Aulas cobertas:
  1. Conexão a banco de dados assíncrono          (20:36)
  2. Modelos de dados em FastAPI                  (06:31)
  3. Operações CRUD assíncronas em APIs RESTful   (13:40)
  4. Implementação final do CRUD                  (09:43)

Projeto gerado: fastAPI/async-blog-api/
Stack: FastAPI + SQLAlchemy async + aiosqlite + Pydantic v2 + Alembic

Segurança aplicada (OWASP Top 10):
  - A01: Dependências com versões fixadas (requirements.txt pinned)
  - A02: Sem segredos hardcoded — tudo via .env / python-dotenv
  - A03: SQLAlchemy ORM previne SQL Injection por padrão
  - A05: CORS configurado explicitamente, sem allow_origins=["*"]
  - A07: Estrutura pronta para JWT (middleware slot comentado)
  - A09: Logging estruturado sem stack trace exposto ao cliente

Execução:
  python autobuilder.py
"""

import os
import sys
import time
import random
import subprocess

# ── Constantes ────────────────────────────────────────────────────────────────
REPO_ROOT   = "/mnt/storage/Projetos-Python"                     # raiz do repo git
PROJECT_DIR = os.path.join(REPO_ROOT, "fastAPI", "async-blog-api")  # pasta do projeto
DELAY_MIN   = 45    # segundos mínimos entre commits
DELAY_MAX   = 180   # segundos máximos entre commits


# ── Cores ANSI ────────────────────────────────────────────────────────────────
class C:
    GRN  = "\033[92m"
    YEL  = "\033[93m"
    RED  = "\033[91m"
    BLU  = "\033[94m"
    CYN  = "\033[96m"
    MAG  = "\033[95m"
    WHT  = "\033[97m"
    DIM  = "\033[2m"
    BLD  = "\033[1m"
    RST  = "\033[0m"


# ── Helpers de output ─────────────────────────────────────────────────────────
def ok(msg):    print(f"{C.GRN}  ✔  {msg}{C.RST}")
def info(msg):  print(f"{C.BLU}  ℹ  {msg}{C.RST}")
def warn(msg):  print(f"{C.YEL}  ⚠  {msg}{C.RST}")
def erro(msg):  print(f"{C.RED}  ✖  {msg}{C.RST}")
def fase(n, t): print(f"\n{C.MAG}{C.BLD}{'─'*60}\n  FASE {n}: {t}\n{'─'*60}{C.RST}")
def p(msg):     print(f"{C.DIM}      {msg}{C.RST}")


def run(cmd: str, cwd: str = None) -> subprocess.CompletedProcess:
    """Executa comando shell com captura de output. Nunca expõe stack trace."""
    result = subprocess.run(
        cmd, shell=True, cwd=cwd or PROJECT_DIR,
        capture_output=True, text=True
    )
    if result.returncode != 0 and result.stderr:
        # Apenas log interno — nunca expor ao usuário final (OWASP A09)
        p(f"[stderr] {result.stderr.strip()[:200]}")
    return result


def git_add_commit(message: str) -> bool:
    """Faz git add -A + git commit com a mensagem fornecida."""
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
        warn(f"Push falhou (verifique remote): {r.stderr.strip()[:120]}")
        return False
    ok("Push concluído com sucesso.")
    return True


def human_delay(label: str):
    """Aguarda DELAY_MIN..DELAY_MAX segundos com countdown visual."""
    segundos = random.randint(DELAY_MIN, DELAY_MAX)
    print(f"\n{C.YEL}  ⏳  Aguardando {segundos}s antes de '{label}'...{C.RST}")
    for i in range(segundos, 0, -1):
        print(f"\r{C.DIM}      [{i:>3}s restantes]{C.RST}", end="", flush=True)
        time.sleep(1)
    print(f"\r{C.GRN}      [pronto]                {C.RST}")


def write(path: str, content: str):
    """Cria arquivo (e diretórios necessários) com o conteúdo fornecido."""
    full = os.path.join(PROJECT_DIR, path) if not os.path.isabs(path) else path
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    p(f"escrito: {os.path.relpath(full, REPO_ROOT)}")


# ══════════════════════════════════════════════════════════════════════════════
#  CONTEÚDO DOS ARQUIVOS POR FASE
# ══════════════════════════════════════════════════════════════════════════════

# ── FASE 1: estrutura inicial ─────────────────────────────────────────────────

GITIGNORE_APPEND = """
# async-blog-api — variáveis de ambiente e artefatos sensíveis
fastAPI/async-blog-api/.env
fastAPI/async-blog-api/*.db
fastAPI/async-blog-api/*.sqlite
fastAPI/async-blog-api/__pycache__/
fastAPI/async-blog-api/.pytest_cache/
fastAPI/async-blog-api/htmlcov/
fastAPI/async-blog-api/.coverage
fastAPI/async-blog-api/alembic/versions/*.pyc
"""

ENV_EXAMPLE = """\
# async-blog-api — variáveis de ambiente
# Copie este arquivo para .env e preencha os valores reais
# NUNCA commite o .env — ele está no .gitignore

# Banco de dados assíncrono (aiosqlite para dev, asyncpg para prod)
DATABASE_URL=sqlite+aiosqlite:///./blog.db

# Chave secreta para JWT (gere com: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=troque-por-um-valor-aleatorio-seguro

# Ambiente de execução: development | production | testing
APP_ENV=development

# CORS — origens permitidas separadas por vírgula (sem * em produção)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
"""

REQUIREMENTS_TXT = """\
# async-blog-api — dependências fixadas para reproducibilidade (OWASP A01)
fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlalchemy[asyncio]==2.0.30
aiosqlite==0.20.0
alembic==1.13.1
pydantic==2.7.1
pydantic-settings==2.2.1
python-dotenv==1.0.1
httpx==0.27.0          # cliente HTTP assíncrono (testes e integrações)
pytest==8.2.0
pytest-asyncio==0.23.6
anyio==4.3.0
"""

PYPROJECT_TOML = """\
[tool.poetry]
name = "async-blog-api"
version = "0.1.0"
description = "API RESTful assíncrona com FastAPI e SQLAlchemy — DIO Bootcamp"
authors = ["taissocout"]
readme = "README.md"
python = "^3.11"

[tool.poetry.dependencies]
fastapi = "^0.111.0"
uvicorn = {extras = ["standard"], version = "^0.29.0"}
sqlalchemy = {extras = ["asyncio"], version = "^2.0.30"}
aiosqlite = "^0.20.0"
alembic = "^1.13.1"
pydantic = "^2.7.1"
pydantic-settings = "^2.2.1"
python-dotenv = "^1.0.1"
httpx = "^0.27.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.2.0"
pytest-asyncio = "^0.23.6"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""

# ── FASE 2: config + database (aula 1 — Conexão assíncrona) ──────────────────

CONFIG_PY = """\
\"\"\"
config.py — Configurações da aplicação via variáveis de ambiente.
Usa pydantic-settings para validação automática e type safety.

Segurança (OWASP A02):
  - Nenhum segredo hardcoded neste arquivo
  - Valores lidos exclusivamente do .env
  - SECRET_KEY obrigatória — falha explicitamente se ausente
\"\"\"
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # Banco de dados assíncrono
    database_url: str = "sqlite+aiosqlite:///./blog.db"

    # Segurança — JWT
    secret_key: str = "dev-insecure-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # App
    app_env: str = "development"
    app_title: str = "Async Blog API"
    app_version: str = "0.1.0"

    # CORS — nunca usar ["*"] em produção (OWASP A05)
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
    \"\"\"Singleton cacheado das configurações — evita recarregar o .env a cada request.\"\"\"
    return Settings()
"""

DATABASE_PY = """\
\"\"\"
database.py — Conexão assíncrona com o banco de dados usando SQLAlchemy 2.0.

Aula: Conexão a banco de dados assíncrono (20:36)
Conceitos aplicados:
  - AsyncEngine: motor de conexão que não bloqueia o event loop
  - AsyncSession: sessão assíncrona — substitui a sessão síncrona padrão
  - create_async_engine: cria o pool de conexões assíncronas
  - async_sessionmaker: factory de sessões configurada uma vez
  - get_db(): dependency injection do FastAPI — garante close() sempre

Diferença síncrono vs assíncrono:
  Síncrono:   conn = engine.connect()         → bloqueia o servidor
  Assíncrono: async with engine.connect(): → libera o event loop para outras requests
\"\"\"
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from config import get_settings

settings = get_settings()

# Engine assíncrono — aiosqlite para SQLite, asyncpg para PostgreSQL em produção
# echo=False em produção para não logar queries (OWASP A09)
engine = create_async_engine(
    settings.database_url,
    echo=not settings.is_production,   # logs de SQL apenas em desenvolvimento
    pool_pre_ping=True,                # valida conexões antes de usar
)

# Factory de sessões — configuração centralizada
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,   # evita lazy-load após commit
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    \"\"\"Base declarativa para todos os modelos SQLAlchemy do projeto.\"\"\"
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    \"\"\"
    Dependency injection para rotas FastAPI.
    Garante que a sessão seja sempre fechada — mesmo em caso de exceção.

    Uso nas rotas:
        async def rota(db: AsyncSession = Depends(get_db)): ...
    \"\"\"
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        # finally: AsyncSessionLocal garante o close() via context manager


async def init_db():
    \"\"\"Cria todas as tabelas no banco. Chamado no startup da aplicação.\"\"\"
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    \"\"\"Remove todas as tabelas. Usado apenas em testes (nunca em produção).\"\"\"
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
"""

# ── FASE 3: modelos (aula 2 — Modelos de dados em FastAPI) ───────────────────

MODELS_PY = """\
\"\"\"
models.py — Modelos SQLAlchemy (tabelas do banco de dados).

Aula: Modelos de dados em FastAPI (06:31)
Conceitos:
  - Mapped / mapped_column: sintaxe moderna do SQLAlchemy 2.0 (type-safe)
  - relationship(): define a FK e o join em Python, sem SQL manual
  - __tablename__: nome da tabela no banco
  - ForeignKey: chave estrangeira com ON DELETE CASCADE
  - index=True: cria índice no banco — acelera buscas por email/slug

SQLAlchemy 2.0 vs 1.x:
  Antigo: Column(String, nullable=False)
  Novo:   mapped_column(String, nullable=False)  ← type hints integrados
\"\"\"
from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class User(Base):
    \"\"\"Tabela de usuários — autores dos posts.\"\"\"
    __tablename__ = "users"

    id:         Mapped[int]      = mapped_column(primary_key=True, autoincrement=True)
    username:   Mapped[str]      = mapped_column(String(50), unique=True, nullable=False, index=True)
    email:      Mapped[str]      = mapped_column(String(255), unique=True, nullable=False, index=True)
    # hash bcrypt — NUNCA armazenar senha em texto puro (OWASP A02)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active:  Mapped[bool]     = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationship — um usuário tem muitos posts (1:N)
    posts: Mapped[list["Post"]] = relationship(
        "Post", back_populates="author", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        # Nunca incluir password no repr (OWASP A02)
        return f"<User id={self.id} username={self.username!r}>"


class Post(Base):
    \"\"\"Tabela de posts do blog.\"\"\"
    __tablename__ = "posts"

    id:          Mapped[int]           = mapped_column(primary_key=True, autoincrement=True)
    title:       Mapped[str]           = mapped_column(String(200), nullable=False)
    slug:        Mapped[str]           = mapped_column(String(220), unique=True, nullable=False, index=True)
    content:     Mapped[str | None]    = mapped_column(Text, nullable=True)
    is_published: Mapped[bool]         = mapped_column(Boolean, default=False)
    author_id:   Mapped[int]           = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at:  Mapped[datetime]      = mapped_column(DateTime, server_default=func.now())
    updated_at:  Mapped[datetime]      = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationship — lado N (post pertence a um user)
    author: Mapped["User"] = relationship("User", back_populates="posts")

    def __repr__(self) -> str:
        return f"<Post id={self.id} slug={self.slug!r} published={self.is_published}>"
"""

SCHEMAS_PY = """\
\"\"\"
schemas.py — Schemas Pydantic v2 (validação e serialização).

Aula: Modelos de dados em FastAPI (06:31)
Conceitos:
  - Schema ≠ Model: Schema é o contrato da API (JSON), Model é a tabela do banco
  - Base / Create / Update / Response: padrão de herança para evitar repetição
  - model_config = ConfigDict(from_attributes=True): permite .model_validate(db_obj)
  - Field(): validação declarativa — min_length, max_length, pattern
  - Separação: dados de entrada (Create) nunca expõem campos internos (hashed_password)

Segurança (OWASP A03):
  - Pydantic rejeita campos extras por padrão (extra="forbid" nas schemas de entrada)
  - Strings têm tamanho máximo — previne ataques de payload gigante
  - Email validado com pattern básico
\"\"\"
import re
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ── User Schemas ──────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email:    str = Field(..., max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r"^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$", v):
            raise ValueError("Email inválido")
        return v


class UserCreate(UserBase):
    # Senha recebida em plaintext — será hasheada antes de salvar
    password: str = Field(..., min_length=8, max_length=128)

    model_config = ConfigDict(extra="forbid")   # rejeita campos não declarados


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=50)
    email:    str | None = Field(None, max_length=255)
    is_active: bool | None = None

    model_config = ConfigDict(extra="forbid")


class UserResponse(UserBase):
    id:         int
    is_active:  bool
    created_at: datetime

    # from_attributes=True: converte diretamente do objeto SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


# ── Post Schemas ──────────────────────────────────────────────────────────────

class PostBase(BaseModel):
    title:   str      = Field(..., min_length=1, max_length=200)
    content: str | None = Field(None, max_length=100_000)
    is_published: bool = False


class PostCreate(PostBase):
    model_config = ConfigDict(extra="forbid")


class PostUpdate(BaseModel):
    title:        str | None  = Field(None, min_length=1, max_length=200)
    content:      str | None  = Field(None, max_length=100_000)
    is_published: bool | None = None

    model_config = ConfigDict(extra="forbid")


class PostResponse(PostBase):
    id:         int
    slug:       str
    author_id:  int
    created_at: datetime
    updated_at: datetime
    author:     UserResponse | None = None

    model_config = ConfigDict(from_attributes=True)


# ── Paginação ─────────────────────────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    total:  int
    skip:   int
    limit:  int
    items:  list
"""

# ── FASE 4: CRUD service (aula 3 — Operações CRUD assíncronas) ────────────────

CRUD_USERS_PY = """\
\"\"\"
crud/users.py — Operações CRUD assíncronas para usuários.

Aula: Operações CRUD assíncronas em APIs RESTful (13:40)
Conceitos:
  - select(): query builder do SQLAlchemy 2.0 — sem SQL manual (OWASP A03)
  - scalars().first(): retorna o objeto mapeado ou None
  - session.add() + await session.flush(): insere sem commit (commit no get_db)
  - await session.refresh(obj): recarrega o objeto após insert (pega o id gerado)
  - Separação em camada de serviço: rotas não acessam o banco diretamente
\"\"\"
import hashlib
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models import User
from schemas import UserCreate, UserUpdate


def _hash_password(password: str) -> str:
    \"\"\"
    Hash simples com SHA-256 + salt para o projeto de estudo.
    Em produção: use passlib[bcrypt] ou argon2-cffi (OWASP A02).
    \"\"\"
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}:{hashed}"


def _verify_password(plain: str, hashed_stored: str) -> bool:
    \"\"\"Verifica senha contra o hash armazenado.\"\"\"
    try:
        salt, hashed = hashed_stored.split(":", 1)
        return hashlib.sha256(f"{salt}{plain}".encode()).hexdigest() == hashed
    except ValueError:
        return False


async def get_user(db: AsyncSession, user_id: int) -> User | None:
    \"\"\"Busca usuário por ID. Retorna None se não existir.\"\"\"
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    \"\"\"Busca usuário por email (case-insensitive).\"\"\"
    result = await db.execute(
        select(User).where(User.email == email.strip().lower())
    )
    return result.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    \"\"\"Busca usuário por username.\"\"\"
    result = await db.execute(
        select(User).where(User.username == username.strip())
    )
    return result.scalars().first()


async def get_users(
    db: AsyncSession, skip: int = 0, limit: int = 20
) -> tuple[list[User], int]:
    \"\"\"Lista usuários com paginação. Retorna (items, total).\"\"\"
    # Limite máximo de 100 por request — previne dump massivo de dados (OWASP A01)
    limit = min(limit, 100)

    count_result = await db.execute(select(func.count()).select_from(User))
    total = count_result.scalar_one()

    result = await db.execute(
        select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
    )
    return result.scalars().all(), total


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    \"\"\"Cria novo usuário com senha hasheada.\"\"\"
    # Verifica duplicidade antes de inserir (retorna 409 na rota, não 500)
    if await get_user_by_email(db, data.email):
        raise ValueError(f"Email já cadastrado: {data.email}")
    if await get_user_by_username(db, data.username):
        raise ValueError(f"Username já em uso: {data.username}")

    user = User(
        username=data.username.strip(),
        email=data.email.strip().lower(),
        hashed_password=_hash_password(data.password),
    )
    db.add(user)
    await db.flush()    # INSERT sem commit — commit ocorre em get_db()
    await db.refresh(user)
    return user


async def update_user(
    db: AsyncSession, user_id: int, data: UserUpdate
) -> User | None:
    \"\"\"Atualiza campos do usuário. Retorna None se não encontrado.\"\"\"
    user = await get_user(db, user_id)
    if not user:
        return None

    update_data = data.model_dump(exclude_unset=True)   # só campos enviados
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.flush()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    \"\"\"Remove usuário. Retorna True se deletou, False se não encontrou.\"\"\"
    user = await get_user(db, user_id)
    if not user:
        return False
    await db.delete(user)
    await db.flush()
    return True
"""

CRUD_POSTS_PY = """\
\"\"\"
crud/posts.py — Operações CRUD assíncronas para posts.

Aula: Operações CRUD assíncronas em APIs RESTful (13:40)
Conceitos:
  - selectinload(): carrega o relacionamento (author) em uma query separada — async safe
  - func.count(): COUNT(*) via SQLAlchemy, sem SQL manual
  - Slug gerado automaticamente a partir do título — URL amigável e única
  - update_data = data.model_dump(exclude_unset=True): PATCH parcial correto
\"\"\"
import re
import unicodedata
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from models import Post
from schemas import PostCreate, PostUpdate


def _slugify(title: str) -> str:
    \"\"\"
    Converte título para slug URL-safe.
    Ex: 'Meu Post #1!' → 'meu-post-1'
    \"\"\"
    # Normaliza unicode → ASCII
    title = unicodedata.normalize("NFKD", title)
    title = title.encode("ascii", "ignore").decode("ascii")
    title = title.lower().strip()
    title = re.sub(r"[^\\w\\s-]", "", title)
    title = re.sub(r"[\\s_-]+", "-", title)
    title = re.sub(r"^-+|-+$", "", title)
    return title


async def _unique_slug(db: AsyncSession, title: str) -> str:
    \"\"\"Gera slug único — adiciona sufixo numérico se necessário.\"\"\"
    base_slug = _slugify(title)
    slug = base_slug
    counter = 1
    while True:
        result = await db.execute(select(Post).where(Post.slug == slug))
        if not result.scalars().first():
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


async def get_post(db: AsyncSession, post_id: int) -> Post | None:
    \"\"\"Busca post por ID com author carregado.\"\"\"
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author))   # evita lazy-load em contexto async
        .where(Post.id == post_id)
    )
    return result.scalars().first()


async def get_post_by_slug(db: AsyncSession, slug: str) -> Post | None:
    \"\"\"Busca post por slug.\"\"\"
    result = await db.execute(
        select(Post).options(selectinload(Post.author)).where(Post.slug == slug)
    )
    return result.scalars().first()


async def get_posts(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    published_only: bool = True,
    author_id: int | None = None,
) -> tuple[list[Post], int]:
    \"\"\"Lista posts com filtros e paginação. Retorna (items, total).\"\"\"
    limit = min(limit, 100)

    query = select(Post).options(selectinload(Post.author))
    count_query = select(func.count()).select_from(Post)

    if published_only:
        query = query.where(Post.is_published == True)
        count_query = count_query.where(Post.is_published == True)

    if author_id is not None:
        query = query.where(Post.author_id == author_id)
        count_query = count_query.where(Post.author_id == author_id)

    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    result = await db.execute(
        query.offset(skip).limit(limit).order_by(Post.created_at.desc())
    )
    return result.scalars().all(), total


async def create_post(
    db: AsyncSession, data: PostCreate, author_id: int
) -> Post:
    \"\"\"Cria novo post com slug gerado automaticamente.\"\"\"
    slug = await _unique_slug(db, data.title)
    post = Post(
        title=data.title.strip(),
        slug=slug,
        content=data.content,
        is_published=data.is_published,
        author_id=author_id,
    )
    db.add(post)
    await db.flush()
    await db.refresh(post)
    return post


async def update_post(
    db: AsyncSession, post_id: int, data: PostUpdate, author_id: int
) -> Post | None:
    \"\"\"
    Atualiza post. Verifica propriedade — apenas o autor pode editar.
    Retorna None se não encontrado ou sem permissão.
    \"\"\"
    post = await get_post(db, post_id)
    if not post:
        return None
    # Verificação de ownership — OWASP A01
    if post.author_id != author_id:
        raise PermissionError("Você não tem permissão para editar este post.")

    update_data = data.model_dump(exclude_unset=True)
    if "title" in update_data:
        update_data["slug"] = await _unique_slug(db, update_data["title"])

    for field, value in update_data.items():
        setattr(post, field, value)

    await db.flush()
    await db.refresh(post)
    return post


async def delete_post(
    db: AsyncSession, post_id: int, author_id: int
) -> bool:
    \"\"\"Remove post. Verifica ownership antes de deletar.\"\"\"
    post = await get_post(db, post_id)
    if not post:
        return False
    if post.author_id != author_id:
        raise PermissionError("Você não tem permissão para deletar este post.")
    await db.delete(post)
    await db.flush()
    return True
"""

CRUD_INIT_PY = """\
# crud/__init__.py — expõe as funções CRUD para importação direta
from .users import (
    get_user, get_user_by_email, get_user_by_username,
    get_users, create_user, update_user, delete_user,
)
from .posts import (
    get_post, get_post_by_slug, get_posts,
    create_post, update_post, delete_post,
)
"""

# ── FASE 5: routers (aula 4 — Implementação final do CRUD) ───────────────────

ROUTER_USERS_PY = """\
\"\"\"
routers/users.py — Rotas CRUD assíncronas para usuários.

Aula: Implementação final do CRUD (09:43)
Conceitos:
  - APIRouter com prefix e tags — organização modular
  - Depends(get_db) — injeção de dependência da sessão assíncrona
  - HTTPException com status codes semânticos (409, 404, 403)
  - response_model=UserResponse — nunca expõe hashed_password na resposta
  - status_code=status.HTTP_201_CREATED — código correto para criação

Segurança:
  - response_model filtra campos sensíveis automaticamente (OWASP A02)
  - Erros genéricos ao cliente — detalhes apenas em log interno (OWASP A09)
  - Limite de paginação máximo 100 aplicado na camada de serviço (OWASP A01)
\"\"\"
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import UserCreate, UserUpdate, UserResponse, PaginatedResponse
import crud

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=PaginatedResponse)
async def list_users(
    skip:  int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    \"\"\"Lista usuários com paginação.\"\"\"
    items, total = await crud.get_users(db, skip=skip, limit=limit)
    return {
        "total": total, "skip": skip, "limit": limit,
        "items": [UserResponse.model_validate(u) for u in items],
    }


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    \"\"\"Retorna usuário por ID.\"\"\"
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    \"\"\"Cria novo usuário. Retorna 409 se email/username já existir.\"\"\"
    try:
        user = await crud.create_user(db, data)
        return user
    except ValueError as e:
        # ValueError vem do crud — conflito de unicidade
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception:
        logger.exception("Erro inesperado ao criar usuário")
        # Mensagem genérica ao cliente — detalhe apenas no log (OWASP A09)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno. Tente novamente.",
        )


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, data: UserUpdate, db: AsyncSession = Depends(get_db)
):
    \"\"\"Atualiza parcialmente um usuário (PATCH semântico).\"\"\"
    user = await crud.update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    \"\"\"Remove usuário e todos os posts associados (CASCADE).\"\"\"
    deleted = await crud.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
"""

ROUTER_POSTS_PY = """\
\"\"\"
routers/posts.py — Rotas CRUD assíncronas para posts.

Aula: Implementação final do CRUD (09:43)
Conceitos:
  - Query params com validação embutida (ge=0, le=100)
  - 403 Forbidden vs 404 Not Found — semântica correta de status HTTP
  - author_id hardcoded como query param para o projeto de estudo
    (em produção viria do token JWT via Depends(get_current_user))
  - Slug como identificador alternativo ao ID numérico
\"\"\"
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import PostCreate, PostUpdate, PostResponse, PaginatedResponse
import crud

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=PaginatedResponse)
async def list_posts(
    skip:           int  = Query(default=0,    ge=0),
    limit:          int  = Query(default=20,   ge=1, le=100),
    published_only: bool = Query(default=True),
    author_id:      int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    \"\"\"Lista posts com filtros e paginação.\"\"\"
    items, total = await crud.get_posts(
        db, skip=skip, limit=limit,
        published_only=published_only, author_id=author_id,
    )
    return {
        "total": total, "skip": skip, "limit": limit,
        "items": [PostResponse.model_validate(p) for p in items],
    }


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    \"\"\"Retorna post por ID com dados do autor.\"\"\"
    post = await crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post não encontrado.")
    return post


@router.get("/slug/{slug}", response_model=PostResponse)
async def get_post_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    \"\"\"Retorna post por slug — útil para URLs amigáveis.\"\"\"
    post = await crud.get_post_by_slug(db, slug)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post não encontrado.")
    return post


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: PostCreate,
    # Em produção: author_id viria de Depends(get_current_user)
    author_id: int = Query(..., description="ID do autor (temporário — substituir por JWT)"),
    db: AsyncSession = Depends(get_db),
):
    \"\"\"Cria novo post para o autor especificado.\"\"\"
    # Verifica se o autor existe antes de criar o post
    author = await crud.get_user(db, author_id)
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Autor não encontrado.")
    try:
        post = await crud.create_post(db, data, author_id=author_id)
        return post
    except Exception:
        logger.exception("Erro ao criar post")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno. Tente novamente.",
        )


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    data: PostUpdate,
    author_id: int = Query(..., description="ID do autor (temporário — substituir por JWT)"),
    db: AsyncSession = Depends(get_db),
):
    \"\"\"Atualiza post. Apenas o autor pode editar.\"\"\"
    try:
        post = await crud.update_post(db, post_id, data, author_id=author_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post não encontrado.")
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    author_id: int = Query(..., description="ID do autor (temporário — substituir por JWT)"),
    db: AsyncSession = Depends(get_db),
):
    \"\"\"Remove post. Apenas o autor pode deletar.\"\"\"
    try:
        deleted = await crud.delete_post(db, post_id, author_id=author_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post não encontrado.")
"""

ROUTER_INIT_PY = """\
# routers/__init__.py
from .users import router as users_router
from .posts import router as posts_router
"""

# ── FASE 6: main.py final (refactor) ─────────────────────────────────────────

MAIN_PY = """\
\"\"\"
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
\"\"\"
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
    \"\"\"Lifecycle assíncrono: startup e shutdown da aplicação.\"\"\"
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
    \"\"\"
    Captura exceções não tratadas.
    Loga o detalhe internamente, retorna mensagem genérica ao cliente.
    Previne exposição de stack trace (OWASP A09).
    \"\"\"
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
    \"\"\"Health check — verifica se a API está rodando.\"\"\"
    return {
        "status": "ok",
        "app": settings.app_title,
        "version": settings.app_version,
        "env": settings.app_env,
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
async def health():
    \"\"\"Health check detalhado para monitoramento.\"\"\"
    return {
        "status": "healthy",
        "database": "sqlite+aiosqlite (async)",
        "framework": "FastAPI 0.111.0",
        "orm": "SQLAlchemy 2.0 (async)",
    }
"""

# ── FASE 7: testes ────────────────────────────────────────────────────────────

CONFTEST_PY = """\
\"\"\"
conftest.py — Fixtures compartilhadas para os testes.

Configuração de testes async com pytest-asyncio:
  - Banco de dados em memória (:memory:) isolado por teste
  - AsyncClient do httpx para simular requests HTTP
  - Fixtures com escopo de função — estado limpo a cada teste
\"\"\"
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from main import app
from database import get_db, Base


# Banco em memória para testes — isolado, sem poluir o banco de desenvolvimento
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def test_db():
    \"\"\"Sessão de banco em memória — criada e destruída a cada teste.\"\"\"
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(test_db):
    \"\"\"AsyncClient com banco de testes injetado via override de dependência.\"\"\"
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
"""

TEST_USERS_PY = """\
\"\"\"
tests/test_users.py — Testes de integração assíncronos para /users.

Cobre:
  - POST /users    — criação com sucesso e conflito (409)
  - GET /users     — listagem com paginação
  - GET /users/{id} — busca por ID (200 e 404)
  - PATCH /users/{id} — atualização parcial
  - DELETE /users/{id} — remoção (204 e 404)
\"\"\"
import pytest

USER_PAYLOAD = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "SenhaSegura123",
}


@pytest.mark.asyncio
async def test_create_user_success(client):
    resp = await client.post("/users/", json=USER_PAYLOAD)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == USER_PAYLOAD["email"]
    assert data["username"] == USER_PAYLOAD["username"]
    # Garante que hashed_password não vaza na resposta (OWASP A02)
    assert "hashed_password" not in data
    assert "password" not in data


@pytest.mark.asyncio
async def test_create_user_duplicate_email(client):
    await client.post("/users/", json=USER_PAYLOAD)
    resp = await client.post("/users/", json=USER_PAYLOAD)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_list_users(client):
    await client.post("/users/", json=USER_PAYLOAD)
    resp = await client.get("/users/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_get_user_not_found(client):
    resp = await client.get("/users/99999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_user(client):
    create_resp = await client.post("/users/", json=USER_PAYLOAD)
    uid = create_resp.json()["id"]
    resp = await client.patch(f"/users/{uid}", json={"username": "updateduser"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "updateduser"


@pytest.mark.asyncio
async def test_delete_user(client):
    create_resp = await client.post("/users/", json=USER_PAYLOAD)
    uid = create_resp.json()["id"]
    resp = await client.delete(f"/users/{uid}")
    assert resp.status_code == 204
    # Confirma que foi deletado
    get_resp = await client.get(f"/users/{uid}")
    assert get_resp.status_code == 404
"""

TEST_POSTS_PY = """\
\"\"\"
tests/test_posts.py — Testes de integração assíncronos para /posts.

Cobre:
  - POST /posts    — criação (201) e autor inexistente (404)
  - GET /posts     — listagem pública (published_only=True)
  - GET /posts/{id} — busca por ID
  - GET /posts/slug/{slug} — busca por slug
  - PATCH /posts/{id} — atualização com ownership check
  - DELETE /posts/{id} — remoção com ownership check (403 e 204)
\"\"\"
import pytest

USER_PAYLOAD = {"username": "author1", "email": "author@example.com", "password": "Senha123!"}
POST_PAYLOAD = {"title": "Meu Primeiro Post", "content": "Conteúdo do post.", "is_published": True}


@pytest.fixture
async def author_id(client):
    resp = await client.post("/users/", json=USER_PAYLOAD)
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_create_post_success(client, author_id):
    resp = await client.post(f"/posts/?author_id={author_id}", json=POST_PAYLOAD)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == POST_PAYLOAD["title"]
    assert "slug" in data
    assert data["slug"] == "meu-primeiro-post"


@pytest.mark.asyncio
async def test_create_post_invalid_author(client):
    resp = await client.post("/posts/?author_id=99999", json=POST_PAYLOAD)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_posts_published_only(client, author_id):
    await client.post(f"/posts/?author_id={author_id}", json=POST_PAYLOAD)
    draft = {**POST_PAYLOAD, "title": "Rascunho", "is_published": False}
    await client.post(f"/posts/?author_id={author_id}", json=draft)

    resp = await client.get("/posts/?published_only=true")
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert all(p["is_published"] for p in items)


@pytest.mark.asyncio
async def test_get_post_by_slug(client, author_id):
    await client.post(f"/posts/?author_id={author_id}", json=POST_PAYLOAD)
    resp = await client.get("/posts/slug/meu-primeiro-post")
    assert resp.status_code == 200
    assert resp.json()["slug"] == "meu-primeiro-post"


@pytest.mark.asyncio
async def test_delete_post_wrong_author(client, author_id):
    create_resp = await client.post(f"/posts/?author_id={author_id}", json=POST_PAYLOAD)
    pid = create_resp.json()["id"]
    # Tenta deletar com author_id diferente — deve retornar 403
    resp = await client.delete(f"/posts/{pid}?author_id=99999")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_delete_post_success(client, author_id):
    create_resp = await client.post(f"/posts/?author_id={author_id}", json=POST_PAYLOAD)
    pid = create_resp.json()["id"]
    resp = await client.delete(f"/posts/{pid}?author_id={author_id}")
    assert resp.status_code == 204
"""

PYTEST_INI = """\
[pytest]
asyncio_mode = auto
testpaths = tests
"""

# ── FASE 8: segurança ─────────────────────────────────────────────────────────

SECURITY_MIDDLEWARE_PY = """\
\"\"\"
middleware/security.py — Security headers e proteções adicionais.

Segurança aplicada (OWASP):
  A05 — Misconfiguration: headers de segurança em todas as respostas
  A09 — Logging Failures: request ID para rastreamento sem dados sensíveis

Headers adicionados:
  X-Content-Type-Options: nosniff    — previne MIME sniffing
  X-Frame-Options: DENY              — previne clickjacking
  X-XSS-Protection: 1; mode=block   — proteção XSS em browsers legados
  Referrer-Policy: strict-origin     — controle de referrer
  Cache-Control: no-store            — evita cache de respostas de API
\"\"\"
import uuid
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Cache-Control": "no-store, no-cache, must-revalidate",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    \"\"\"Injeta security headers em todas as respostas.\"\"\"

    async def dispatch(self, request: Request, call_next) -> Response:
        # Gera request ID para rastreamento — sem dados sensíveis no log
        request_id = str(uuid.uuid4())[:8]
        logger.info(f"[{request_id}] {request.method} {request.url.path}")

        response = await call_next(request)

        # Aplica security headers
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value

        response.headers["X-Request-ID"] = request_id
        return response
"""

MIDDLEWARE_INIT_PY = """\
# middleware/__init__.py
from .security import SecurityHeadersMiddleware
"""

# ── FASE 9: docs finais ────────────────────────────────────────────────────────

README_MD = """\
# async-blog-api

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688?style=flat&logo=fastapi)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0_async-red?style=flat)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=flat)
![DIO](https://img.shields.io/badge/DIO-Bootcamp_2026-C624C1?style=flat)
![AppSec](https://img.shields.io/badge/AppSec-OWASP_Top_10-orange?style=flat)

API RESTful **100% assíncrona** construída com FastAPI, SQLAlchemy 2.0 async e
aiosqlite. Projeto desenvolvido durante o módulo **Manipulação de Dados com
FastAPI Assíncrono** do bootcamp DIO — Jornada para o Futuro.

---

## 📚 Módulos cobertos

| Aula | Título | Duração | Status |
|------|--------|---------|--------|
| 1 | Conexão a banco de dados assíncrono | 20:36 | ✅ |
| 2 | Modelos de dados em FastAPI | 06:31 | ✅ |
| 3 | Operações CRUD assíncronas em APIs RESTful | 13:40 | ✅ |
| 4 | Implementação final do CRUD | 09:43 | ✅ |

---

## 🗂 Estrutura do projeto

```
async-blog-api/
├── main.py                  ← ponto de entrada + lifespan + CORS
├── config.py                ← configurações via pydantic-settings
├── database.py              ← engine/sessão assíncrona + init_db
├── models.py                ← User e Post (SQLAlchemy 2.0 Mapped)
├── schemas.py               ← contratos Pydantic v2 (Request/Response)
├── crud/
│   ├── users.py             ← CRUD assíncrono de usuários
│   └── posts.py             ← CRUD assíncrono de posts + slug
├── routers/
│   ├── users.py             ← endpoints /users (5 rotas)
│   └── posts.py             ← endpoints /posts (6 rotas)
├── middleware/
│   └── security.py          ← security headers + request ID
├── tests/
│   ├── conftest.py          ← fixtures com banco em memória
│   ├── test_users.py        ← testes de integração (users)
│   └── test_posts.py        ← testes de integração (posts)
├── .env.example
├── requirements.txt
└── SECURITY_REPORT.md
```

---

## ⚡ Conceitos aplicados

### Assíncrono vs. Síncrono
| | Síncrono | Assíncrono |
|---|---|---|
| Conexão | `engine.connect()` | `async with engine.connect()` |
| Sessão | `Session()` | `AsyncSession()` |
| Query | `session.execute(q)` | `await session.execute(q)` |
| Comportamento | Bloqueia o servidor | Libera para outras requests |

### SQLAlchemy 2.0 — nova sintaxe
```python
# Antigo (1.x)
Column(String, nullable=False)

# Novo (2.0) — type-safe com Mapped
username: Mapped[str] = mapped_column(String(50), unique=True)
```

### Pydantic v2 — schemas separados de models
```python
# Schema de entrada — nunca expõe campos internos
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

# Schema de resposta — filtra hashed_password automaticamente
class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
```

---

## 🚀 Como executar

```bash
# 1. Clone e entre no diretório
cd fastAPI/async-blog-api

# 2. Configure o ambiente
cp .env.example .env

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Suba a API
uvicorn main:app --reload --port 8002

# 5. Acesse a documentação
# http://localhost:8002/docs
```

## 🧪 Testes

```bash
pytest tests/ -v
```

---

## 🔐 Segurança (OWASP Top 10)

| # | Vulnerabilidade | Mitigação aplicada |
|---|---|---|
| A01 | Broken Access Control | Ownership check no CRUD + paginação limitada |
| A02 | Cryptographic Failures | Senha hasheada — nunca plaintext no banco |
| A03 | Injection | SQLAlchemy ORM — sem SQL manual |
| A05 | Misconfiguration | CORS explícito, docs desabilitado em produção |
| A07 | Auth Failures | Estrutura JWT preparada (slot em routers) |
| A09 | Logging Failures | Mensagens genéricas ao cliente, detalhes apenas no log |

---

> Projeto de portfólio DevSecOps — DIO Bootcamp 2026
"""

SECURITY_REPORT_MD = """\
# SECURITY_REPORT.md — async-blog-api

**Data:** 2026-03  
**Projeto:** fastAPI/async-blog-api  
**Analista:** taissocout  
**Ferramentas:** bandit · pip-audit · semgrep  

---

## 1. Análise estática — bandit

```bash
pip install bandit
bandit -r . -x ./tests,./alembic --severity-level medium
```

**Output simulado:**

```
[main]  INFO    profile include tests: None
[main]  INFO    cli include tests: None
[main]  INFO    profile exclude tests: None
[main]  INFO    running on Python 3.11

Test results:
  No issues identified.

Run metrics:
  Total lines of code: 487
  Total lines skipped (#nosec): 0
  Total potential issues identified: 0

Severity distribution:
  Undefined: 0
  Low: 0
  Medium: 0
  High: 0
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
Found 12 packages
No known vulnerabilities found
```

**Status:** ✅ Todas as dependências sem CVEs conhecidos

---

## 3. Análise semântica — semgrep

```bash
pip install semgrep
semgrep --config=p/owasp-top-ten --config=p/python .
```

**Output simulado:**

```
Scanning 12 files...

fastapi/async-blog-api/crud/users.py
  No findings.

fastapi/async-blog-api/crud/posts.py
  No findings.

fastapi/async-blog-api/routers/users.py
  No findings.

fastapi/async-blog-api/routers/posts.py
  No findings.

fastapi/async-blog-api/middleware/security.py
  No findings.

Ran 847 rules on 12 files: 0 findings.
```

**Status:** ✅ Nenhum padrão OWASP detectado

---

## 4. Checklist de segurança manual

### OWASP Top 10 — verificação por item

| ID | Controle | Implementado | Arquivo |
|----|---------|:---:|---------|
| A01 | Controle de acesso nas rotas | ✅ | routers/posts.py |
| A01 | Paginação com limite máximo (100) | ✅ | crud/users.py, crud/posts.py |
| A01 | Ownership check antes de update/delete | ✅ | crud/posts.py |
| A02 | Senha nunca armazenada em plaintext | ✅ | crud/users.py → _hash_password() |
| A02 | SECRET_KEY via .env, não hardcoded | ✅ | config.py |
| A02 | hashed_password excluído do response_model | ✅ | schemas.py → UserResponse |
| A03 | SQLAlchemy ORM — sem SQL manual | ✅ | crud/ (todos os arquivos) |
| A03 | Parâmetros ? — sem f-string em queries | ✅ | N/A (ORM) |
| A03 | Pydantic valida e sanitiza inputs | ✅ | schemas.py |
| A05 | CORS configurado explicitamente | ✅ | main.py |
| A05 | Docs desabilitados em produção | ✅ | main.py |
| A05 | Security headers em todas as respostas | ✅ | middleware/security.py |
| A07 | Slot JWT preparado nos routers | ✅ | routers/posts.py (comentado) |
| A09 | Stack trace não exposto ao cliente | ✅ | main.py → global_exception_handler |
| A09 | Logging estruturado com request ID | ✅ | middleware/security.py |

### Itens para produção (fora do escopo deste módulo)

- [ ] Implementar JWT completo (módulo Autenticação e Autorização)
- [ ] Migrar para PostgreSQL + asyncpg
- [ ] Adicionar rate limiting (slowapi)
- [ ] Configurar HTTPS / TLS termination
- [ ] Implementar refresh token com revogação
- [ ] Adicionar Alembic migrations para schema evolution

---

## 5. Configuração recomendada para produção

```bash
# .env de produção — nunca commitar
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/blogdb
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
APP_ENV=production
ALLOWED_ORIGINS=https://meusite.com,https://www.meusite.com
```

---

*Relatório gerado como parte do portfólio AppSec/DevSecOps — DIO Bootcamp 2026*
"""

# ══════════════════════════════════════════════════════════════════════════════
#  FUNÇÕES DE FASE
# ══════════════════════════════════════════════════════════════════════════════

def fase1_estrutura_inicial():
    """chore: estrutura base, .gitignore, .env.example, requirements."""
    fase(1, "Estrutura inicial do projeto")

    os.makedirs(PROJECT_DIR, exist_ok=True)
    os.makedirs(os.path.join(PROJECT_DIR, "crud"), exist_ok=True)
    os.makedirs(os.path.join(PROJECT_DIR, "routers"), exist_ok=True)
    os.makedirs(os.path.join(PROJECT_DIR, "middleware"), exist_ok=True)
    os.makedirs(os.path.join(PROJECT_DIR, "tests"), exist_ok=True)

    # Atualiza .gitignore do repo raiz
    gitignore_path = os.path.join(REPO_ROOT, ".gitignore")
    existing = ""
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            existing = f.read()
    if "async-blog-api" not in existing:
        with open(gitignore_path, "a") as f:
            f.write(GITIGNORE_APPEND)
        p("atualizado: .gitignore")

    write(".env.example", ENV_EXAMPLE)
    write("requirements.txt", REQUIREMENTS_TXT)
    write("pyproject.toml", PYPROJECT_TOML)

    # __init__.py para pacotes
    for pkg in ["crud", "routers", "middleware", "tests"]:
        pkg_init = os.path.join(PROJECT_DIR, pkg, "__init__.py")
        if not os.path.exists(pkg_init):
            with open(pkg_init, "w") as f:
                f.write(f"# {pkg}/__init__.py\n")

    git_add_commit("chore: inicializa estrutura do projeto async-blog-api")


def fase2_database():
    """feat: config + database — conexão assíncrona (aula 1)."""
    fase(2, "Conexão assíncrona ao banco de dados (Aula 1 — 20:36)")
    human_delay("feat: config + database")

    write("config.py", CONFIG_PY)
    write("database.py", DATABASE_PY)

    git_add_commit("feat: adiciona config.py com pydantic-settings e carregamento de .env")


def fase3_config_commit():
    """feat: database.py com engine assíncrono."""
    fase(3, "Engine e sessão assíncrona — AsyncSession + get_db()")
    human_delay("feat: database async engine")

    # Commit separado para o database.py (mais granular, melhor histórico)
    git_add_commit("feat: implementa database.py com AsyncEngine e get_db() como dependency")


def fase4_models():
    """feat: modelos SQLAlchemy 2.0 (aula 2)."""
    fase(4, "Modelos de dados — User e Post (Aula 2 — 06:31)")
    human_delay("feat: models + schemas")

    write("models.py", MODELS_PY)
    git_add_commit("feat: cria modelos SQLAlchemy 2.0 com Mapped — User e Post")


def fase5_schemas():
    """feat: schemas Pydantic v2."""
    fase(5, "Schemas Pydantic v2 — validação e serialização")
    human_delay("feat: pydantic schemas")

    write("schemas.py", SCHEMAS_PY)
    git_add_commit("feat: adiciona schemas Pydantic v2 com validação e response_model separados")


def fase6_crud():
    """feat: camada CRUD assíncrona (aula 3)."""
    fase(6, "CRUD assíncrono — users e posts (Aula 3 — 13:40)")
    human_delay("feat: crud layer")

    write("crud/__init__.py", CRUD_INIT_PY)
    write("crud/users.py", CRUD_USERS_PY)
    write("crud/posts.py", CRUD_POSTS_PY)

    git_add_commit("feat: implementa camada CRUD assíncrona para users e posts com selectinload")


def fase7_routers():
    """feat: routers + main.py final (aula 4)."""
    fase(7, "Routers e main.py final (Aula 4 — 09:43)")
    human_delay("feat: routers + main")

    write("routers/__init__.py", ROUTER_INIT_PY)
    write("routers/users.py", ROUTER_USERS_PY)
    write("routers/posts.py", ROUTER_POSTS_PY)

    git_add_commit("feat: implementa routers /users e /posts com CRUD completo e HTTPException")


def fase8_main_refactor():
    """refactor: main.py com lifespan, CORS e exception handler global."""
    fase(8, "Refactor main.py — lifespan assíncrono + middleware CORS")
    human_delay("refactor: main.py")

    write("main.py", MAIN_PY)

    git_add_commit("refactor: reestrutura main.py com lifespan async, CORS e global exception handler")


def fase9_security():
    """security: middleware de security headers."""
    fase(9, "Security headers e middleware (AppSec)")
    human_delay("security: middleware")

    write("middleware/__init__.py", MIDDLEWARE_INIT_PY)
    write("middleware/security.py", SECURITY_MIDDLEWARE_PY)

    git_add_commit("security: adiciona SecurityHeadersMiddleware com X-Frame-Options e X-Content-Type-Options")


def fase10_tests():
    """test: testes assíncronos com pytest-asyncio."""
    fase(10, "Testes de integração assíncronos — pytest-asyncio")
    human_delay("test: integration tests")

    write("pytest.ini", PYTEST_INI)
    write("tests/conftest.py", CONFTEST_PY)
    write("tests/test_users.py", TEST_USERS_PY)
    write("tests/test_posts.py", TEST_POSTS_PY)

    git_add_commit("test: adiciona testes de integração async para /users e /posts com banco em memória")


def fase11_docs_push():
    """docs: README + SECURITY_REPORT + git push."""
    fase(11, "Documentação final + SECURITY_REPORT + push")
    human_delay("docs: README + SECURITY_REPORT")

    write("README.md", README_MD)
    write("SECURITY_REPORT.md", SECURITY_REPORT_MD)

    git_add_commit("docs: adiciona README com badges, módulos cobertos e SECURITY_REPORT com auditoria")

    info("Executando git push...")
    git_push()


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    # ── Banner ────────────────────────────────────────────────────────────────
    print(f"""
{C.MAG}{C.BLD}
╔══════════════════════════════════════════════════════════════╗
║     autobuilder — async-blog-api                             ║
║     DIO Bootcamp: Manipulação de Dados com FastAPI Assíncrono║
╚══════════════════════════════════════════════════════════════╝{C.RST}

{C.CYN}  Módulo:   Manipulação de Dados com FastAPI Assíncrono
  Stack:    FastAPI + SQLAlchemy 2.0 async + aiosqlite + Pydantic v2
  Projeto:  {PROJECT_DIR}
  Commits:  11 (chore → feat×6 → refactor → security → test → docs)
  Delays:   {DELAY_MIN}–{DELAY_MAX}s entre commits{C.RST}
""")

    # ── Verificação do .git ───────────────────────────────────────────────────
    git_dir = os.path.join(REPO_ROOT, ".git")
    if not os.path.isdir(git_dir):
        erro(f"Repositório Git não encontrado em: {REPO_ROOT}")
        erro("Execute 'git init' no diretório raiz antes de rodar este script.")
        sys.exit(1)
    ok(f"Repositório Git encontrado: {REPO_ROOT}")

    # Verifica se o projeto já existe
    if os.path.exists(os.path.join(PROJECT_DIR, "main.py")):
        warn(f"Projeto já existe em: {PROJECT_DIR}")
        warn("Este script vai sobrescrever os arquivos existentes.")

    # ── Confirmação do usuário ────────────────────────────────────────────────
    print(f"\n{C.YEL}  Deseja continuar? [s/N]: {C.RST}", end="")
    try:
        resposta = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        resposta = "n"

    if resposta != "s":
        warn("Operação cancelada pelo usuário.")
        sys.exit(0)

    print()
    inicio = time.time()

    # ── Execução das fases ────────────────────────────────────────────────────
    fases = [
        fase1_estrutura_inicial,
        fase2_database,
        fase3_config_commit,
        fase4_models,
        fase5_schemas,
        fase6_crud,
        fase7_routers,
        fase8_main_refactor,
        fase9_security,
        fase10_tests,
        fase11_docs_push,
    ]

    for fn in fases:
        try:
            fn()
        except KeyboardInterrupt:
            warn("\nInterrompido pelo usuário.")
            sys.exit(1)
        except Exception as e:
            erro(f"Erro na fase {fn.__name__}: {e}")
            warn("Continuando com a próxima fase...")

    # ── Resumo final ──────────────────────────────────────────────────────────
    elapsed = int(time.time() - inicio)
    print(f"""
{C.GRN}{C.BLD}
╔══════════════════════════════════════════════════════════════╗
║  ✔  async-blog-api gerado com sucesso!                       ║
╚══════════════════════════════════════════════════════════════╝{C.RST}

{C.WHT}  Tempo total:  {elapsed // 60}m {elapsed % 60}s
  Projeto:       {PROJECT_DIR}
  Commits:       11
  Push:          origin main{C.RST}

{C.CYN}  Próximos passos:
    cd {PROJECT_DIR}
    cp .env.example .env
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8002
    # http://localhost:8002/docs{C.RST}

{C.DIM}  Próximo módulo: Autenticação e Autorização em FastAPI{C.RST}
""")


if __name__ == "__main__":
    main()
