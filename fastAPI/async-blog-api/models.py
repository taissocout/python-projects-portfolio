"""
models.py — Modelos SQLAlchemy (tabelas do banco de dados).

Aula: Modelos de dados em FastAPI (06:31)
Conceitos:
  - Mapped / mapped_column: sintaxe moderna do SQLAlchemy 2.0 (type-safe)
  - relationship(): define a FK e o join em Python, sem SQL manual
  - __tablename__: nome da tabela no banco
  - ForeignKey: chave estrangeira com ON DELETE CASCADE
  - index=True: cria índice no banco — acelera buscas por email/slug

SQLAlchemy 2.0 vs 1.x:
  Antigo: Column(String, nullable=False)
  Novo:   mapped_column(String, nullable=False)  ← type hints integrados
"""
from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class User(Base):
    """Tabela de usuários — autores dos posts."""
    __tablename__ = "users"

    id:         Mapped[int]      = mapped_column(primary_key=True, autoincrement=True)
    username:   Mapped[str]      = mapped_column(String(50), unique=True, nullable=False, index=True)
    email:      Mapped[str]      = mapped_column(String(255), unique=True, nullable=False, index=True)
    # hash bcrypt — NUNCA armazenar senha em texto puro (OWASP A02)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active:  Mapped[bool]     = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationship — um usuário tem muitos posts (1:N)
    posts: Mapped[list["Post"]] = relationship(
        "Post", back_populates="author", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        # Nunca incluir password no repr (OWASP A02)
        return f"<User id={self.id} username={self.username!r}>"


class Post(Base):
    """Tabela de posts do blog."""
    __tablename__ = "posts"

    id:          Mapped[int]           = mapped_column(primary_key=True, autoincrement=True)
    title:       Mapped[str]           = mapped_column(String(200), nullable=False)
    slug:        Mapped[str]           = mapped_column(String(220), unique=True, nullable=False, index=True)
    content:     Mapped[str | None]    = mapped_column(Text, nullable=True)
    is_published: Mapped[bool]         = mapped_column(Boolean, default=False)
    author_id:   Mapped[int]           = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at:  Mapped[datetime]      = mapped_column(DateTime, server_default=func.now())
    updated_at:  Mapped[datetime]      = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationship — lado N (post pertence a um user)
    author: Mapped["User"] = relationship("User", back_populates="posts")

    def __repr__(self) -> str:
        return f"<Post id={self.id} slug={self.slug!r} published={self.is_published}>"
