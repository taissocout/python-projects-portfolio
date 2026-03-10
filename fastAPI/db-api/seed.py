"""
seed.py — Popula o banco com dados de exemplo para desenvolvimento/testes
"""
from database import get_connection, configure_connection
from schema import criar_schema, resetar_banco
from usuarios import inserir_usuarios_lote
from posts import inserir_posts_lote

USUARIOS_SEED = [
    ("Tais Cout",    "tais@dev.com"),
    ("Caio Souza",   "caio@dev.com"),
    ("Ana Lima",     "ana@dev.com"),
    ("Pedro Alves",  "pedro@dev.com"),
]

def run_seed():
    conn = get_connection()
    conn = configure_connection(conn)
    resetar_banco(conn)

    uids = []
    for nome, email in USUARIOS_SEED:
        from usuarios import inserir_usuario
        uid = inserir_usuario(conn, nome, email)
        uids.append(uid)

    posts_batch = [
        {"titulo": "FastAPI na pratica",   "conteudo": "...", "usuario_id": uids[0], "publicado": True},
        {"titulo": "SQLite com Python",    "conteudo": "...", "usuario_id": uids[0], "publicado": True},
        {"titulo": "Docker do zero",       "conteudo": "...", "usuario_id": uids[1], "publicado": True},
        {"titulo": "Intro ao DevSecOps",   "conteudo": "...", "usuario_id": uids[2], "publicado": False},
        {"titulo": "OWASP Top 10 2025",    "conteudo": "...", "usuario_id": uids[2], "publicado": True},
        {"titulo": "Git workflow pro",     "conteudo": "...", "usuario_id": uids[3], "publicado": True},
    ]
    inserir_posts_lote(conn, posts_batch)
    print("[SEED] Banco populado com sucesso!")
    conn.close()

if __name__ == "__main__":
    run_seed()
