
---

## 🧪 Testes (Módulo: Testando APIs RESTful Assíncronas)

| Arquivo | Tipo | Cobertura |
|---------|------|-----------|
| `tests/test_unit.py` | Unitário + Mock | Lógica de filtragem e paginação |
| `tests/test_routes.py` | Integração | CRUD completo de posts |
| `tests/test_security.py` | Segurança | Inputs maliciosos, headers, erros |
| `tests/test_database.py` | Banco | Conexão, schema, transações |
| `tests/test_concurrent.py` | Concorrência | asyncio.gather(), tempo de resposta |

### Como executar

```bash
cd fastAPI/dio-blog

# Instala dependências de teste
pip install -r requirements-dev.txt --break-system-packages

# Roda todos os testes
pytest tests/ -v

# Com cobertura de código
bash run_tests.sh --coverage

# Apenas um arquivo
pytest tests/test_security.py -v

# Apenas uma classe
pytest tests/test_routes.py::TestPostCRUD -v
```

### Stack de testes

| Biblioteca | Função |
|-----------|--------|
| `pytest-asyncio` | Suporte a testes `async def` |
| `httpx + ASGITransport` | Requisições HTTP sem servidor real |
| `pytest-mock` | Mocks e patches isolados por teste |
| `asyncio.gather` | Testes de concorrência assíncrona |
| `SQLite :memory:` | Banco isolado por teste |
| `coverage` | Relatório de cobertura de código |

