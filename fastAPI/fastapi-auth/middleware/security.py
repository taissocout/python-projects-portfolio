"""
middleware/security.py — Security headers para todas as respostas.

Headers adicionados (OWASP A05 — Security Misconfiguration):
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  X-XSS-Protection: 1; mode=block
  Strict-Transport-Security: HTTPS obrigatório (HSTS)
  Cache-Control: no-store — tokens não devem ser cacheados
"""
import uuid, logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

SECURITY_HEADERS = {
    "X-Content-Type-Options":  "nosniff",
    "X-Frame-Options":         "DENY",
    "X-XSS-Protection":        "1; mode=block",
    "Referrer-Policy":         "strict-origin-when-cross-origin",
    "Cache-Control":           "no-store, no-cache, must-revalidate",
    "Strict-Transport-Security": "max-age=63072000; includeSubDomains",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        rid = str(uuid.uuid4())[:8]
        # Não loga Authorization header — previne vazamento de token no log
        logger.info(f"[{rid}] {request.method} {request.url.path}")
        response = await call_next(request)
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value
        response.headers["X-Request-ID"] = rid
        return response
