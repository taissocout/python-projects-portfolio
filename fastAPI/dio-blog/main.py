# ==========================================================
# FASTAPI - EXEMPLO SIMPLES COM JSON, COOKIE E HEADER
# ==========================================================
#
# O que este código mostra:
#
# 1) Como criar uma API com FastAPI
# 2) Como receber dados com POST
# 3) Como listar dados com GET
# 4) Como retornar dados em formato JSON
# 5) Como ler Cookie e Header
# 6) Como testar tudo no Insomnia
#
# ==========================================================


# ----------------------------------------------------------
# IMPORTAÇÕES
# ----------------------------------------------------------
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Cookie, FastAPI, Header, Response, status
from pydantic import BaseModel


# ----------------------------------------------------------
# CRIANDO A APLICAÇÃO FASTAPI
# ----------------------------------------------------------
app = FastAPI()


# ----------------------------------------------------------
# BANCO DE DADOS FALSO
# ----------------------------------------------------------
# Isso é só uma lista de dicionários para simular um banco.
fake_db = [
    {"title": "Criando uma aplicação com Django", "date": datetime.now(UTC), "published": True},
    {"title": "Criando uma aplicação com FastAPI", "date": datetime.now(UTC), "published": True},
    {"title": "Criando uma aplicação com Flask", "date": datetime.now(UTC), "published": True},
    {"title": "Criando uma aplicação com Starlette", "date": datetime.now(UTC), "published": True},
]


# ----------------------------------------------------------
# MODELO DO POST
# ----------------------------------------------------------
# BaseModel valida os dados que chegam no body da requisição.
class Post(BaseModel):
    title: str
    date: datetime = datetime.now(UTC)
    published: bool = False


# ----------------------------------------------------------
# ROTA POST - CRIAR POST
# ----------------------------------------------------------
# Aqui o usuário envia um JSON no body da requisição.
#
# Exemplo no Insomnia:
# {
#   "title": "Aprendendo FastAPI",
#   "date": "2026-03-08T12:00:00Z",
#   "published": true
# }
#
# O FastAPI transforma esse JSON em um objeto Post.
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    # Converte o modelo para dicionário e salva na fake_db
    fake_db.append(post.model_dump())

    # Aqui retornamos um dicionário Python.
    # O FastAPI converte isso automaticamente para JSON.
    return {
        "message": "Post criado com sucesso!",
        "post": post
    }


# ----------------------------------------------------------
# ROTA GET - LISTAR POSTS
# ----------------------------------------------------------
# Aqui usamos:
#
# - response: para enviar cookie na resposta
# - published: filtra posts publicados ou não
# - limit: limita quantidade de posts
# - skip: pula alguns posts
# - ads_id: lê cookie da requisição
# - user_agent: lê o header User-Agent
#
# IMPORTANTE:
# FastAPI entende automaticamente que user_agent
# corresponde ao header "User-Agent".
@app.get("/posts")
def read_posts(
    response: Response,
    published: bool = True,
    limit: int = 10,
    skip: int = 0,
    ads_id: Annotated[str | None, Cookie()] = None,
    user_agent: Annotated[str | None, Header()] = None,
):
    # Envia um cookie para o cliente
    response.set_cookie(key="ads_id", value="123")

    # Prints para aparecer no terminal do servidor
    print(f"Cookie ads_id: {ads_id}")
    print(f"User-Agent: {user_agent}")

    # Filtrando os posts
    posts_filtrados = [
        post
        for post in fake_db[skip : skip + limit]
        if post["published"] == published
    ]

    # Retornando um dicionário Python.
    # Isso vira JSON automaticamente no FastAPI.
    return {
        "total": len(posts_filtrados),
        "skip": skip,
        "limit": limit,
        "published": published,
        "items": posts_filtrados
    }


# ----------------------------------------------------------
# ROTA GET - POSTS POR FRAMEWORK
# ----------------------------------------------------------
# framework é um path parameter, ou seja,
# vem direto da URL.
#
# Exemplo:
# /posts/FastAPI
@app.get("/posts/{framework}")
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
        ]
    }