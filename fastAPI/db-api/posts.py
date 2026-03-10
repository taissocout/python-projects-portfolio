"""
posts.py — Operacoes de posts no banco
"""
import sqlite3


def inserir_post(conn: sqlite3.Connection, titulo: str, conteudo: str,
                 usuario_id: int, publicado: bool = False) -> int:
    """Insere um post vinculado a um usuario existente."""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO posts (titulo, conteudo, publicado, usuario_id) VALUES (?, ?, ?, ?)",
        (titulo.strip(), conteudo.strip(), int(publicado), usuario_id)
    )
    conn.commit()
    print(f"[INSERT] Post '{titulo}' inserido com ID={cursor.lastrowid}")
    return cursor.lastrowid
