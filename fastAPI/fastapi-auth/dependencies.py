"""
dependencies.py — Dependências de autenticação para injeção nas rotas.

Aula 2: Uso de tokens para autenticação (19:46)
Conceito central:
  get_current_user() é o guard das rotas protegidas.
  Qualquer rota que receba Depends(get_current_user) exige Bearer token válido.

Fluxo:
  Request → Header Authorization: Bearer <token>
             → oauth2_scheme extrai o token
             → decode_token valida JWT
             → get_user_by_id busca o user no banco
             → retorna User ou levanta 401

Segurança (OWASP A07):
  - Valida expiração do JWT (jose faz isso automaticamente)
  - Verifica tipo do token: "access" — refresh token não pode autenticar rotas
  - Verifica is_active: usuário desativado não autentica mesmo com token válido
  - WWW-Authenticate header no 401: RFC 6750 compliance
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import User
from services.auth_service import decode_token, get_user_by_id

# tokenUrl aponta para a rota de login — alimenta o "Authorize" no Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency que protege rotas.
    Uso: async def minha_rota(user: User = Depends(get_current_user))
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado.",
        # RFC 6750: WWW-Authenticate obrigatório no 401 de Bearer auth
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    # Garante que é access token — refresh token não autentica rotas (OWASP A07)
    if payload.type != "access":
        raise credentials_exception

    user = await get_user_by_id(db, int(payload.sub))
    if user is None:
        raise credentials_exception

    # Usuário desativado — mesmo com token válido, não acessa (OWASP A07)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada. Entre em contato com o suporte.",
        )

    return user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency para rotas restritas a superusuários."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores.",
        )
    return current_user
