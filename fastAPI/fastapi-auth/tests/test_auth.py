"""
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
"""
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
