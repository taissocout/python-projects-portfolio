"""
crud/posts.py — Operações CRUD assíncronas para posts.

Aula: Operações CRUD assíncronas em APIs RESTful (13:40)
Conceitos:
  - selectinload(): carrega o relacionamento (author) em uma query separada — async safe
  - func.count(): COUNT(*) via SQLAlchemy, sem SQL manual
  - Slug gerado automaticamente a partir do título — URL amigável e única
  - update_data = data.model_dump(exclude_unset=True): PATCH parcial correto
"""
import re
import unicodedata
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from models import Post
from schemas import PostCreate, PostUpdate


def _slugify(title: str) -> str:
    """
    Converte título para slug URL-safe.
    Ex: 'Meu Post #1!' → 'meu-post-1'
    """
    # Normaliza unicode → ASCII
    title = unicodedata.normalize("NFKD", title)
    title = title.encode("ascii", "ignore").decode("ascii")
    title = title.lower().strip()
    title = re.sub(r"[^\w\s-]", "", title)
    title = re.sub(r"[\s_-]+", "-", title)
    title = re.sub(r"^-+|-+$", "", title)
    return title


async def _unique_slug(db: AsyncSession, title: str) -> str:
    """Gera slug único — adiciona sufixo numérico se necessário."""
    base_slug = _slugify(title)
    slug = base_slug
    counter = 1
    while True:
        result = await db.execute(select(Post).where(Post.slug == slug))
        if not result.scalars().first():
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


async def get_post(db: AsyncSession, post_id: int) -> Post | None:
    """Busca post por ID com author carregado."""
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author))   # evita lazy-load em contexto async
        .where(Post.id == post_id)
    )
    return result.scalars().first()


async def get_post_by_slug(db: AsyncSession, slug: str) -> Post | None:
    """Busca post por slug."""
    result = await db.execute(
        select(Post).options(selectinload(Post.author)).where(Post.slug == slug)
    )
    return result.scalars().first()


async def get_posts(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    published_only: bool = True,
    author_id: int | None = None,
) -> tuple[list[Post], int]:
    """Lista posts com filtros e paginação. Retorna (items, total)."""
    limit = min(limit, 100)

    query = select(Post).options(selectinload(Post.author))
    count_query = select(func.count()).select_from(Post)

    if published_only:
        query = query.where(Post.is_published == True)
        count_query = count_query.where(Post.is_published == True)

    if author_id is not None:
        query = query.where(Post.author_id == author_id)
        count_query = count_query.where(Post.author_id == author_id)

    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    result = await db.execute(
        query.offset(skip).limit(limit).order_by(Post.created_at.desc())
    )
    return result.scalars().all(), total


async def create_post(
    db: AsyncSession, data: PostCreate, author_id: int
) -> Post:
    """Cria novo post com slug gerado automaticamente."""
    slug = await _unique_slug(db, data.title)
    post = Post(
        title=data.title.strip(),
        slug=slug,
        content=data.content,
        is_published=data.is_published,
        author_id=author_id,
    )
    db.add(post)
    await db.flush()
    await db.refresh(post)
    return post


async def update_post(
    db: AsyncSession, post_id: int, data: PostUpdate, author_id: int
) -> Post | None:
    """
    Atualiza post. Verifica propriedade — apenas o autor pode editar.
    Retorna None se não encontrado ou sem permissão.
    """
    post = await get_post(db, post_id)
    if not post:
        return None
    # Verificação de ownership — OWASP A01
    if post.author_id != author_id:
        raise PermissionError("Você não tem permissão para editar este post.")

    update_data = data.model_dump(exclude_unset=True)
    if "title" in update_data:
        update_data["slug"] = await _unique_slug(db, update_data["title"])

    for field, value in update_data.items():
        setattr(post, field, value)

    await db.flush()
    await db.refresh(post)
    return post


async def delete_post(
    db: AsyncSession, post_id: int, author_id: int
) -> bool:
    """Remove post. Verifica ownership antes de deletar."""
    post = await get_post(db, post_id)
    if not post:
        return False
    if post.author_id != author_id:
        raise PermissionError("Você não tem permissão para deletar este post.")
    await db.delete(post)
    await db.flush()
    return True
