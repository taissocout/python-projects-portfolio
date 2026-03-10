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


def transferir_post(conn: sqlite3.Connection,
                    post_id: int, novo_usuario_id: int) -> bool:
    """
    Transfere autoria de um post — operacao que exige atomicidade.
    Se qualquer verificacao falhar, tudo e revertido.
    """
    with transacao(conn) as cursor:
        cursor.execute("SELECT id FROM posts WHERE id = ?", (post_id,))
        if not cursor.fetchone():
            raise ValueError(f"Post {post_id} nao existe.")

        cursor.execute("SELECT id FROM usuarios WHERE id = ?", (novo_usuario_id,))
        if not cursor.fetchone():
            raise ValueError(f"Usuario {novo_usuario_id} nao existe.")

        cursor.execute(
            "UPDATE posts SET usuario_id = ? WHERE id = ?",
            (novo_usuario_id, post_id)
        )
    return True


def demo_rollback(conn: sqlite3.Connection):
    """Demonstra rollback: simula erro no meio de uma transacao."""
    print("\n[DEMO] Iniciando transacao que vai falhar...")
    try:
        with transacao(conn) as cursor:
            cursor.execute(
                "INSERT INTO usuarios (nome, email) VALUES (?, ?)",
                ("Usuario Fantasma", "fantasma@dev.com")
            )
            print("[DEMO] Primeiro INSERT ok — forcando erro agora...")
            raise Exception("Erro simulado — ROLLBACK deve ser executado!")
    except Exception:
        pass  # rollback ja foi feito pelo context manager

    # Verifica que o usuario NAO foi inserido
    cursor2 = conn.cursor()
    cursor2.execute("SELECT * FROM usuarios WHERE email = ?", ("fantasma@dev.com",))
    resultado = cursor2.fetchone()
    print(f"[DEMO] Usuario fantasma no banco: {resultado}")  # deve ser None
