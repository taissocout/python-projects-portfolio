"""
database.py — Gerenciamento de conexão com SQLite
Segue o padrão Python DB API (PEP 249)
"""

import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "blog.db")


def get_connection() -> sqlite3.Connection:
    """
    Retorna uma conexão com o banco de dados.
    row_factory = sqlite3.Row permite acessar colunas por nome.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row          # acesso por nome de coluna
    conn.execute("PRAGMA journal_mode=WAL") # melhor concorrencia
    conn.execute("PRAGMA foreign_keys=ON")  # integridade referencial
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    """Cria as tabelas se não existirem."""
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nome      TEXT    NOT NULL,
            email     TEXT    NOT NULL UNIQUE,
            criado_em TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS posts (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo     TEXT    NOT NULL,
            conteudo   TEXT,
            publicado  INTEGER DEFAULT 0,
            usuario_id INTEGER NOT NULL,
            criado_em  TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );
    """)

    conn.commit()
    print("[DB] Schema criado/verificado com sucesso.")
