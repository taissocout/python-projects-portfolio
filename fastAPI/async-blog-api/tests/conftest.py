"""
conftest.py — Fixtures compartilhadas para os testes.

Configuração de testes async com pytest-asyncio:
  - Banco de dados em memória (:memory:) isolado por teste
  - AsyncClient do httpx para simular requests HTTP
  - Fixtures com escopo de função — estado limpo a cada teste
"""
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
    """Sessão de banco em memória — criada e destruída a cada teste."""
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
    """AsyncClient com banco de testes injetado via override de dependência."""
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
