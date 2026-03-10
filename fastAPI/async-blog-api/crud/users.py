"""
crud/users.py — Operações CRUD assíncronas para usuários.

Aula: Operações CRUD assíncronas em APIs RESTful (13:40)
Conceitos:
  - select(): query builder do SQLAlchemy 2.0 — sem SQL manual (OWASP A03)
  - scalars().first(): retorna o objeto mapeado ou None
  - session.add() + await session.flush(): insere sem commit (commit no get_db)
  - await session.refresh(obj): recarrega o objeto após insert (pega o id gerado)
  - Separação em camada de serviço: rotas não acessam o banco diretamente
"""
import hashlib
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models import User
from schemas import UserCreate, UserUpdate


def _hash_password(password: str) -> str:
    """
    Hash simples com SHA-256 + salt para o projeto de estudo.
    Em produção: use passlib[bcrypt] ou argon2-cffi (OWASP A02).
    """
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}:{hashed}"


def _verify_password(plain: str, hashed_stored: str) -> bool:
    """Verifica senha contra o hash armazenado."""
    try:
        salt, hashed = hashed_stored.split(":", 1)
        return hashlib.sha256(f"{salt}{plain}".encode()).hexdigest() == hashed
    except ValueError:
        return False


async def get_user(db: AsyncSession, user_id: int) -> User | None:
    """Busca usuário por ID. Retorna None se não existir."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Busca usuário por email (case-insensitive)."""
    result = await db.execute(
        select(User).where(User.email == email.strip().lower())
    )
    return result.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    """Busca usuário por username."""
    result = await db.execute(
        select(User).where(User.username == username.strip())
    )
    return result.scalars().first()


async def get_users(
    db: AsyncSession, skip: int = 0, limit: int = 20
) -> tuple[list[User], int]:
    """Lista usuários com paginação. Retorna (items, total)."""
    # Limite máximo de 100 por request — previne dump massivo de dados (OWASP A01)
    limit = min(limit, 100)

    count_result = await db.execute(select(func.count()).select_from(User))
    total = count_result.scalar_one()

    result = await db.execute(
        select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
    )
    return result.scalars().all(), total


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    """Cria novo usuário com senha hasheada."""
    # Verifica duplicidade antes de inserir (retorna 409 na rota, não 500)
    if await get_user_by_email(db, data.email):
        raise ValueError(f"Email já cadastrado: {data.email}")
    if await get_user_by_username(db, data.username):
        raise ValueError(f"Username já em uso: {data.username}")

    user = User(
        username=data.username.strip(),
        email=data.email.strip().lower(),
        hashed_password=_hash_password(data.password),
    )
    db.add(user)
    await db.flush()    # INSERT sem commit — commit ocorre em get_db()
    await db.refresh(user)
    return user


async def update_user(
    db: AsyncSession, user_id: int, data: UserUpdate
) -> User | None:
    """Atualiza campos do usuário. Retorna None se não encontrado."""
    user = await get_user(db, user_id)
    if not user:
        return None

    update_data = data.model_dump(exclude_unset=True)   # só campos enviados
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.flush()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """Remove usuário. Retorna True se deletou, False se não encontrou."""
    user = await get_user(db, user_id)
    if not user:
        return False
    await db.delete(user)
    await db.flush()
    return True
