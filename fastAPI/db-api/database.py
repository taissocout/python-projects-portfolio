"""
database.py — Gerenciamento de conexão com SQLite
Padrão: Python DB API (PEP 249)
"""

import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "blog.db")


def get_connection() -> sqlite3.Connection:
    """
    Abre e retorna uma conexão com o banco SQLite.
    Segue o padrão Python DB API (PEP 249).
    """
    conn = sqlite3.connect(DB_PATH)
    return conn


def configure_connection(conn: sqlite3.Connection) -> sqlite3.Connection:
    """Aplica configurações de segurança e performance na conexão."""
    conn.execute("PRAGMA journal_mode=WAL")   # write-ahead log — melhor concorrencia
    conn.execute("PRAGMA foreign_keys=ON")    # ativa integridade referencial
    conn.execute("PRAGMA synchronous=NORMAL") # equilibrio seguranca x velocidade
    return conn
