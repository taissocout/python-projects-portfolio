# fastapi-auth

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688?style=flat&logo=fastapi)
![JWT](https://img.shields.io/badge/JWT-python--jose-000000?style=flat&logo=jsonwebtokens)
![bcrypt](https://img.shields.io/badge/Hash-bcrypt-red?style=flat)
![DIO](https://img.shields.io/badge/DIO-Bootcamp_2026-C624C1?style=flat)
![AppSec](https://img.shields.io/badge/AppSec-OWASP_A07-orange?style=flat)

API de **Autenticação e Autorização** com FastAPI, JWT (access + refresh token),
bcrypt e revogação de tokens. Desenvolvida no módulo
**Autenticação e Autorização em FastAPI** — DIO Jornada para o Futuro.

---

## 📚 Módulo coberto

| Aula | Título | Duração | Status |
|------|--------|---------|--------|
| 1 | Como iremos autenticar as nossas rotas | 02:39 | ✅ |
| 2 | Uso de tokens para autenticação | 19:46 | ✅ |

---

## 🔐 Fluxo de autenticação implementado

```
1. POST /auth/register  → cria usuário com senha bcrypt
2. POST /auth/login     → retorna access_token (30min) + refresh_token (7 dias)
3. GET  /auth/me        → Bearer <access_token> → dados do usuário
4. POST /auth/refresh   → refresh_token → novo par de tokens (token rotation)
5. POST /auth/logout    → revoga refresh_token (logout simples)
6. POST /auth/logout-all → revoga todos os tokens (logout total)
```

---

## 🗂 Estrutura do projeto

```
fastapi-auth/
├── main.py                    ← entry point + CORS + exception handler
├── config.py                  ← settings via pydantic-settings
├── database.py                ← engine assíncrono + get_db()
├── models.py                  ← User + RefreshToken (SQLAlchemy 2.0)
├── schemas.py                 ← contratos Pydantic v2
├── dependencies.py            ← get_current_user + get_current_superuser
├── services/
│   └── auth_service.py        ← hash, JWT, CRUD de user/token
├── routers/
│   └── auth.py                ← /auth/* (6 endpoints)
├── middleware/
│   └── security.py            ← security headers
├── tests/
│   ├── conftest.py
│   └── test_auth.py           ← 9 testes de integração
├── .env.example
├── requirements.txt
└── SECURITY_REPORT.md
```

---

## 🚀 Como executar

```bash
cd fastAPI/fastapi-auth
cp .env.example .env
pip install -r requirements.txt
uvicorn main:app --reload --port 8003
# http://localhost:8003/docs
```

## 🧪 Testes

```bash
pytest tests/ -v
```

---

## 🔐 Segurança (OWASP Top 10)

| # | Vulnerabilidade | Mitigação |
|---|---|---|
| A02 | Cryptographic Failures | bcrypt com custo 12 — hash adaptativo |
| A02 | Exposição de senha | hashed_password nunca no response_model |
| A03 | Injection | SQLAlchemy ORM — sem SQL manual |
| A05 | Misconfiguration | CORS explícito, docs off em produção, security headers |
| A07 | Auth Failures — User Enumeration | Mensagem genérica no login inválido |
| A07 | Auth Failures — Token Reutilização | Token rotation no refresh |
| A07 | Auth Failures — Sem Revogação | RefreshToken no banco com is_revoked |
| A07 | Auth Failures — Timing Attack | passlib verify em tempo constante |
| A09 | Logging Failures | Stack trace nunca exposto ao cliente |

> Projeto de portfólio DevSecOps — DIO Bootcamp 2026
