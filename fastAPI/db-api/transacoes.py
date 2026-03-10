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
