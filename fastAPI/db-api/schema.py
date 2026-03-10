"""
schema.py — Definição e criação das tabelas do banco
"""

import sqlite3


def criar_tabela_usuarios(conn: sqlite3.Connection) -> None:
    """
    CREATE TABLE IF NOT EXISTS — não falha se a tabela já existir.
    Usa tipos SQLite: INTEGER, TEXT, REAL, BLOB, NULL.
    """
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nome      TEXT    NOT NULL,
            email     TEXT    NOT NULL UNIQUE,
            criado_em TEXT    DEFAULT (datetime('now', 'localtime'))
        )
    """)
    conn.commit()
    print("[DB] Tabela 'usuarios' criada/verificada.")
