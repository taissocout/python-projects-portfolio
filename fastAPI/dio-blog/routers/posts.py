# ==========================================================
# ROTAS DE POSTS - APIRouter
# ==========================================================
# Todas as rotas relacionadas a posts ficam aqui.
# O prefix="/posts" faz com que todas as rotas comecem com /posts
# O tags=["posts"] agrupa as rotas na documentação /docs
# ==========================================================

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Cookie, Header, Response, status
from pydantic import BaseModel

# ----------------------------------------------------------
# CRIANDO O ROUTER
# ----------------------------------------------------------
# Em vez de @app.get, usamos @router.get
# O main.py registra esse router no app principal
router = APIRouter(prefix="/posts", tags=["posts"])


# ----------------------------------------------------------
# BANCO DE DADOS FALSO
# ----------------------------------------------------------
fake_db = [
    {"title": "Criando uma aplicação com Django",    "date": datetime.now(UTC), "published": True},
    {"title": "Criando uma aplicação com FastAPI",   "date": datetime.now(UTC), "published": True},
    {"title": "Criando uma aplicação com Flask",     "date": datetime.now(UTC), "published": True},
    {"title": "Criando uma aplicação com Starlette", "date": datetime.now(UTC), "published": True},
]


# ----------------------------------------------------------
# MODELO DO POST
# ----------------------------------------------------------
class Post(BaseModel):
    title: str
    date: datetime = datetime.now(UTC)
    published: bool = False


# ----------------------------------------------------------
# ROTA POST - CRIAR POST
# ----------------------------------------------------------
# URL final: POST /posts/
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    fake_db.append(post.model_dump())
    return {
        "message": "Post criado com sucesso!",
        "post": post,
    }


# ----------------------------------------------------------
# ROTA GET - LISTAR POSTS
# ----------------------------------------------------------
# URL final: GET /posts/
@router.get("/")
def read_posts(
    response: Response,
    published: bool = True,
    limit: int = 10,
    skip: int = 0,
    ads_id: Annotated[str | None, Cookie()] = None,
    user_agent: Annotated[str | None, Header()] = None,
):
    # Envia cookie para o cliente
    response.set_cookie(key="ads_id", value="123")

    # Logs no terminal do servidor
    print(f"Cookie ads_id: {ads_id}")
    print(f"User-Agent: {user_agent}")

    # Filtra posts por published
    posts_filtrados = [
        post
        for post in fake_db[skip : skip + limit]
        if post["published"] == published
    ]

    return {
        "total": len(posts_filtrados),
        "skip": skip,
        "limit": limit,
        "published": published,
        "items": posts_filtrados,
    }


# ----------------------------------------------------------
# ROTA GET - POSTS POR FRAMEWORK
# ----------------------------------------------------------
# URL final: GET /posts/{framework}
@router.get("/{framework}")
def read_framework_posts(framework: str):
    return {
        "framework": framework,
        "posts": [
            {
                "title": f"Criando uma aplicação com {framework}",
                "date": datetime.now(UTC),
                "published": True,
            },
            {
                "title": f"Boas práticas com {framework}",
                "date": datetime.now(UTC),
                "published": True,
            },
        ],
    }
