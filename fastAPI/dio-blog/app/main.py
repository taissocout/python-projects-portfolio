from fastapi import FastAPI
from app.routers import posts

app = FastAPI(
    title="DIO Blog API",
    description="Blog API construída com FastAPI — projeto DIO Bootcamp",
    version="0.1.0",
)

app.include_router(posts.router)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "message": "DIO Blog API is running"}
