"""
middleware/security.py — Security headers e proteções adicionais.

Segurança aplicada (OWASP):
  A05 — Misconfiguration: headers de segurança em todas as respostas
  A09 — Logging Failures: request ID para rastreamento sem dados sensíveis

Headers adicionados:
  X-Content-Type-Options: nosniff    — previne MIME sniffing
  X-Frame-Options: DENY              — previne clickjacking
  X-XSS-Protection: 1; mode=block   — proteção XSS em browsers legados
  Referrer-Policy: strict-origin     — controle de referrer
  Cache-Control: no-store            — evita cache de respostas de API
"""
import uuid
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Cache-Control": "no-store, no-cache, must-revalidate",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Injeta security headers em todas as respostas."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Gera request ID para rastreamento — sem dados sensíveis no log
        request_id = str(uuid.uuid4())[:8]
        logger.info(f"[{request_id}] {request.method} {request.url.path}")

        response = await call_next(request)

        # Aplica security headers
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value

        response.headers["X-Request-ID"] = request_id
        return response
