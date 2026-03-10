from fastapi import APIRouter, HTTPException
from app.schemas.post import PostCreate, PostResponse

router = APIRouter(prefix="/posts", tags=["posts"])

posts_db: list[dict] = []
_id_counter = 1


@router.get("/", response_model=list[PostResponse])
def list_posts():
    return posts_db


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int):
    post = next((p for p in posts_db if p["id"] == post_id), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post não encontrado")
    return post


@router.post("/", response_model=PostResponse, status_code=201)
def create_post(post: PostCreate):
    global _id_counter
    new_post = {"id": _id_counter, **post.model_dump()}
    posts_db.append(new_post)
    _id_counter += 1
    return new_post


@router.delete("/{post_id}", status_code=204)
def delete_post(post_id: int):
    global posts_db
    post = next((p for p in posts_db if p["id"] == post_id), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post não encontrado")
    posts_db = [p for p in posts_db if p["id"] != post_id]
