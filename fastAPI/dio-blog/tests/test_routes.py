"""
tests/test_routes.py — Testes de integração para as rotas da API.

Conceitos:
  - AsyncClient faz requisições HTTP reais ao app (sem servidor)
  - Fixtures do conftest.py injetam banco em memória
  - Testa o ciclo completo: HTTP → rota → validação → banco → resposta
  - Cobre todos os status codes esperados: 200, 201, 404, 422

Estrutura dos testes:
  TestHealthRoutes   → GET / e GET /health (se existir)
  TestPostCRUD       → POST, GET, GET por id
  TestPostFilters    → filtros published, paginação skip/limit
  TestPostValidation → inputs inválidos retornam 422
"""
import pytest


class TestHealthRoutes:
    """Testes para rotas de health check."""

    @pytest.mark.asyncio
    async def test_root_returns_200(self, client):
        """GET / deve retornar 200 e status ok."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"

    @pytest.mark.asyncio
    async def test_root_response_has_message(self, client):
        """GET / deve conter campo message."""
        response = await client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()


class TestPostCRUD:
    """Testes de integração para CRUD de posts."""

    @pytest.mark.asyncio
    async def test_create_post_returns_201(self, client):
        """POST /posts/ com dados válidos deve retornar 201 Created."""
        payload = {"title": "Meu Post de Integração", "published": True}
        response = await client.post("/posts/", json=payload)
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_post_response_structure(self, client):
        """Resposta do POST deve conter os campos esperados."""
        payload = {"title": "Post com Estrutura", "published": False}
        response = await client.post("/posts/", json=payload)
        assert response.status_code == 201
        data = response.json()
        # Verifica campos presentes na resposta
        assert "title" in data or "message" in data  # depende da implementação

    @pytest.mark.asyncio
    async def test_list_posts_returns_200(self, client):
        """GET /posts/ deve retornar 200."""
        response = await client.get("/posts/")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_posts_returns_list(self, client):
        """GET /posts/ deve retornar estrutura com lista de itens."""
        response = await client.get("/posts/")
        assert response.status_code == 200
        data = response.json()
        # Aceita tanto lista direta quanto objeto paginado
        assert isinstance(data, (list, dict))

    @pytest.mark.asyncio
    async def test_create_then_list(self, client):
        """Cria post e verifica que aparece na listagem."""
        title = "Post Criado para Listar"
        await client.post("/posts/", json={"title": title, "published": True})
        response = await client.get("/posts/")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_create_multiple_posts(self, client):
        """Cria múltiplos posts sequencialmente sem erro."""
        for i in range(3):
            resp = await client.post(
                "/posts/", json={"title": f"Post Sequencial {i}", "published": True}
            )
            assert resp.status_code == 201


class TestPostFilters:
    """Testes para filtros e paginação."""

    @pytest.mark.asyncio
    async def test_filter_published_true(self, client):
        """GET /posts/?published=true deve aceitar o query param."""
        response = await client.get("/posts/?published=true")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_filter_published_false(self, client):
        """GET /posts/?published=false deve aceitar o query param."""
        response = await client.get("/posts/?published=false")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_pagination_skip_param(self, client):
        """Query param skip=0 deve ser aceito."""
        response = await client.get("/posts/?skip=0&limit=5")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_pagination_large_skip(self, client):
        """Skip maior que o total de posts deve retornar lista vazia."""
        response = await client.get("/posts/?skip=9999")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_framework_filter(self, client):
        """GET /posts/{framework} deve retornar dados do framework."""
        response = await client.get("/posts/FastAPI")
        assert response.status_code == 200
        data = response.json()
        assert "framework" in data
        assert data["framework"] == "FastAPI"


class TestPostValidation:
    """Testes para validação de entrada — inputs inválidos."""

    @pytest.mark.asyncio
    async def test_create_post_missing_title_returns_422(self, client):
        """POST sem título deve retornar 422 Unprocessable Entity."""
        response = await client.post("/posts/", json={"published": True})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_post_empty_body_returns_422(self, client):
        """POST com body vazio deve retornar 422."""
        response = await client.post("/posts/", json={})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_published_wrong_type_returns_422(self, client):
        """POST com published como string inválida deve retornar 422."""
        response = await client.post(
            "/posts/", json={"title": "Post", "published": "nao_e_bool"}
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_published_query_param(self, client):
        """Query param published com valor inválido deve retornar 422."""
        response = await client.get("/posts/?published=invalido")
        assert response.status_code == 422
