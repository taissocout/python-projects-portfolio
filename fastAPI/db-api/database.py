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
