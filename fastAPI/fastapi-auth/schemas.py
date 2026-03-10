"""
schemas.py — Schemas Pydantic v2 para autenticação e autorização.

Aula 2: Uso de tokens para autenticação (19:46)
Padrão de schemas:
  - UserCreate     → entrada para registro (inclui password)
  - UserResponse   → saída (NUNCA inclui hashed_password)
  - TokenResponse  → retorno do /auth/login e /auth/refresh
  - TokenPayload   → dados decodificados do JWT

Segurança:
  - extra="forbid" em schemas de entrada → rejeita campos extras (OWASP A03)
  - password com min_length=8 e pattern de complexidade
  - TokenResponse separa access_token e refresh_token
"""
import re
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ── User ──────────────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email:    str = Field(..., max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v or v.count("@") != 1 or "." not in v.split("@")[-1]:
            raise ValueError("Email inválido")
        return v


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        # Complexidade mínima: maiúscula + minúscula + dígito (OWASP A07)
        if not re.search(r"[A-Z]", v):
            raise ValueError("Senha precisa ter ao menos uma letra maiúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("Senha precisa ter ao menos uma letra minúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("Senha precisa ter ao menos um número")
        return v

    model_config = ConfigDict(extra="forbid")


class UserResponse(UserBase):
    id:         int
    is_active:  bool
    is_superuser: bool
    created_at: datetime

    # from_attributes=True: converte direto do objeto SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


# ── Auth / Tokens ─────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)

    model_config = ConfigDict(extra="forbid")


class TokenResponse(BaseModel):
    """Retorno do login e do refresh. Segue RFC 6749 (OAuth2)."""
    access_token:  str
    refresh_token: str
    token_type:    str = "bearer"
    expires_in:    int   # segundos até expirar o access token


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")


class TokenPayload(BaseModel):
    """Payload decodificado do JWT — claims padrão RFC 7519."""
    sub: str          # subject = user_id como string
    exp: int          # expiration timestamp
    type: str         # "access" | "refresh"


# ── Utilitários ───────────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str
