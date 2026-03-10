"""
tests/test_concurrent.py — Testes de concorrência e performance básica.

Conceitos:
  - asyncio.gather(): executa múltiplas corrotinas concorrentemente
  - Testa que a API aguenta múltiplas requisições simultâneas
  - Mede tempo de resposta básico
  - Verifica que não há race conditions nas operações de leitura

Por que testar concorrência em APIs assíncronas?
  O objetivo do async/await é exatamente suportar múltiplas requisições
  simultâneas. Precisamos confirmar que a implementação funciona corretamente
  sob carga — não apenas com uma requisição por vez.
"""
import pytest
import asyncio
import time


class TestConcurrentRequests:
    """Testa múltiplas requisições simultâneas."""

    @pytest.mark.asyncio
    async def test_concurrent_get_requests(self, client):
        """
        10 requisições GET simultâneas não devem causar erro.
        Usa asyncio.gather() para execução verdadeiramente concorrente.
        """
        tasks = [client.get("/posts/") for _ in range(10)]
        responses = await asyncio.gather(*tasks)

        for response in responses:
            assert response.status_code == 200,                 f"Falha em requisição concorrente: {response.status_code}"

    @pytest.mark.asyncio
    async def test_concurrent_post_requests(self, client):
        """
        5 criações simultâneas de posts não devem conflitar.
        Cada post tem título único para evitar conflitos de UNIQUE constraint.
        """
        tasks = [
            client.post("/posts/", json={"title": f"Post Concorrente {i}", "published": True})
            for i in range(5)
        ]
        responses = await asyncio.gather(*tasks)

        # Todas devem ser criadas com sucesso
        status_codes = [r.status_code for r in responses]
        assert all(s == 201 for s in status_codes),             f"Falha em posts concorrentes: {status_codes}"

    @pytest.mark.asyncio
    async def test_mixed_concurrent_requests(self, client):
        """
        Mix de GET e POST simultâneos sem interferência.
        """
        get_tasks  = [client.get("/posts/") for _ in range(5)]
        post_tasks = [
            client.post("/posts/", json={"title": f"Post Mix {i}", "published": True})
            for i in range(3)
        ]
        responses = await asyncio.gather(*(get_tasks + post_tasks))

        # Verifica que nenhuma requisição retornou 500
        errors = [r for r in responses if r.status_code >= 500]
        assert len(errors) == 0,             f"{len(errors)} requisições retornaram erro 5xx"


class TestResponseTime:
    """Testes básicos de tempo de resposta."""

    @pytest.mark.asyncio
    async def test_health_check_fast(self, client):
        """
        GET / deve responder em menos de 1 segundo.
        Testa que não há operações bloqueantes na rota de health.
        """
        start = time.perf_counter()
        response = await client.get("/")
        elapsed = time.perf_counter() - start

        assert response.status_code == 200
        assert elapsed < 1.0, f"Health check demorou {elapsed:.3f}s (máx: 1.0s)"

    @pytest.mark.asyncio
    async def test_list_posts_acceptable_time(self, client):
        """GET /posts/ deve responder em menos de 2 segundos."""
        start = time.perf_counter()
        response = await client.get("/posts/")
        elapsed = time.perf_counter() - start

        assert response.status_code == 200
        assert elapsed < 2.0, f"Listagem demorou {elapsed:.3f}s (máx: 2.0s)"
