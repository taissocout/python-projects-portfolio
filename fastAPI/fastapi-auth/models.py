"""
models.py — Modelos SQLAlchemy 2.0 para autenticação.

Aula 2: Uso de tokens para autenticação (19:46)
Tabelas:
  - User: armazena credenciais (hashed_password — NUNCA plaintext)
  - RefreshToken: persiste refresh tokens para revogação (OWASP A07)

Segurança:
  - hashed_password: bcrypt via passlib — custo adaptativo
  - is_active: permite desativar usuário sem deletar (soft disable)
  - refresh_token com is_revoked: permite logout e invalidação
"""
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id:              Mapped[int]      = mapped_column(primary_key=True, autoincrement=True)
    username:        Mapped[str]      = mapped_column(String(50),  unique=True, nullable=False, index=True)
    email:           Mapped[str]      = mapped_column(String(255), unique=True, nullable=False, index=True)
    # bcrypt hash — NUNCA armazenar senha em plaintext (OWASP A02)
    hashed_password: Mapped[str]      = mapped_column(String(255), nullable=False)
    is_active:       Mapped[bool]     = mapped_column(Boolean, default=True)
    is_superuser:    Mapped[bool]     = mapped_column(Boolean, default=False)
    created_at:      Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at:      Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationship: um user tem muitos refresh tokens
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        # NUNCA incluir hashed_password no repr (OWASP A02)
        return f"<User id={self.id} username={self.username!r} active={self.is_active}>"


class RefreshToken(Base):
    """
    Persiste refresh tokens para permitir revogação explícita.
    Sem essa tabela, um refresh token roubado seria válido até expirar (OWASP A07).
    """
    __tablename__ = "refresh_tokens"

    id:         Mapped[int]      = mapped_column(primary_key=True, autoincrement=True)
    token:      Mapped[str]      = mapped_column(Text, unique=True, nullable=False, index=True)
    user_id:    Mapped[int]      = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    is_revoked: Mapped[bool]     = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")
