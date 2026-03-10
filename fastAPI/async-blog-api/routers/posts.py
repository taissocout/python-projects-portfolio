"""
routers/posts.py — Rotas CRUD assíncronas para posts.

Aula: Implementação final do CRUD (09:43)
Conceitos:
  - Query params com validação embutida (ge=0, le=100)
  - 403 Forbidden vs 404 Not Found — semântica correta de status HTTP
  - author_id hardcoded como query param para o projeto de estudo
    (em produção viria do token JWT via Depends(get_current_user))
  - Slug como identificador alternativo ao ID numérico
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import PostCreate, PostUpdate, PostResponse, PaginatedResponse
import crud

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=PaginatedResponse)
async def list_posts(
    skip:           int  = Query(default=0,    ge=0),
    limit:          int  = Query(default=20,   ge=1, le=100),
    published_only: bool = Query(default=True),
    author_id:      int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Lista posts com filtros e paginação."""
    items, total = await crud.get_posts(
        db, skip=skip, limit=limit,
        published_only=published_only, author_id=author_id,
    )
    return {
        "total": total, "skip": skip, "limit": limit,
        "items": [PostResponse.model_validate(p) for p in items],
    }


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    """Retorna post por ID com dados do autor."""
    post = await crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post não encontrado.")
    return post


@router.get("/slug/{slug}", response_model=PostResponse)
async def get_post_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    """Retorna post por slug — útil para URLs amigáveis."""
    post = await crud.get_post_by_slug(db, slug)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post não encontrado.")
    return post


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: PostCreate,
    # Em produção: author_id viria de Depends(get_current_user)
    author_id: int = Query(..., description="ID do autor (temporário — substituir por JWT)"),
    db: AsyncSession = Depends(get_db),
):
    """Cria novo post para o autor especificado."""
    # Verifica se o autor existe antes de criar o post
    author = await crud.get_user(db, author_id)
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Autor não encontrado.")
    try:
        post = await crud.create_post(db, data, author_id=author_id)
        return post
    except Exception:
        logger.exception("Erro ao criar post")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno. Tente novamente.",
        )


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    data: PostUpdate,
    author_id: int = Query(..., description="ID do autor (temporário — substituir por JWT)"),
    db: AsyncSession = Depends(get_db),
):
    """Atualiza post. Apenas o autor pode editar."""
    try:
        post = await crud.update_post(db, post_id, data, author_id=author_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post não encontrado.")
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    author_id: int = Query(..., description="ID do autor (temporário — substituir por JWT)"),
    db: AsyncSession = Depends(get_db),
):
    """Remove post. Apenas o autor pode deletar."""
    try:
        deleted = await crud.delete_post(db, post_id, author_id=author_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post não encontrado.")
