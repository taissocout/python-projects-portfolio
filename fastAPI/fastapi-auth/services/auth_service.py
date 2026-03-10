"""
services/auth_service.py — Lógica de autenticação: hash, JWT, verificação.

Aula 2: Uso de tokens para autenticação (19:46)

Fluxo completo de autenticação:
  1. Registro: UserCreate → hash bcrypt → salva no banco
  2. Login: username/password → verifica hash → gera access + refresh token
  3. Request protegido: Bearer token → decodifica JWT → valida claims → retorna user
  4. Refresh: refresh_token → valida no banco → gera novo access token
  5. Logout: revoga refresh_token no banco

Segurança (OWASP A07 — Auth Failures):
  - bcrypt com custo padrão (12 rounds) — resistente a brute force
  - JWT com expiração curta (access: 30min, refresh: 7 dias)
  - Refresh token armazenado no banco para permitir revogação
  - Sub do JWT é user_id (int) — não email (evita enumeração)
  - Tipo do token no payload ("access"/"refresh") — evita uso de refresh como access
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import User, RefreshToken
from schemas import UserCreate, TokenPayload
from config import get_settings

settings = get_settings()

# CryptContext com bcrypt — custo adaptativo, resistente a GPU cracking (OWASP A02)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Hash de senha ─────────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Gera hash bcrypt da senha plaintext."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verifica senha contra hash armazenado.
    Usa comparação em tempo constante — previne timing attacks (OWASP A02).
    """
    return pwd_context.verify(plain, hashed)


# ── JWT ───────────────────────────────────────────────────────────────────────

def create_access_token(user_id: int) -> tuple[str, int]:
    """
    Gera access token JWT de curta duração.
    Retorna (token, expires_in_seconds).
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",   # distingue de refresh (OWASP A07)
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return token, settings.access_token_expire_minutes * 60


def create_refresh_token(user_id: int) -> tuple[str, datetime]:
    """
    Gera refresh token JWT de longa duração.
    Retorna (token, expires_at datetime).
    """
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return token, expire


def decode_token(token: str) -> Optional[TokenPayload]:
    """
    Decodifica e valida JWT.
    Retorna None se inválido ou expirado — nunca levanta exceção para o cliente.
    """
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return TokenPayload(**payload)
    except JWTError:
        return None


# ── CRUD de usuário ───────────────────────────────────────────────────────────

async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(
        select(User).where(User.username == username.strip())
    )
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(
        select(User).where(User.email == email.strip().lower())
    )
    return result.scalars().first()


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    """Cria usuário com senha hasheada."""
    if await get_user_by_email(db, data.email):
        raise ValueError("Email já cadastrado.")
    if await get_user_by_username(db, data.username):
        raise ValueError("Username já em uso.")

    user = User(
        username=data.username.strip(),
        email=data.email.strip().lower(),
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


# ── Operações de token ────────────────────────────────────────────────────────

async def save_refresh_token(
    db: AsyncSession, user_id: int, token: str, expires_at: datetime
) -> RefreshToken:
    """Persiste refresh token no banco para permitir revogação."""
    rt = RefreshToken(token=token, user_id=user_id, expires_at=expires_at)
    db.add(rt)
    await db.flush()
    return rt


async def revoke_refresh_token(db: AsyncSession, token: str) -> bool:
    """Marca refresh token como revogado (logout)."""
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token == token,
            RefreshToken.is_revoked == False,
        )
    )
    rt = result.scalars().first()
    if not rt:
        return False
    rt.is_revoked = True
    await db.flush()
    return True


async def get_valid_refresh_token(
    db: AsyncSession, token: str
) -> Optional[RefreshToken]:
    """Busca refresh token válido (não revogado e não expirado)."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token == token,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > now,
        )
    )
    return result.scalars().first()


async def revoke_all_user_tokens(db: AsyncSession, user_id: int) -> int:
    """Revoga todos os refresh tokens de um usuário (logout total)."""
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False,
        )
    )
    tokens = result.scalars().all()
    for rt in tokens:
        rt.is_revoked = True
    await db.flush()
    return len(tokens)
