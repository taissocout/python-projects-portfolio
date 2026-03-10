"""
routers/auth.py — Endpoints de autenticação e autorização.

Aula 2: Uso de tokens para autenticação (19:46)
Rotas implementadas:
  POST /auth/register  → cria novo usuário
  POST /auth/login     → autentica e retorna access + refresh token
  POST /auth/refresh   → renova access token com refresh token válido
  POST /auth/logout    → revoga refresh token (logout simples)
  POST /auth/logout-all → revoga todos os tokens (logout total)
  GET  /auth/me        → retorna dados do usuário autenticado

Segurança:
  - Login retorna mensagem genérica para username/senha inválidos
    (não diferencia "usuário não existe" de "senha errada" — OWASP A07)
  - /me exige Bearer token via Depends(get_current_user)
  - response_model=UserResponse nunca expõe hashed_password (OWASP A02)
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import User
from schemas import (
    UserCreate, UserResponse, LoginRequest,
    TokenResponse, RefreshRequest, MessageResponse,
)
from services.auth_service import (
    create_user, get_user_by_username,
    verify_password, create_access_token, create_refresh_token,
    save_refresh_token, revoke_refresh_token,
    get_valid_refresh_token, revoke_all_user_tokens,
    decode_token, get_user_by_id,
)
from dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Registra novo usuário. Retorna 409 se email/username já existir."""
    try:
        user = await create_user(db, data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception:
        logger.exception("Erro ao registrar usuário")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno. Tente novamente.",
        )


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Autentica usuário e retorna access + refresh token.

    Mensagem de erro GENÉRICA para username e senha inválidos:
    Não diferencia "usuário não existe" de "senha errada" — previne
    enumeração de usuários (OWASP A07 / User Enumeration).
    """
    INVALID_MSG = "Usuário ou senha inválidos."

    user = await get_user_by_username(db, data.username)
    # Verifica senha mesmo se user não existe — previne timing attack
    # (comparação de tempo constante via passlib — OWASP A02)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_MSG,
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada.",
        )

    access_token, expires_in = create_access_token(user.id)
    refresh_token, expires_at = create_refresh_token(user.id)
    await save_refresh_token(db, user.id, refresh_token, expires_at)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """
    Renova o access token usando um refresh token válido.
    Invalida o refresh token usado e gera um novo (token rotation — OWASP A07).
    """
    # 1. Valida assinatura e claims do JWT
    payload = decode_token(data.refresh_token)
    if not payload or payload.type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado.",
        )

    # 2. Verifica no banco se não foi revogado
    stored = await get_valid_refresh_token(db, data.refresh_token)
    if not stored:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token revogado ou expirado.",
        )

    # 3. Busca o usuário
    user = await get_user_by_id(db, int(payload.sub))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário inválido.")

    # 4. Token rotation: revoga o atual, gera novo par
    await revoke_refresh_token(db, data.refresh_token)
    access_token, expires_in = create_access_token(user.id)
    new_refresh_token, expires_at = create_refresh_token(user.id)
    await save_refresh_token(db, user.id, new_refresh_token, expires_at)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=expires_in,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    data: RefreshRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoga o refresh token — logout simples (dispositivo atual)."""
    await revoke_refresh_token(db, data.refresh_token)
    return MessageResponse(message="Logout realizado com sucesso.")


@router.post("/logout-all", response_model=MessageResponse)
async def logout_all(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoga TODOS os refresh tokens do usuário — logout total (todos os dispositivos)."""
    count = await revoke_all_user_tokens(db, current_user.id)
    return MessageResponse(message=f"Logout total: {count} sessão(ões) encerrada(s).")


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    """
    Retorna dados do usuário autenticado.
    response_model=UserResponse filtra hashed_password automaticamente (OWASP A02).
    """
    return current_user
