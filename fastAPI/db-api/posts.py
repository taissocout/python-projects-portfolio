"""
posts.py — CRUD de posts + inserção em lote
"""

import sqlite3
from typing import Generator


def inserir_post(conn: sqlite3.Connection, titulo: str, conteudo: str,
                 usuario_id: int, publicado: bool = False) -> int:
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO posts (titulo, conteudo, publicado, usuario_id) VALUES (?, ?, ?, ?)",
        (titulo.strip(), conteudo.strip(), int(publicado), usuario_id)
    )
    conn.commit()
    return cursor.lastrowid


def inserir_posts_em_lote(conn: sqlite3.Connection, posts: list[dict]) -> int:
    """
    Inserção em lote com executemany — mais eficiente para grandes volumes.
    posts = [{"titulo": ..., "conteudo": ..., "usuario_id": ..., "publicado": ...}]
    """
    dados = [
        (p["titulo"], p.get("conteudo", ""), int(p.get("publicado", False)), p["usuario_id"])
        for p in posts
    ]
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO posts (titulo, conteudo, publicado, usuario_id) VALUES (?, ?, ?, ?)",
        dados
    )
    conn.commit()
    return cursor.rowcount


def buscar_posts(conn: sqlite3.Connection, publicado: bool = True) -> list:
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT p.*, u.nome AS autor
        FROM posts p
        JOIN usuarios u ON p.usuario_id = u.id
        WHERE p.publicado = ?
        ORDER BY p.criado_em DESC
        """,
        (int(publicado),)
    )
    return cursor.fetchall()


def buscar_post_por_id(conn: sqlite3.Connection, post_id: int):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT p.*, u.nome AS autor FROM posts p JOIN usuarios u ON p.usuario_id = u.id WHERE p.id = ?",
        (post_id,)
    )
    return cursor.fetchone()


def atualizar_post(conn: sqlite3.Connection, post_id: int, titulo: str,
                   conteudo: str, publicado: bool) -> bool:
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE posts SET titulo = ?, conteudo = ?, publicado = ? WHERE id = ?",
        (titulo.strip(), conteudo.strip(), int(publicado), post_id)
    )
    conn.commit()
    return cursor.rowcount > 0


def remover_post(conn: sqlite3.Connection, post_id: int) -> bool:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    return cursor.rowcount > 0


def gerar_relatorio(conn: sqlite3.Connection) -> Generator:
    """Generator — retorna posts um a um sem carregar tudo na memória."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT p.id, p.titulo, u.nome, p.criado_em FROM posts p JOIN usuarios u ON p.usuario_id = u.id"
    )
    for row in cursor:
        yield dict(row)
