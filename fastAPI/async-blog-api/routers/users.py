"""
routers/users.py — Rotas CRUD assíncronas para usuários.

Aula: Implementação final do CRUD (09:43)
Conceitos:
  - APIRouter com prefix e tags — organização modular
  - Depends(get_db) — injeção de dependência da sessão assíncrona
  - HTTPException com status codes semânticos (409, 404, 403)
  - response_model=UserResponse — nunca expõe hashed_password na resposta
  - status_code=status.HTTP_201_CREATED — código correto para criação

Segurança:
  - response_model filtra campos sensíveis automaticamente (OWASP A02)
  - Erros genéricos ao cliente — detalhes apenas em log interno (OWASP A09)
  - Limite de paginação máximo 100 aplicado na camada de serviço (OWASP A01)
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import UserCreate, UserUpdate, UserResponse, PaginatedResponse
import crud

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=PaginatedResponse)
async def list_users(
    skip:  int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Lista usuários com paginação."""
    items, total = await crud.get_users(db, skip=skip, limit=limit)
    return {
        "total": total, "skip": skip, "limit": limit,
        "items": [UserResponse.model_validate(u) for u in items],
    }


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Retorna usuário por ID."""
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Cria novo usuário. Retorna 409 se email/username já existir."""
    try:
        user = await crud.create_user(db, data)
        return user
    except ValueError as e:
        # ValueError vem do crud — conflito de unicidade
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception:
        logger.exception("Erro inesperado ao criar usuário")
        # Mensagem genérica ao cliente — detalhe apenas no log (OWASP A09)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno. Tente novamente.",
        )


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, data: UserUpdate, db: AsyncSession = Depends(get_db)
):
    """Atualiza parcialmente um usuário (PATCH semântico)."""
    user = await crud.update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Remove usuário e todos os posts associados (CASCADE)."""
    deleted = await crud.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
