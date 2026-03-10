"""
usuarios.py — CRUD de usuários
Operações: inserir, buscar, atualizar, remover
"""

import sqlite3


def inserir_usuario(conn: sqlite3.Connection, nome: str, email: str) -> int:
    """Insere um usuário e retorna o ID gerado."""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nome, email) VALUES (?, ?)",
        (nome.strip(), email.strip().lower())   # sanitização básica
    )
    conn.commit()
    return cursor.lastrowid


def buscar_usuarios(conn: sqlite3.Connection) -> list:
    """Retorna todos os usuários."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios ORDER BY criado_em DESC")
    return cursor.fetchall()


def buscar_usuario_por_id(conn: sqlite3.Connection, usuario_id: int):
    """Retorna um usuário pelo ID ou None."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
    return cursor.fetchone()


def atualizar_usuario(conn: sqlite3.Connection, usuario_id: int, nome: str, email: str) -> bool:
    """Atualiza nome e email de um usuário. Retorna True se encontrado."""
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET nome = ?, email = ? WHERE id = ?",
        (nome.strip(), email.strip().lower(), usuario_id)
    )
    conn.commit()
    return cursor.rowcount > 0


def remover_usuario(conn: sqlite3.Connection, usuario_id: int) -> bool:
    """Remove um usuário pelo ID. Retorna True se removido."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
    conn.commit()
    return cursor.rowcount > 0
