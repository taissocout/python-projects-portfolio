"""
conftest.py — Fixtures compartilhadas para todos os testes do dio-blog.

Módulo DIO: Testando APIs RESTful Assíncronas em FastAPI (22:41)

Conceitos aplicados:
  - Banco em memória isolado por teste (SQLite :memory:)
  - Override de dependência (get_db) — injeta sessão de teste
  - AsyncClient + ASGITransport — requisições HTTP sem servidor real
  - Fixtures assíncronas com pytest_asyncio.fixture
  - scope="function" — estado limpo a cada teste (sem contaminação)

Por que banco em memória e não o arquivo blog.db?
  O banco de testes deve ser isolado do banco de desenvolvimento.
  :memory: é criado e destruído a cada função de teste — zero side effects.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    create_async_engine, async_sessionmaker, AsyncSession
)

from main import app
from database import get_db, Base

# Banco em memória: isolado, rápido, sem persistência entre testes
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """
    Cria banco em memória, roda os testes e destrói tudo.
    scope="function" = nova instância para CADA teste.
    """
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(
        bind=engine, class_=AsyncSession,
        expire_on_commit=False, autocommit=False, autoflush=False,
    )
    async with session_factory() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(test_db):
    """
    AsyncClient com banco de testes injetado via override de dependência.
    app.dependency_overrides substitui get_db() pelo test_db fixture.
    """
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def sample_post(client):
    """Fixture helper: cria um post publicado para testes que precisam de dado pré-existente."""
    payload = {"title": "Post de Teste", "published": True}
    response = await client.post("/posts/", json=payload)
    assert response.status_code == 201, f"Falha na fixture sample_post: {response.text}"
    return response.json()


@pytest_asyncio.fixture(scope="function")
async def sample_unpublished_post(client):
    """Fixture helper: cria um post NÃO publicado."""
    payload = {"title": "Rascunho", "published": False}
    response = await client.post("/posts/", json=payload)
    assert response.status_code == 201
    return response.json()
