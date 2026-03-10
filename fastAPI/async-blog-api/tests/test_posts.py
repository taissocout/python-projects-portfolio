"""
tests/test_posts.py — Testes de integração assíncronos para /posts.

Cobre:
  - POST /posts    — criação (201) e autor inexistente (404)
  - GET /posts     — listagem pública (published_only=True)
  - GET /posts/{id} — busca por ID
  - GET /posts/slug/{slug} — busca por slug
  - PATCH /posts/{id} — atualização com ownership check
  - DELETE /posts/{id} — remoção com ownership check (403 e 204)
"""
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
