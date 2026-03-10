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
