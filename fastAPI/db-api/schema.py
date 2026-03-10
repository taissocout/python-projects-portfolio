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


def criar_tabela_posts(conn: sqlite3.Connection) -> None:
    """
    Tabela posts com FOREIGN KEY referenciando usuarios.
    Requer PRAGMA foreign_keys=ON para ser validada.
    """
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo     TEXT    NOT NULL,
            conteudo   TEXT,
            publicado  INTEGER DEFAULT 0,
            usuario_id INTEGER NOT NULL,
            criado_em  TEXT    DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                ON DELETE CASCADE
        )
    """)
    conn.commit()
    print("[DB] Tabela 'posts' criada/verificada.")


def criar_schema(conn: sqlite3.Connection) -> None:
    """Inicializa todas as tabelas em ordem de dependencia."""
    criar_tabela_usuarios(conn)
    criar_tabela_posts(conn)
