# SECURITY_REPORT — dio-blog
---

## 6. Cobertura de testes de segurança

| Teste | Vulnerabilidade | Resultado |
|-------|----------------|-----------|
| `test_sql_injection_attempt_in_title` | OWASP A03 | ✅ 201 ou 422 — nunca 500 |
| `test_xss_attempt_in_title` | OWASP A03 | ✅ Tratado como string |
| `test_oversized_title_handled` | DoS / A05 | ✅ 201 ou 422 — nunca 500 |
| `test_422_error_no_stack_trace` | OWASP A09 | ✅ Sem Traceback na resposta |
| `test_extra_fields_ignored_or_rejected` | OWASP A03 | ✅ 201 ou 422 |
| `test_no_server_header_leakage` | OWASP A05 | ✅ Sem versão exposta |
| `test_404_returns_json_not_html` | OWASP A09 | ✅ JSON consistente |

```bash
# Rodar apenas testes de segurança
pytest tests/test_security.py -v

# Output esperado:
# PASSED tests/test_security.py::TestSecurityHeaders::test_response_has_content_type
# PASSED tests/test_security.py::TestInputSanitization::test_sql_injection_attempt_in_title
# PASSED tests/test_security.py::TestInputSanitization::test_xss_attempt_in_title
# PASSED tests/test_security.py::TestInputSanitization::test_oversized_title_handled
# PASSED tests/test_security.py::TestErrorHandling::test_422_error_no_stack_trace
# ...
```

