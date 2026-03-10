"""
transacoes.py — Gerenciamento de transacoes com Python DB API

ACID em pratica:
  A — Atomicidade: tudo ou nada
  C — Consistencia: banco sempre em estado valido
  I — Isolamento: transacoes nao interferem entre si
  D — Durabilidade: commit = persistido

SQLite por padrao: autocommit OFF ao usar cursor.
"""
import sqlite3
from contextlib import contextmanager
from database import get_db


@contextmanager
def transacao(conn: sqlite3.Connection):
    """
    Context manager para transacoes seguras.
    COMMIT se tudo ok, ROLLBACK automatico em caso de excecao.

    Uso:
        with transacao(conn) as c:
            c.execute(...)
            c.execute(...)
    """
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
        print("[TRANSACAO] COMMIT aplicado com sucesso.")
    except Exception as e:
        conn.rollback()
        print(f"[TRANSACAO] ROLLBACK executado: {e}")
        raise
