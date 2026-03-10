"""
usuarios.py — Operacoes de usuarios no banco
"""
import sqlite3


def inserir_usuario(conn: sqlite3.Connection, nome: str, email: str) -> int:
    """
    Insere usuario usando parametro ? (previne SQL Injection).
    Retorna o ID do registro inserido.
    """
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nome, email) VALUES (?, ?)",
        (nome.strip(), email.strip().lower())
    )
    conn.commit()
    print(f"[INSERT] Usuario '{nome}' inserido com ID={cursor.lastrowid}")
    return cursor.lastrowid


def atualizar_usuario(conn: sqlite3.Connection, usuario_id: int,
                      nome: str, email: str) -> bool:
    """
    UPDATE com WHERE — cursor.rowcount indica quantas linhas foram afetadas.
    Retorna True se encontrou e atualizou, False se nao encontrou.
    """
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET nome = ?, email = ? WHERE id = ?",
        (nome.strip(), email.strip().lower(), usuario_id)
    )
    conn.commit()
    afetadas = cursor.rowcount
    print(f"[UPDATE] usuarios — {afetadas} linha(s) afetada(s)")
    return afetadas > 0
