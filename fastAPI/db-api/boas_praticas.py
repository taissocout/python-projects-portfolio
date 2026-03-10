"""
boas_praticas.py — Demonstracao de boas praticas com Python DB API

1. Sempre usar parametros ? (nunca f-string em SQL)
2. Fechar conexoes e cursores
3. Usar context manager
4. Nunca logar dados sensiveis
5. Tratar excecoes especificas
"""
import sqlite3
from database import get_db


# ── 1. PARAMETROS SEGUROS ────────────────────────────────────────────────────

def busca_segura(conn: sqlite3.Connection, email: str):
    """CORRETO: usa ? para parametros — previne SQL Injection."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    return cursor.fetchone()

def busca_insegura_EXEMPLO_PROIBIDO(conn, email: str):
    """
    ERRADO (NUNCA FAZER): f-string em SQL.
    Vulneravel a SQL Injection: email = "x' OR '1'='1"
    Aqui apenas como documentacao do que NAO fazer.
    """
    # cursor.execute(f"SELECT * FROM usuarios WHERE email = '{email}'")  # PROIBIDO
    pass


# ── 2. CONTEXT MANAGER ────────────────────────────────────────────────────────

def usar_context_manager(db_path: str = "blog.db"):
    """with sqlite3.connect() fecha a conexao automaticamente."""
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM usuarios")
        row = cursor.fetchone()
        print(f"[CM] Total de usuarios: {row['total']}")
    # conexao fechada automaticamente aqui


# ── 3. TRATAMENTO DE EXCECOES ─────────────────────────────────────────────────

def inserir_com_tratamento(conn: sqlite3.Connection, nome: str, email: str) -> int | None:
    """Trata erros especificos: IntegrityError para UNIQUE constraint."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, email) VALUES (?, ?)",
            (nome.strip(), email.strip().lower())
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        print(f"[AVISO] Email '{email}' ja cadastrado.")
        conn.rollback()
        return None
    except sqlite3.Error as e:
        print(f"[ERRO DB] {type(e).__name__}: {e}")
        conn.rollback()
        return None
