"""
schemas.py — Schemas Pydantic v2 (validação e serialização).

Aula: Modelos de dados em FastAPI (06:31)
Conceitos:
  - Schema ≠ Model: Schema é o contrato da API (JSON), Model é a tabela do banco
  - Base / Create / Update / Response: padrão de herança para evitar repetição
  - model_config = ConfigDict(from_attributes=True): permite .model_validate(db_obj)
  - Field(): validação declarativa — min_length, max_length, pattern
  - Separação: dados de entrada (Create) nunca expõem campos internos (hashed_password)

Segurança (OWASP A03):
  - Pydantic rejeita campos extras por padrão (extra="forbid" nas schemas de entrada)
  - Strings têm tamanho máximo — previne ataques de payload gigante
  - Email validado com pattern básico
"""
import re
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ── User Schemas ──────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email:    str = Field(..., max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("Email inválido")
        return v


class UserCreate(UserBase):
    # Senha recebida em plaintext — será hasheada antes de salvar
    password: str = Field(..., min_length=8, max_length=128)

    model_config = ConfigDict(extra="forbid")   # rejeita campos não declarados


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=50)
    email:    str | None = Field(None, max_length=255)
    is_active: bool | None = None

    model_config = ConfigDict(extra="forbid")


class UserResponse(UserBase):
    id:         int
    is_active:  bool
    created_at: datetime

    # from_attributes=True: converte diretamente do objeto SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


# ── Post Schemas ──────────────────────────────────────────────────────────────

class PostBase(BaseModel):
    title:   str      = Field(..., min_length=1, max_length=200)
    content: str | None = Field(None, max_length=100_000)
    is_published: bool = False


class PostCreate(PostBase):
    model_config = ConfigDict(extra="forbid")


class PostUpdate(BaseModel):
    title:        str | None  = Field(None, min_length=1, max_length=200)
    content:      str | None  = Field(None, max_length=100_000)
    is_published: bool | None = None

    model_config = ConfigDict(extra="forbid")


class PostResponse(PostBase):
    id:         int
    slug:       str
    author_id:  int
    created_at: datetime
    updated_at: datetime
    author:     UserResponse | None = None

    model_config = ConfigDict(from_attributes=True)


# ── Paginação ─────────────────────────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    total:  int
    skip:   int
    limit:  int
    items:  list
