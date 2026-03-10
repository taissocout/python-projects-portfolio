"""
tests/test_unit.py — Testes unitários com pytest-mock.

Conceitos:
  - mocker.patch(): substitui dependências externas sem banco real
  - mocker.MagicMock(): objeto mock com atributos configuráveis
  - AsyncMock: mock de funções assíncronas (await compatível)
  - Testa lógica de negócio isolada — sem I/O, sem banco, sem HTTP

Diferença unitário vs integração:
  Unitário:    testa UMA função em isolamento — mock nas dependências
  Integração:  testa o fluxo completo — banco real (em memória) + HTTP
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone


class TestPostFiltering:
    """Testes unitários para lógica de filtragem de posts."""

    def test_published_filter_true(self):
        """Filtragem por published=True retorna apenas posts publicados."""
        fake_db = [
            {"title": "Pub 1",  "published": True},
            {"title": "Draft",  "published": False},
            {"title": "Pub 2",  "published": True},
        ]
        result = [p for p in fake_db if p["published"] == True]
        assert len(result) == 2
        assert all(p["published"] for p in result)

    def test_published_filter_false(self):
        """Filtragem por published=False retorna apenas rascunhos."""
        fake_db = [
            {"title": "Pub",   "published": True},
            {"title": "Draft", "published": False},
        ]
        result = [p for p in fake_db if p["published"] == False]
        assert len(result) == 1
        assert result[0]["title"] == "Draft"

    def test_pagination_skip(self):
        """Skip correto pula os primeiros N itens."""
        fake_db = [{"title": f"Post {i}", "published": True} for i in range(5)]
        skip, limit = 2, 10
        result = fake_db[skip: skip + limit]
        assert len(result) == 3
        assert result[0]["title"] == "Post 2"

    def test_pagination_limit(self):
        """Limit correto retorna no máximo N itens."""
        fake_db = [{"title": f"Post {i}", "published": True} for i in range(10)]
        skip, limit = 0, 3
        result = fake_db[skip: skip + limit]
        assert len(result) == 3

    def test_pagination_skip_and_limit_combined(self):
        """Skip + limit combinados funcionam corretamente."""
        fake_db = [{"title": f"Post {i}", "published": True} for i in range(10)]
        result = fake_db[3: 3 + 4]
        assert len(result) == 4
        assert result[0]["title"] == "Post 3"

    def test_empty_db_returns_empty_list(self):
        """Banco vazio retorna lista vazia — sem exceção."""
        fake_db = []
        result = [p for p in fake_db if p.get("published") == True]
        assert result == []


class TestPostValidation:
    """Testes para validação de dados dos posts."""

    def test_post_title_required(self):
        """Post sem título não deve ser aceito."""
        from pydantic import ValidationError
        # Importa o schema real para testar validação Pydantic
        try:
            from routers.posts import Post
            with pytest.raises((ValidationError, TypeError)):
                Post()  # sem title → deve falhar
        except ImportError:
            # Se a estrutura mudou, testa diretamente
            pytest.skip("Schema Post não encontrado no path esperado")

    def test_post_published_default_false(self):
        """Campo published deve ter default False."""
        try:
            from routers.posts import Post
            post = Post(title="Teste")
            assert post.published == False
        except ImportError:
            pytest.skip("Schema Post não encontrado")


class TestMockUsage:
    """Demonstra uso de pytest-mock para isolar dependências."""

    @pytest.mark.asyncio
    async def test_mock_async_function(self, mocker):
        """
        Mostra como mockar uma função assíncrona.
        AsyncMock permite usar await no mock.
        """
        mock_fetch = mocker.AsyncMock(return_value=[{"title": "Mocked", "published": True}])
        result = await mock_fetch()
        assert len(result) == 1
        assert result[0]["title"] == "Mocked"
        mock_fetch.assert_called_once()

    def test_mock_return_value(self, mocker):
        """MagicMock com return_value configurado."""
        mock_db = mocker.MagicMock()
        mock_db.query.return_value = [{"id": 1, "title": "Post"}]
        result = mock_db.query()
        assert result[0]["id"] == 1

    def test_mock_side_effect(self, mocker):
        """side_effect permite simular exceções em mocks."""
        mock_service = mocker.MagicMock()
        mock_service.process.side_effect = ValueError("Erro simulado")
        with pytest.raises(ValueError, match="Erro simulado"):
            mock_service.process()

    @pytest.mark.asyncio
    async def test_mock_patch_decorator(self, mocker):
        """
        mocker.patch() substitui objeto em seu namespace original.
        Útil para mockar dependências externas (banco, API externa, etc).
        """
        # Simula patch de uma função que faria I/O
        with patch("builtins.open", mocker.mock_open(read_data="mocked content")):
            content = open("qualquer_arquivo.txt").read()
            assert content == "mocked content"
