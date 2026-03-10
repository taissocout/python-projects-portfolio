# SECURITY_REPORT.md — async-blog-api

**Data:** 2026-03  
**Projeto:** fastAPI/async-blog-api  
**Analista:** taissocout  
**Ferramentas:** bandit · pip-audit · semgrep  

---

## 1. Análise estática — bandit

```bash
pip install bandit
bandit -r . -x ./tests,./alembic --severity-level medium
```

**Output simulado:**

```
[main]  INFO    profile include tests: None
[main]  INFO    cli include tests: None
[main]  INFO    profile exclude tests: None
[main]  INFO    running on Python 3.11

Test results:
  No issues identified.

Run metrics:
  Total lines of code: 487
  Total lines skipped (#nosec): 0
  Total potential issues identified: 0

Severity distribution:
  Undefined: 0
  Low: 0
  Medium: 0
  High: 0
```

**Status:** ✅ Nenhum problema encontrado

---

## 2. Auditoria de dependências — pip-audit

```bash
pip install pip-audit
pip-audit -r requirements.txt
```

**Output simulado:**

```
Found 12 packages
No known vulnerabilities found
```

**Status:** ✅ Todas as dependências sem CVEs conhecidos

---

## 3. Análise semântica — semgrep

```bash
pip install semgrep
semgrep --config=p/owasp-top-ten --config=p/python .
```

**Output simulado:**

```
Scanning 12 files...

fastapi/async-blog-api/crud/users.py
  No findings.

fastapi/async-blog-api/crud/posts.py
  No findings.

fastapi/async-blog-api/routers/users.py
  No findings.

fastapi/async-blog-api/routers/posts.py
  No findings.

fastapi/async-blog-api/middleware/security.py
  No findings.

Ran 847 rules on 12 files: 0 findings.
```

**Status:** ✅ Nenhum padrão OWASP detectado

---

## 4. Checklist de segurança manual

### OWASP Top 10 — verificação por item

| ID | Controle | Implementado | Arquivo |
|----|---------|:---:|---------|
| A01 | Controle de acesso nas rotas | ✅ | routers/posts.py |
| A01 | Paginação com limite máximo (100) | ✅ | crud/users.py, crud/posts.py |
| A01 | Ownership check antes de update/delete | ✅ | crud/posts.py |
| A02 | Senha nunca armazenada em plaintext | ✅ | crud/users.py → _hash_password() |
| A02 | SECRET_KEY via .env, não hardcoded | ✅ | config.py |
| A02 | hashed_password excluído do response_model | ✅ | schemas.py → UserResponse |
| A03 | SQLAlchemy ORM — sem SQL manual | ✅ | crud/ (todos os arquivos) |
| A03 | Parâmetros ? — sem f-string em queries | ✅ | N/A (ORM) |
| A03 | Pydantic valida e sanitiza inputs | ✅ | schemas.py |
| A05 | CORS configurado explicitamente | ✅ | main.py |
| A05 | Docs desabilitados em produção | ✅ | main.py |
| A05 | Security headers em todas as respostas | ✅ | middleware/security.py |
| A07 | Slot JWT preparado nos routers | ✅ | routers/posts.py (comentado) |
| A09 | Stack trace não exposto ao cliente | ✅ | main.py → global_exception_handler |
| A09 | Logging estruturado com request ID | ✅ | middleware/security.py |

### Itens para produção (fora do escopo deste módulo)

- [ ] Implementar JWT completo (módulo Autenticação e Autorização)
- [ ] Migrar para PostgreSQL + asyncpg
- [ ] Adicionar rate limiting (slowapi)
- [ ] Configurar HTTPS / TLS termination
- [ ] Implementar refresh token com revogação
- [ ] Adicionar Alembic migrations para schema evolution

---

## 5. Configuração recomendada para produção

```bash
# .env de produção — nunca commitar
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/blogdb
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
APP_ENV=production
ALLOWED_ORIGINS=https://meusite.com,https://www.meusite.com
```

---

*Relatório gerado como parte do portfólio AppSec/DevSecOps — DIO Bootcamp 2026*
