# ==========================================================
# API COM FASTAPI - POSTS
# ==========================================================
#
# Neste exemplo vamos usar:
#
# - FastAPI
# - BaseModel do Pydantic
# - status code
# - query parameters
# - path parameters
# - cookie
# - header
# - response
#
# ==========================================================


# ----------------------------------------------------------
# IMPORTAÇÕES
# ----------------------------------------------------------
# datetime e UTC para salvar datas em UTC
from datetime import UTC, datetime

# Annotated ajuda a deixar os parâmetros mais explícitos
from typing import Annotated

# Importações do FastAPI
from fastapi import Cookie, FastAPI, Header, Response, status

# BaseModel para validar o corpo da requisição
from pydantic import BaseModel


# ----------------------------------------------------------
# INSTÂNCIA DA APLICAÇÃO
# ----------------------------------------------------------
app = FastAPI()


# ----------------------------------------------------------
# BANCO DE DADOS FAKE
# ----------------------------------------------------------
# Aqui usamos uma lista para simular um banco de dados.
fake_db = [
    {"title": "Criando uma aplicação com Django", "date": datetime.now(UTC), "published": True},
    {"title": "Criando uma aplicação com FastAPI", "date": datetime.now(UTC), "published": True},
    {"title": "Criando uma aplicação com Flask", "date": datetime.now(UTC), "published": True},
    {"title": "Criando uma aplicação com Starlette", "date": datetime.now(UTC), "published": True},
]


# ----------------------------------------------------------
# MODEL DO POST
# ----------------------------------------------------------
# BaseModel valida os dados recebidos no body da requisição.
class Post(BaseModel):
    title: str
    date: datetime = datetime.now(UTC)
    published: bool = False


# ----------------------------------------------------------
# ROTA PARA CRIAR UM POST
# ----------------------------------------------------------
# status_code=201 indica que um recurso foi criado com sucesso.
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    # model_dump() é o modo mais atual para transformar em dicionário
    fake_db.append(post.model_dump())

    return {
        "message": "Post criado com sucesso!",
        "post": post
    }


# ----------------------------------------------------------
# ROTA PARA LISTAR POSTS
# ----------------------------------------------------------
# Aqui vamos usar:
#
# - response: para manipular cookies na resposta
# - published: filtrar posts publicados
# - limit: limitar quantidade
# - skip: pular registros
# - ads_id: pegar valor de cookie
# - user_agent: pegar valor do header
#
# IMPORTANTE:
# user_agent precisa ser escrito assim no parâmetro,
# mas o FastAPI entende automaticamente o header "User-Agent".
@app.get("/posts")
def read_posts(
    response: Response,
    published: bool,
    limit: int,
    skip: int = 0,
    ads_id: Annotated[str | None, Cookie()] = None,
    user_agent: Annotated[str | None, Header()] = None,
):
    # definindo um cookie na resposta
    response.set_cookie(key="ads_id", value="123")

    # prints para aparecer no terminal do servidor
    print(f"Cookie ads_id: {ads_id}")
    print(f"User-Agent: {user_agent}")

    # retornando apenas os posts filtrados
    return [
        post
        for post in fake_db[skip : skip + limit]
        if post["published"] is published
    ]


# ----------------------------------------------------------
# ROTA COM PATH PARAMETER
# ----------------------------------------------------------
# Aqui o framework é recebido diretamente pela URL.
@app.get("/posts/{framework}")
def read_framework_posts(framework: str):
    return {
        "posts": [
            {
                "title": f"Criando uma aplicação com {framework}",
                "date": datetime.now(UTC),
            },
            {
                "title": f"Boas práticas com {framework}",
                "date": datetime.now(UTC),
            },
        ]
    }