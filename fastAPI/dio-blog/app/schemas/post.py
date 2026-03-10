from pydantic import BaseModel, Field


class PostCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    content: str = Field(..., min_length=10)
    author: str = Field(..., min_length=2, max_length=50)


class PostResponse(PostCreate):
    id: int

    model_config = {"from_attributes": True}
