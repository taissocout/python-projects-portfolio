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


def atualizar_post(conn: sqlite3.Connection, post_id: int, titulo: str,
                   conteudo: str, publicado: bool) -> bool:
    """Atualiza um post pelo ID. Retorna True se encontrado."""
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE posts SET titulo = ?, conteudo = ?, publicado = ? WHERE id = ?",
        (titulo.strip(), conteudo.strip(), int(publicado), post_id)
    )
    conn.commit()
    return cursor.rowcount > 0


def publicar_post(conn: sqlite3.Connection, post_id: int) -> bool:
    """Marca um post como publicado (UPDATE parcial — apenas um campo)."""
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE posts SET publicado = 1 WHERE id = ?",
        (post_id,)
    )
    conn.commit()
    return cursor.rowcount > 0


def remover_post(conn: sqlite3.Connection, post_id: int) -> bool:
    """Remove um post pelo ID."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    return cursor.rowcount > 0


def remover_posts_do_usuario(conn: sqlite3.Connection, usuario_id: int) -> int:
    """Remove todos os posts de um usuario. Retorna quantidade removida."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM posts WHERE usuario_id = ?", (usuario_id,))
    conn.commit()
    print(f"[DELETE] {cursor.rowcount} post(s) do usuario {usuario_id} removidos")
    return cursor.rowcount


def inserir_posts_lote(conn: sqlite3.Connection, posts: list[dict]) -> int:
    """
    Batch insert de posts. Mais eficiente que insercoes individuais.
    posts = [{"titulo": ..., "conteudo": ..., "usuario_id": ..., "publicado": bool}]
    """
    dados = [
        (p["titulo"].strip(), p.get("conteudo", "").strip(),
         int(p.get("publicado", False)), p["usuario_id"])
        for p in posts
    ]
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO posts (titulo, conteudo, publicado, usuario_id) VALUES (?, ?, ?, ?)",
        dados
    )
    conn.commit()
    print(f"[BATCH] {cursor.rowcount} post(s) inseridos em lote")
    return cursor.rowcount


def buscar_posts_publicados(conn: sqlite3.Connection) -> list:
    """JOIN com usuarios para retornar nome do autor junto com o post."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.titulo, p.conteudo, p.criado_em, u.nome AS autor
        FROM posts p
        INNER JOIN usuarios u ON p.usuario_id = u.id
        WHERE p.publicado = 1
        ORDER BY p.criado_em DESC
    """)
    return cursor.fetchall()


def buscar_posts_do_usuario(conn: sqlite3.Connection, usuario_id: int) -> list:
    """Filtragem por usuario_id com WHERE."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM posts WHERE usuario_id = ? ORDER BY criado_em DESC",
        (usuario_id,)
    )
    return cursor.fetchall()


def buscar_post_por_id(conn: sqlite3.Connection, post_id: int):
    cursor = conn.cursor()
    cursor.execute(
        """SELECT p.*, u.nome AS autor
           FROM posts p JOIN usuarios u ON p.usuario_id = u.id
           WHERE p.id = ?""",
        (post_id,)
    )
    return cursor.fetchone()


def contar_posts(conn: sqlite3.Connection, publicado: bool | None = None) -> int:
    """SELECT COUNT — funcoes de agregacao."""
    cursor = conn.cursor()
    if publicado is None:
        cursor.execute("SELECT COUNT(*) FROM posts")
    else:
        cursor.execute("SELECT COUNT(*) FROM posts WHERE publicado = ?", (int(publicado),))
    return cursor.fetchone()[0]
