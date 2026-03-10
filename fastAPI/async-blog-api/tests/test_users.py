"""
tests/test_users.py — Testes de integração assíncronos para /users.

Cobre:
  - POST /users    — criação com sucesso e conflito (409)
  - GET /users     — listagem com paginação
  - GET /users/{id} — busca por ID (200 e 404)
  - PATCH /users/{id} — atualização parcial
  - DELETE /users/{id} — remoção (204 e 404)
"""
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
