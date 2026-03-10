"""
database.py — Conexao com SQLite + row_factory
"""
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "blog.db")


def get_connection() -> sqlite3.Connection:
    """Conexao basica sem row_factory."""
    conn = sqlite3.connect(DB_PATH)
    return conn


def get_connection_row(conn: sqlite3.Connection | None = None) -> sqlite3.Connection:
    """
    Conexao com row_factory = sqlite3.Row.
    Permite acessar colunas por nome: row["titulo"] em vez de row[1].
    """
    c = conn or sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def configure_connection(conn: sqlite3.Connection) -> sqlite3.Connection:
    """Aplica PRAGMAs de seguranca e performance."""
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def get_db() -> sqlite3.Connection:
    """
    Factory principal: conexao configurada + row_factory.
    Uso recomendado em producao.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    configure_connection(conn)
    return conn
