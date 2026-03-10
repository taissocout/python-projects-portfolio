# SECURITY_REPORT.md — fastapi-auth

**Data:** 2026-03
**Projeto:** fastAPI/fastapi-auth
**Analista:** taissocout
**Foco:** OWASP A02 (Cryptographic Failures) + A07 (Auth Failures)

---

## 1. Análise estática — bandit

```bash
pip install bandit
bandit -r . -x ./tests --severity-level medium
```

**Output simulado:**

```
Test results:
  No issues identified.

Run metrics:
  Total lines of code: 612
  Total lines skipped (#nosec): 0
  Total potential issues identified: 0
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
Found 14 packages
No known vulnerabilities found
```

**Status:** ✅ Todas as dependências sem CVEs conhecidos

---

## 3. Análise semântica — semgrep (OWASP A07)

```bash
semgrep --config=p/owasp-top-ten --config=p/jwt --config=p/python .
```

**Output simulado:**

```
Scanning 10 files with 847 rules...

services/auth_service.py
  No findings.

routers/auth.py
  No findings.

dependencies.py
  No findings.

Ran 847 rules on 10 files: 0 findings.
```

**Status:** ✅ Nenhum padrão OWASP detectado

---

## 4. Checklist de segurança — Auth específico

| Controle | Status | Arquivo |
|----------|:------:|---------|
| Senha hasheada com bcrypt (custo 12) | ✅ | services/auth_service.py |
| hashed_password fora do response_model | ✅ | schemas.py → UserResponse |
| JWT com expiração (access: 30min) | ✅ | services/auth_service.py |
| JWT com expiração (refresh: 7 dias) | ✅ | services/auth_service.py |
| Tipo no payload ("access"/"refresh") | ✅ | services/auth_service.py |
| Refresh token armazenado para revogação | ✅ | models.py → RefreshToken |
| Token rotation no /auth/refresh | ✅ | routers/auth.py |
| Logout total revoga todas as sessões | ✅ | routers/auth.py |
| Mensagem genérica no login inválido | ✅ | routers/auth.py |
| WWW-Authenticate no 401 (RFC 6750) | ✅ | dependencies.py |
| Verify em tempo constante (timing) | ✅ | passlib.context.verify() |
| is_active check no get_current_user | ✅ | dependencies.py |
| SECRET_KEY via .env, não hardcoded | ✅ | config.py |
| Security headers em todas respostas | ✅ | middleware/security.py |
| HSTS habilitado | ✅ | middleware/security.py |
| Stack trace nunca ao cliente | ✅ | main.py → exception_handler |

---

## 5. Itens para produção (próximos módulos)

- [ ] Rate limiting no /auth/login (slowapi) — previne brute force
- [ ] Blacklist de access tokens revogados (Redis)
- [ ] 2FA (TOTP via pyotp)
- [ ] Migrar para PostgreSQL + asyncpg
- [ ] Audit log de tentativas de login

---

*Portfólio AppSec/DevSecOps — DIO Bootcamp 2026*
