"""
usuarios.py — Operacoes de usuarios no banco
"""
import sqlite3


def inserir_usuario(conn: sqlite3.Connection, nome: str, email: str) -> int:
    """
    Insere usuario usando parametro ? (previne SQL Injection).
    Retorna o ID do registro inserido.
    """
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nome, email) VALUES (?, ?)",
        (nome.strip(), email.strip().lower())
    )
    conn.commit()
    print(f"[INSERT] Usuario '{nome}' inserido com ID={cursor.lastrowid}")
    return cursor.lastrowid


def atualizar_usuario(conn: sqlite3.Connection, usuario_id: int,
                      nome: str, email: str) -> bool:
    """
    UPDATE com WHERE — cursor.rowcount indica quantas linhas foram afetadas.
    Retorna True se encontrou e atualizou, False se nao encontrou.
    """
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET nome = ?, email = ? WHERE id = ?",
        (nome.strip(), email.strip().lower(), usuario_id)
    )
    conn.commit()
    afetadas = cursor.rowcount
    print(f"[UPDATE] usuarios — {afetadas} linha(s) afetada(s)")
    return afetadas > 0


def remover_usuario(conn: sqlite3.Connection, usuario_id: int) -> bool:
    """
    DELETE com WHERE. ON DELETE CASCADE no schema garante que os posts
    do usuario tambem sao removidos automaticamente.
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
    conn.commit()
    removido = cursor.rowcount > 0
    print(f"[DELETE] Usuario {usuario_id} {'removido' if removido else 'nao encontrado'}")
    return removido


def inserir_usuarios_lote(conn: sqlite3.Connection,
                          usuarios: list[tuple[str, str]]) -> int:
    """
    executemany — muito mais eficiente que N chamadas a execute().
    Uma unica transacao para todos os registros.
    usuarios = [("Nome", "email@x.com"), ...]
    """
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT OR IGNORE INTO usuarios (nome, email) VALUES (?, ?)",
        [(n.strip(), e.strip().lower()) for n, e in usuarios]
    )
    conn.commit()
    print(f"[BATCH] {cursor.rowcount} usuario(s) inseridos em lote")
    return cursor.rowcount


def buscar_todos_usuarios(conn: sqlite3.Connection) -> list:
    """SELECT * com ORDER BY."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios ORDER BY nome ASC")
    return cursor.fetchall()


def buscar_usuario_por_id(conn: sqlite3.Connection, uid: int):
    """fetchone — retorna um registro ou None."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (uid,))
    return cursor.fetchone()


def buscar_usuario_por_email(conn: sqlite3.Connection, email: str):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email.lower(),))
    return cursor.fetchone()
