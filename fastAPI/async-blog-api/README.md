# async-blog-api

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688?style=flat&logo=fastapi)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0_async-red?style=flat)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=flat)
![DIO](https://img.shields.io/badge/DIO-Bootcamp_2026-C624C1?style=flat)
![AppSec](https://img.shields.io/badge/AppSec-OWASP_Top_10-orange?style=flat)

API RESTful **100% assíncrona** construída com FastAPI, SQLAlchemy 2.0 async e
aiosqlite. Projeto desenvolvido durante o módulo **Manipulação de Dados com
FastAPI Assíncrono** do bootcamp DIO — Jornada para o Futuro.

---

## 📚 Módulos cobertos

| Aula | Título | Duração | Status |
|------|--------|---------|--------|
| 1 | Conexão a banco de dados assíncrono | 20:36 | ✅ |
| 2 | Modelos de dados em FastAPI | 06:31 | ✅ |
| 3 | Operações CRUD assíncronas em APIs RESTful | 13:40 | ✅ |
| 4 | Implementação final do CRUD | 09:43 | ✅ |

---

## 🗂 Estrutura do projeto

```
async-blog-api/
├── main.py                  ← ponto de entrada + lifespan + CORS
├── config.py                ← configurações via pydantic-settings
├── database.py              ← engine/sessão assíncrona + init_db
├── models.py                ← User e Post (SQLAlchemy 2.0 Mapped)
├── schemas.py               ← contratos Pydantic v2 (Request/Response)
├── crud/
│   ├── users.py             ← CRUD assíncrono de usuários
│   └── posts.py             ← CRUD assíncrono de posts + slug
├── routers/
│   ├── users.py             ← endpoints /users (5 rotas)
│   └── posts.py             ← endpoints /posts (6 rotas)
├── middleware/
│   └── security.py          ← security headers + request ID
├── tests/
│   ├── conftest.py          ← fixtures com banco em memória
│   ├── test_users.py        ← testes de integração (users)
│   └── test_posts.py        ← testes de integração (posts)
├── .env.example
├── requirements.txt
└── SECURITY_REPORT.md
```

---

## ⚡ Conceitos aplicados

### Assíncrono vs. Síncrono
| | Síncrono | Assíncrono |
|---|---|---|
| Conexão | `engine.connect()` | `async with engine.connect()` |
| Sessão | `Session()` | `AsyncSession()` |
| Query | `session.execute(q)` | `await session.execute(q)` |
| Comportamento | Bloqueia o servidor | Libera para outras requests |

### SQLAlchemy 2.0 — nova sintaxe
```python
# Antigo (1.x)
Column(String, nullable=False)

# Novo (2.0) — type-safe com Mapped
username: Mapped[str] = mapped_column(String(50), unique=True)
```

### Pydantic v2 — schemas separados de models
```python
# Schema de entrada — nunca expõe campos internos
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

# Schema de resposta — filtra hashed_password automaticamente
class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
```

---

## 🚀 Como executar

```bash
# 1. Clone e entre no diretório
cd fastAPI/async-blog-api

# 2. Configure o ambiente
cp .env.example .env

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Suba a API
uvicorn main:app --reload --port 8002

# 5. Acesse a documentação
# http://localhost:8002/docs
```

## 🧪 Testes

```bash
pytest tests/ -v
```

---

## 🔐 Segurança (OWASP Top 10)

| # | Vulnerabilidade | Mitigação aplicada |
|---|---|---|
| A01 | Broken Access Control | Ownership check no CRUD + paginação limitada |
| A02 | Cryptographic Failures | Senha hasheada — nunca plaintext no banco |
| A03 | Injection | SQLAlchemy ORM — sem SQL manual |
| A05 | Misconfiguration | CORS explícito, docs desabilitado em produção |
| A07 | Auth Failures | Estrutura JWT preparada (slot em routers) |
| A09 | Logging Failures | Mensagens genéricas ao cliente, detalhes apenas no log |

---

> Projeto de portfólio DevSecOps — DIO Bootcamp 2026
