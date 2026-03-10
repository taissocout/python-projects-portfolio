# ==========================================================
# FASTAPI - APLICAÇÃO PRINCIPAL
# ==========================================================
# Este arquivo apenas inicializa o app e registra os routers.
# As rotas ficam em routers/posts.py
# ==========================================================

from fastapi import FastAPI

from routers import posts

app = FastAPI(
    title="DIO Blog API",
    description="Blog API construída com FastAPI — DIO Bootcamp",
    version="0.1.0",
)

# Registra todas as rotas do módulo posts
app.include_router(posts.router)


# ----------------------------------------------------------
# ROTA RAIZ - HEALTH CHECK
# ----------------------------------------------------------
@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "message": "DIO Blog API is running"}
