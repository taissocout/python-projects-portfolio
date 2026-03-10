from fastapi import FastAPI
from datetime import datetime, timezone
from pydantic import BaseModel

app = FastAPI()

UTC = timezone.utc

fake_db = [
    {"title": "Criando uma aplicação com Django", "date": datetime.now(UTC), "published": True},
    {"title": "Criando uma aplicação com FastAPI", "date": datetime.now(UTC), "published": True},
    {"title": "Criando uma aplicação com Flask", "date": datetime.now(UTC), "published": True},
    {"title": "Criando uma aplicação com Starlett", "date": datetime.now(UTC), "published": True},
]

class Post(BaseModel):
    title: str
    date: datetime
    published: bool

@app.post("/posts")
def create_post(post: Post):
    fake_db.append(post.dict())
    return {"message": "Post criado com sucesso!"}

@app.get("/posts")
def read_posts(skip: int = 0, limit: int = len(fake_db), published: bool = True):
    return [post for post in fake_db[skip : skip + limit] if post["published"] == published]

@app.get("/posts/{framework}")
def read_framework_posts(framework: str):
    return {
        "posts": [
            {"title": f"Criando uma aplicação com {framework}", "date": datetime.now(UTC)},
            {"title": f"Criando uma aplicação com {framework}", "date": datetime.now(UTC)},
        ]
    }