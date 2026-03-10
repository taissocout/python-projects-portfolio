"""
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
"""
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
    """Base declarativa para todos os modelos SQLAlchemy do projeto."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection para rotas FastAPI.
    Garante que a sessão seja sempre fechada — mesmo em caso de exceção.

    Uso nas rotas:
        async def rota(db: AsyncSession = Depends(get_db)): ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        # finally: AsyncSessionLocal garante o close() via context manager


async def init_db():
    """Cria todas as tabelas no banco. Chamado no startup da aplicação."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    """Remove todas as tabelas. Usado apenas em testes (nunca em produção)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
