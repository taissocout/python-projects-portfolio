"""
autobuilder_v2.py — DIO DB API Project Builder
Autor: taissocout

- git push apos CADA commit
- 11 fases = 11 aulas do modulo
- 4 a 5 commits por fase
- Delays de 20-60s (total ~30min)
- Commits humanizados e profissionais

Uso:
    cd /mnt/storage/Projetos-Python
    python autobuilder_v2.py
"""

import os
import subprocess
import time
import random
import sys
from datetime import datetime

# ── Config ─────────────────────────────────────────────────────────────────
REPO_ROOT   = "/mnt/storage/Projetos-Python"
PROJECT_DIR = os.path.join(REPO_ROOT, "fastAPI", "db-api")
DELAY_MIN   = 20   # segundos
DELAY_MAX   = 55   # segundos

# ── Cores ───────────────────────────────────────────────────────────────────
class C:
    RESET  = "\033[0m";  BOLD   = "\033[1m"
    GREEN  = "\033[92m"; BLUE   = "\033[94m"
    YELLOW = "\033[93m"; RED    = "\033[91m"
    CYAN   = "\033[96m"; GRAY   = "\033[90m"

def ok(m):   print(f"{C.GREEN}  ✔  {m}{C.RESET}")
def info(m): print(f"{C.BLUE}  ●  {m}{C.RESET}")
def warn(m): print(f"{C.YELLOW}  ⚠  {m}{C.RESET}")
def erro(m): print(f"{C.RED}  ✘  {m}{C.RESET}")
def fase(n, t):
    print(f"\n{C.BOLD}{C.CYAN}{'═'*58}")
    print(f"  AULA {n:02d} — {t}")
    print(f"{'═'*58}{C.RESET}")

# ── Git ─────────────────────────────────────────────────────────────────────
def run(cmd, cwd=None):
    r = subprocess.run(cmd, shell=True, cwd=cwd or REPO_ROOT,
                       capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()

def commit_and_push(msg: str):
    """Stage tudo, commit e push imediato."""
    run("git add -A")
    rc, out, err = run(f'git commit -m "{msg}"')
    if rc != 0:
        if "nothing to commit" in (out + err):
            warn("Nada para commitar — pulando.")
            return
        erro(f"Commit falhou: {err}")
        return
    ok(f"Commit: {msg}")

    rc2, _, err2 = run("git push")
    if rc2 != 0:
        warn(f"Push falhou: {err2}")
    else:
        ok("Push enviado para o GitHub.")

def wait(label: str):
    s = random.randint(DELAY_MIN, DELAY_MAX)
    print(f"\n{C.GRAY}  ⏱  {label} — aguardando {s}s...{C.RESET}")
    for i in range(s, 0, -1):
        print(f"\r{C.GRAY}     {i:>3}s {C.RESET}", end="", flush=True)
        time.sleep(1)
    print(f"\r{C.GRAY}     pronto!{' '*10}{C.RESET}")

# ── Escrita ─────────────────────────────────────────────────────────────────
def w(rel: str, content: str):
    path = os.path.join(PROJECT_DIR, rel)
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else PROJECT_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    info(f"Escrito: fastAPI/db-api/{rel}")

def append_file(rel: str, content: str):
    path = os.path.join(PROJECT_DIR, rel)
    with open(path, "a", encoding="utf-8") as f:
        f.write(content)
    info(f"Atualizado: fastAPI/db-api/{rel}")

# ════════════════════════════════════════════════════════════════════════════
# AULA 1 — Introdução aos Bancos de Dados Relacionais (partes 1, 2, 3)
# ════════════════════════════════════════════════════════════════════════════
def aula01():
    fase(1, "Introdução aos Bancos de Dados Relacionais")

    # Commit 1 — estrutura inicial
    os.makedirs(PROJECT_DIR, exist_ok=True)
    w("README.md", """\
# DB API — Banco de Dados Relacionais com Python

Projeto do módulo **Explorando Banco de Dados Relacionais com Python DB API**
do bootcamp DIO — Jornada para o Futuro.

## Objetivo
Praticar o padrão Python DB API (PEP 249) com SQLite, cobrindo CRUD completo,
transações, boas práticas e segurança.

> Status: 🚧 Em andamento
""")
    commit_and_push("docs: adiciona README inicial do modulo db-api")
    wait("Commit 2")

    # Commit 2 — .gitignore e .env.example
    gi = os.path.join(REPO_ROOT, ".gitignore")
    if os.path.exists(gi):
        with open(gi) as f:
            gc = f.read()
        if "db-api/*.db" not in gc:
            with open(gi, "a") as f:
                f.write("\n# db-api\nfastAPI/db-api/*.db\nfastAPI/db-api/.env\n")
            ok(".gitignore atualizado")
    w(".env.example", "DB_PATH=blog.db\nDEBUG=false\n")
    commit_and_push("chore: adiciona .env.example e regras de gitignore para db-api")
    wait("Commit 3")

    # Commit 3 — anotações conceituais em README
    append_file("README.md", """
## Conceitos — Bancos de Dados Relacionais

- **SGBD**: Sistema Gerenciador de Banco de Dados (SQLite, PostgreSQL, MySQL)
- **Tabela**: estrutura que organiza dados em linhas e colunas
- **Chave primária (PK)**: identificador único de cada registro
- **Chave estrangeira (FK)**: referência a PK de outra tabela (integridade referencial)
- **SQL**: linguagem para manipular dados relacionais
- **ACID**: Atomicidade, Consistência, Isolamento, Durabilidade — propriedades de transações
""")
    commit_and_push("docs: documenta conceitos fundamentais de bancos de dados relacionais")
    wait("Commit 4")

    # Commit 4 — requirements
    w("requirements.txt", "python-dotenv>=1.0.0\n")
    commit_and_push("chore: adiciona requirements.txt com dependencias do projeto")

# ════════════════════════════════════════════════════════════════════════════
# AULA 2 — Conectando com o banco de dados
# ════════════════════════════════════════════════════════════════════════════
def aula02():
    fase(2, "Conectando com o banco de dados")

    # Commit 1 — módulo database.py básico
    w("database.py", '''\
"""
database.py — Gerenciamento de conexão com SQLite
Padrão: Python DB API (PEP 249)
"""

import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "blog.db")
''')
    commit_and_push("feat: cria modulo database.py com carregamento de variaveis de ambiente")
    wait("Commit 2")

    # Commit 2 — função get_connection
    append_file("database.py", '''

def get_connection() -> sqlite3.Connection:
    """
    Abre e retorna uma conexão com o banco SQLite.
    Segue o padrão Python DB API (PEP 249).
    """
    conn = sqlite3.connect(DB_PATH)
    return conn
''')
    commit_and_push("feat: implementa get_connection seguindo padrao Python DB API PEP249")
    wait("Commit 3")

    # Commit 3 — PRAGMAs de segurança
    append_file("database.py", '''

def configure_connection(conn: sqlite3.Connection) -> sqlite3.Connection:
    """Aplica configurações de segurança e performance na conexão."""
    conn.execute("PRAGMA journal_mode=WAL")   # write-ahead log — melhor concorrencia
    conn.execute("PRAGMA foreign_keys=ON")    # ativa integridade referencial
    conn.execute("PRAGMA synchronous=NORMAL") # equilibrio seguranca x velocidade
    return conn
''')
    commit_and_push("feat: adiciona configuracoes PRAGMA para seguranca e performance")
    wait("Commit 4")

    # Commit 4 — main.py inicial com teste de conexão
    w("main.py", '''\
"""main.py — ponto de entrada e teste de conexao"""
from database import get_connection, configure_connection

def main():
    conn = get_connection()
    conn = configure_connection(conn)
    print(f"[OK] Conectado ao banco: {conn}")
    conn.close()
    print("[OK] Conexao encerrada com sucesso.")

if __name__ == "__main__":
    main()
''')
    commit_and_push("feat: adiciona main.py com teste de conexao e encerramento seguro")

# ════════════════════════════════════════════════════════════════════════════
# AULA 3 — Criando uma tabela
# ════════════════════════════════════════════════════════════════════════════
def aula03():
    fase(3, "Criando uma tabela")

    # Commit 1 — módulo schema.py
    w("schema.py", '''\
"""
schema.py — Definição e criação das tabelas do banco
"""

import sqlite3
''')
    commit_and_push("feat: cria modulo schema.py para gerenciamento de estrutura do banco")
    wait("Commit 2")

    # Commit 2 — tabela usuarios
    append_file("schema.py", '''

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
''')
    commit_and_push("feat: cria tabela usuarios com PK autoincrement e campo UNIQUE")
    wait("Commit 3")

    # Commit 3 — tabela posts com FK
    append_file("schema.py", '''

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
''')
    commit_and_push("feat: cria tabela posts com FK e ON DELETE CASCADE")
    wait("Commit 4")

    # Commit 4 — integra schema no main
    w("main.py", '''\
"""main.py — conexao + criacao de schema"""
from database import get_connection, configure_connection
from schema import criar_schema

def main():
    conn = get_connection()
    conn = configure_connection(conn)
    criar_schema(conn)
    print("[OK] Banco inicializado com sucesso.")
    conn.close()

if __name__ == "__main__":
    main()
''')
    commit_and_push("refactor: integra criacao de schema ao main.py")

# ════════════════════════════════════════════════════════════════════════════
# AULA 4 — Inserindo registros
# ════════════════════════════════════════════════════════════════════════════
def aula04():
    fase(4, "Inserindo registros")

    w("usuarios.py", '''\
"""
usuarios.py — Operacoes de usuarios no banco
"""
import sqlite3
''')
    commit_and_push("feat: cria modulo usuarios.py para operacoes de CRUD")
    wait("Commit 2")

    append_file("usuarios.py", '''

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
''')
    commit_and_push("feat: implementa insercao de usuario com parametros seguros anti SQL-injection")
    wait("Commit 3")

    w("posts.py", '''\
"""
posts.py — Operacoes de posts no banco
"""
import sqlite3


def inserir_post(conn: sqlite3.Connection, titulo: str, conteudo: str,
                 usuario_id: int, publicado: bool = False) -> int:
    """Insere um post vinculado a um usuario existente."""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO posts (titulo, conteudo, publicado, usuario_id) VALUES (?, ?, ?, ?)",
        (titulo.strip(), conteudo.strip(), int(publicado), usuario_id)
    )
    conn.commit()
    print(f"[INSERT] Post '{titulo}' inserido com ID={cursor.lastrowid}")
    return cursor.lastrowid
''')
    commit_and_push("feat: implementa insercao de posts com validacao de tipo e sanitizacao")
    wait("Commit 4")

    # main atualizado com inserts
    w("main.py", '''\
"""main.py — demonstracao de insercao de registros"""
from database import get_connection, configure_connection
from schema import criar_schema
from usuarios import inserir_usuario
from posts import inserir_post

def main():
    conn = get_connection()
    conn = configure_connection(conn)
    criar_schema(conn)

    uid = inserir_usuario(conn, "Tais Cout", "tais@dev.com")
    inserir_post(conn, "Introducao ao FastAPI", "Conteudo sobre FastAPI...", uid, True)
    inserir_post(conn, "SQLite com Python DB API", "Conteudo sobre SQLite...", uid, False)

    print("[OK] Registros inseridos.")
    conn.close()

if __name__ == "__main__":
    main()
''')
    commit_and_push("feat: atualiza main.py com demonstracao de insercao de usuarios e posts")

# ════════════════════════════════════════════════════════════════════════════
# AULA 5 — Atualizando registros
# ════════════════════════════════════════════════════════════════════════════
def aula05():
    fase(5, "Atualizando registros")

    append_file("usuarios.py", '''

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
''')
    commit_and_push("feat: implementa atualizacao de usuario com verificacao de rowcount")
    wait("Commit 2")

    append_file("posts.py", '''

def atualizar_post(conn: sqlite3.Connection, post_id: int, titulo: str,
                   conteudo: str, publicado: bool) -> bool:
    """Atualiza um post pelo ID. Retorna True se encontrado."""
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE posts SET titulo = ?, conteudo = ?, publicado = ? WHERE id = ?",
        (titulo.strip(), conteudo.strip(), int(publicado), post_id)
    )
    conn.commit()
    return cursor.rowcount > 0
''')
    commit_and_push("feat: implementa atualizacao de posts com retorno de status booleano")
    wait("Commit 3")

    append_file("posts.py", '''

def publicar_post(conn: sqlite3.Connection, post_id: int) -> bool:
    """Marca um post como publicado (UPDATE parcial — apenas um campo)."""
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE posts SET publicado = 1 WHERE id = ?",
        (post_id,)
    )
    conn.commit()
    return cursor.rowcount > 0
''')
    commit_and_push("feat: adiciona publicar_post com UPDATE parcial de campo unico")
    wait("Commit 4")

    w("main.py", '''\
"""main.py — demonstracao de atualizacao de registros"""
from database import get_connection, configure_connection
from schema import criar_schema
from usuarios import inserir_usuario, atualizar_usuario
from posts import inserir_post, atualizar_post, publicar_post

def main():
    conn = get_connection()
    conn = configure_connection(conn)
    criar_schema(conn)

    uid = inserir_usuario(conn, "Tais Cout", "tais@dev.com")
    pid = inserir_post(conn, "Draft post", "Conteudo inicial", uid)

    atualizar_usuario(conn, uid, "Tais S. Cout", "tais.scout@dev.com")
    atualizar_post(conn, pid, "Post revisado", "Conteudo atualizado", False)
    publicar_post(conn, pid)

    print("[OK] Registros atualizados.")
    conn.close()

if __name__ == "__main__":
    main()
''')
    commit_and_push("refactor: atualiza main.py com fluxo de atualizacao de registros")

# ════════════════════════════════════════════════════════════════════════════
# AULA 6 — Removendo registros
# ════════════════════════════════════════════════════════════════════════════
def aula06():
    fase(6, "Removendo registros")

    append_file("usuarios.py", '''

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
''')
    commit_and_push("feat: implementa remocao de usuario com CASCADE automatico nos posts")
    wait("Commit 2")

    append_file("posts.py", '''

def remover_post(conn: sqlite3.Connection, post_id: int) -> bool:
    """Remove um post pelo ID."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    return cursor.rowcount > 0


def remover_posts_do_usuario(conn: sqlite3.Connection, usuario_id: int) -> int:
    """Remove todos os posts de um usuario. Retorna quantidade removida."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM posts WHERE usuario_id = ?", (usuario_id,))
    conn.commit()
    print(f"[DELETE] {cursor.rowcount} post(s) do usuario {usuario_id} removidos")
    return cursor.rowcount
''')
    commit_and_push("feat: implementa remocao individual e em massa de posts")
    wait("Commit 3")

    append_file("schema.py", '''

def resetar_banco(conn: sqlite3.Connection) -> None:
    """
    DROP + CREATE — util para testes e reset do ambiente de desenvolvimento.
    NUNCA usar em producao.
    """
    cursor = conn.cursor()
    cursor.executescript("""
        DROP TABLE IF EXISTS posts;
        DROP TABLE IF EXISTS usuarios;
    """)
    conn.commit()
    criar_schema(conn)
    print("[DB] Banco resetado com sucesso.")
''')
    commit_and_push("feat: adiciona funcao de reset do banco para ambiente de desenvolvimento")
    wait("Commit 4")

    w("main.py", '''\
"""main.py — demonstracao de remocao de registros"""
from database import get_connection, configure_connection
from schema import criar_schema
from usuarios import inserir_usuario, remover_usuario
from posts import inserir_post, remover_post

def main():
    conn = get_connection()
    conn = configure_connection(conn)
    criar_schema(conn)

    uid = inserir_usuario(conn, "Usuario Temp", "temp@dev.com")
    pid = inserir_post(conn, "Post temporario", "Para deletar", uid)

    remover_post(conn, pid)
    remover_usuario(conn, uid)  # CASCADE remove posts restantes

    print("[OK] Registros removidos com sucesso.")
    conn.close()

if __name__ == "__main__":
    main()
''')
    commit_and_push("refactor: atualiza main.py com demonstracao de remocao e cascade delete")

# ════════════════════════════════════════════════════════════════════════════
# AULA 7 — Inserindo registros em lote
# ════════════════════════════════════════════════════════════════════════════
def aula07():
    fase(7, "Inserindo registros em lote")

    append_file("usuarios.py", '''

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
''')
    commit_and_push("feat: implementa insercao em lote de usuarios com executemany")
    wait("Commit 2")

    append_file("posts.py", '''

def inserir_posts_lote(conn: sqlite3.Connection, posts: list[dict]) -> int:
    """
    Batch insert de posts. Mais eficiente que insercoes individuais.
    posts = [{"titulo": ..., "conteudo": ..., "usuario_id": ..., "publicado": bool}]
    """
    dados = [
        (p["titulo"].strip(), p.get("conteudo", "").strip(),
         int(p.get("publicado", False)), p["usuario_id"])
        for p in posts
    ]
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO posts (titulo, conteudo, publicado, usuario_id) VALUES (?, ?, ?, ?)",
        dados
    )
    conn.commit()
    print(f"[BATCH] {cursor.rowcount} post(s) inseridos em lote")
    return cursor.rowcount
''')
    commit_and_push("feat: implementa batch insert de posts com executemany e validacao de dados")
    wait("Commit 3")

    w("seed.py", '''\
"""
seed.py — Popula o banco com dados de exemplo para desenvolvimento/testes
"""
from database import get_connection, configure_connection
from schema import criar_schema, resetar_banco
from usuarios import inserir_usuarios_lote
from posts import inserir_posts_lote

USUARIOS_SEED = [
    ("Tais Cout",    "tais@dev.com"),
    ("Caio Souza",   "caio@dev.com"),
    ("Ana Lima",     "ana@dev.com"),
    ("Pedro Alves",  "pedro@dev.com"),
]

def run_seed():
    conn = get_connection()
    conn = configure_connection(conn)
    resetar_banco(conn)

    uids = []
    for nome, email in USUARIOS_SEED:
        from usuarios import inserir_usuario
        uid = inserir_usuario(conn, nome, email)
        uids.append(uid)

    posts_batch = [
        {"titulo": "FastAPI na pratica",   "conteudo": "...", "usuario_id": uids[0], "publicado": True},
        {"titulo": "SQLite com Python",    "conteudo": "...", "usuario_id": uids[0], "publicado": True},
        {"titulo": "Docker do zero",       "conteudo": "...", "usuario_id": uids[1], "publicado": True},
        {"titulo": "Intro ao DevSecOps",   "conteudo": "...", "usuario_id": uids[2], "publicado": False},
        {"titulo": "OWASP Top 10 2025",    "conteudo": "...", "usuario_id": uids[2], "publicado": True},
        {"titulo": "Git workflow pro",     "conteudo": "...", "usuario_id": uids[3], "publicado": True},
    ]
    inserir_posts_lote(conn, posts_batch)
    print("[SEED] Banco populado com sucesso!")
    conn.close()

if __name__ == "__main__":
    run_seed()
''')
    commit_and_push("feat: cria seed.py para popular banco com dados de desenvolvimento via batch")
    wait("Commit 4")

    w("main.py", '''\
"""main.py — demonstracao de batch insert"""
from seed import run_seed

def main():
    run_seed()
    print("[OK] Batch insert concluido via seed.py")

if __name__ == "__main__":
    main()
''')
    commit_and_push("refactor: simplifica main.py delegando seed para modulo dedicado")

# ════════════════════════════════════════════════════════════════════════════
# AULA 8 — Consultando os registros
# ════════════════════════════════════════════════════════════════════════════
def aula08():
    fase(8, "Consultando os registros")

    append_file("usuarios.py", '''

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
''')
    commit_and_push("feat: implementa queries de busca de usuarios (fetchall e fetchone)")
    wait("Commit 2")

    append_file("posts.py", '''

def buscar_posts_publicados(conn: sqlite3.Connection) -> list:
    """JOIN com usuarios para retornar nome do autor junto com o post."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.titulo, p.conteudo, p.criado_em, u.nome AS autor
        FROM posts p
        INNER JOIN usuarios u ON p.usuario_id = u.id
        WHERE p.publicado = 1
        ORDER BY p.criado_em DESC
    """)
    return cursor.fetchall()


def buscar_posts_do_usuario(conn: sqlite3.Connection, usuario_id: int) -> list:
    """Filtragem por usuario_id com WHERE."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM posts WHERE usuario_id = ? ORDER BY criado_em DESC",
        (usuario_id,)
    )
    return cursor.fetchall()


def buscar_post_por_id(conn: sqlite3.Connection, post_id: int):
    cursor = conn.cursor()
    cursor.execute(
        """SELECT p.*, u.nome AS autor
           FROM posts p JOIN usuarios u ON p.usuario_id = u.id
           WHERE p.id = ?""",
        (post_id,)
    )
    return cursor.fetchone()
''')
    commit_and_push("feat: implementa queries de posts com JOIN, WHERE e ORDER BY")
    wait("Commit 3")

    append_file("posts.py", '''

def contar_posts(conn: sqlite3.Connection, publicado: bool | None = None) -> int:
    """SELECT COUNT — funcoes de agregacao."""
    cursor = conn.cursor()
    if publicado is None:
        cursor.execute("SELECT COUNT(*) FROM posts")
    else:
        cursor.execute("SELECT COUNT(*) FROM posts WHERE publicado = ?", (int(publicado),))
    return cursor.fetchone()[0]
''')
    commit_and_push("feat: adiciona contagem de posts com funcao de agregacao COUNT")
    wait("Commit 4")

    w("main.py", '''\
"""main.py — demonstracao de consultas"""
from seed import run_seed
from database import get_connection, configure_connection
from usuarios import buscar_todos_usuarios
from posts import buscar_posts_publicados, contar_posts

def main():
    run_seed()
    conn = get_connection()
    conn = configure_connection(conn)

    print("\\n--- Usuarios ---")
    for u in buscar_todos_usuarios(conn):
        print(f"  [{u[0]}] {u[1]} — {u[2]}")

    print("\\n--- Posts publicados ---")
    for p in buscar_posts_publicados(conn):
        print(f"  [{p[0]}] {p[1]} — por {p[4]}")

    total = contar_posts(conn)
    publicados = contar_posts(conn, True)
    print(f"\\n  Total: {total} posts | Publicados: {publicados}")
    conn.close()

if __name__ == "__main__":
    main()
''')
    commit_and_push("refactor: atualiza main.py com demonstracao completa de consultas e JOIN")

# ════════════════════════════════════════════════════════════════════════════
# AULA 9 — Alterando o row_factory
# ════════════════════════════════════════════════════════════════════════════
def aula09():
    fase(9, "Alterando o row_factory")

    # Atualiza database.py com row_factory
    w("database.py", '''\
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
''')
    commit_and_push("feat: adiciona row_factory ao database.py para acesso por nome de coluna")
    wait("Commit 2")

    w("row_factory_demo.py", '''\
"""
row_factory_demo.py — Demonstra diferenca entre acesso por indice e por nome
"""
from database import get_db
from schema import criar_schema
from seed import run_seed

def demo():
    run_seed()
    conn = get_db()

    cursor = conn.cursor()

    # SEM row_factory: acesso por indice — fragil
    conn_plain = __import__("sqlite3").connect("blog.db")
    c2 = conn_plain.cursor()
    c2.execute("SELECT * FROM usuarios LIMIT 1")
    row = c2.fetchone()
    print(f"Sem row_factory — indice [0]: {row[0]}, [1]: {row[1]}")

    # COM row_factory = sqlite3.Row: acesso por nome — legivel e seguro
    cursor.execute("SELECT * FROM usuarios LIMIT 1")
    row = cursor.fetchone()
    print(f"Com row_factory — row['id']: {row['id']}, row['nome']: {row['nome']}")

    # Conversao para dict
    row_dict = dict(row)
    print(f"Como dict: {row_dict}")

    conn.close()
    conn_plain.close()

if __name__ == "__main__":
    demo()
''')
    commit_and_push("feat: cria row_factory_demo.py comparando acesso por indice vs por nome")
    wait("Commit 3")

    append_file("posts.py", '''

def buscar_posts_como_dict(conn: sqlite3.Connection) -> list[dict]:
    """
    Retorna posts como lista de dicionarios (requer row_factory=sqlite3.Row).
    Facilita serializacao para JSON em APIs.
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.titulo, p.publicado, p.criado_em, u.nome AS autor
        FROM posts p JOIN usuarios u ON p.usuario_id = u.id
        ORDER BY p.criado_em DESC
    """)
    return [dict(row) for row in cursor.fetchall()]
''')
    commit_and_push("feat: adiciona busca de posts como dict usando row_factory para serializacao JSON")
    wait("Commit 4")

    w("main.py", '''\
"""main.py — demonstracao de row_factory"""
from row_factory_demo import demo

if __name__ == "__main__":
    demo()
''')
    commit_and_push("refactor: main.py aponta para demo de row_factory")

# ════════════════════════════════════════════════════════════════════════════
# AULA 10 — Boas práticas
# ════════════════════════════════════════════════════════════════════════════
def aula10():
    fase(10, "Boas práticas")

    w("boas_praticas.py", '''\
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
''')
    commit_and_push("feat: cria modulo boas_praticas.py com guia de uso seguro do DB API")
    wait("Commit 2")

    append_file("boas_praticas.py", '''

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
''')
    commit_and_push("feat: documenta prevencao de SQL injection, context manager e tratamento de excecoes")
    wait("Commit 3")

    append_file("boas_praticas.py", '''

# ── 4. FECHAMENTO SEGURO ──────────────────────────────────────────────────────

def executar_query_segura(query: str, params: tuple = ()):
    """
    Padrao recomendado: try/finally garante fechamento mesmo com excecao.
    """
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.fetchall()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise RuntimeError(f"Erro ao executar query: {e}") from e
    finally:
        if conn:
            conn.close()
''')
    commit_and_push("feat: adiciona padrao try-finally para fechamento seguro de conexoes")
    wait("Commit 4")

    w("main.py", '''\
"""main.py — demonstracao de boas praticas"""
from seed import run_seed
from boas_praticas import usar_context_manager, inserir_com_tratamento
from database import get_db

def main():
    run_seed()
    conn = get_db()

    print("\\n--- Context Manager ---")
    usar_context_manager()

    print("\\n--- Insert com tratamento de excecoes ---")
    inserir_com_tratamento(conn, "Novo Dev", "tais@dev.com")  # email ja existe -> aviso
    inserir_com_tratamento(conn, "Novo Dev", "novo@dev.com")  # insere com sucesso

    conn.close()

if __name__ == "__main__":
    main()
''')
    commit_and_push("refactor: main.py com demonstracao de boas praticas e tratamento de erros")

# ════════════════════════════════════════════════════════════════════════════
# AULA 11 — Gerenciando transações
# ════════════════════════════════════════════════════════════════════════════
def aula11():
    fase(11, "Gerenciando transações")

    w("transacoes.py", '''\
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
''')
    commit_and_push("feat: cria modulo transacoes.py com documentacao ACID")
    wait("Commit 2")

    append_file("transacoes.py", '''

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
''')
    commit_and_push("feat: implementa context manager de transacao com commit e rollback automatico")
    wait("Commit 3")

    append_file("transacoes.py", '''

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
    print("\\n[DEMO] Iniciando transacao que vai falhar...")
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
''')
    commit_and_push("feat: implementa transferencia atomica de posts e demo de rollback")
    wait("Commit 4")

    # README final completo
    w("README.md", """\
# DB API — Banco de Dados Relacionais com Python

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![DIO](https://img.shields.io/badge/DIO-Bootcamp-9B59F7?style=for-the-badge)](https://dio.me)
[![AppSec](https://img.shields.io/badge/AppSec-Hardened-FF4444?style=for-the-badge)]()

> Projeto completo do módulo **Explorando Banco de Dados Relacionais com Python DB API**  
> DIO Bootcamp — Jornada para o Futuro

## Módulos cobertos (11 aulas)

| # | Aula | Duração |
|---|------|---------|
| 1 | Introdução aos Bancos de Dados Relacionais | ~31 min |
| 2 | Conectando com o banco de dados | 8 min |
| 3 | Criando uma tabela | 5 min |
| 4 | Inserindo registros | 6 min |
| 5 | Atualizando registros | 6 min |
| 6 | Removendo registros | 3 min |
| 7 | Inserindo registros em lote | 6 min |
| 8 | Consultando os registros | 10 min |
| 9 | Alterando o row_factory | 7 min |
| 10 | Boas práticas | 10 min |
| 11 | Gerenciando transações | 12 min |

## Estrutura

```
db-api/
├── database.py         ← conexão, row_factory, PRAGMAs
├── schema.py           ← criação de tabelas e reset
├── usuarios.py         ← CRUD + batch
├── posts.py            ← CRUD + batch + generator
├── transacoes.py       ← context manager ACID
├── boas_praticas.py    ← segurança e padrões
├── row_factory_demo.py ← comparativo row_factory
├── seed.py             ← dados de desenvolvimento
├── main.py             ← demo completo
├── requirements.txt
└── .env.example
```

## Segurança (AppSec)

| Prática | Implementação |
|---------|--------------|
| SQL Injection | Parâmetros `?` em todas as queries — nunca f-string |
| Integridade referencial | `PRAGMA foreign_keys=ON` + `ON DELETE CASCADE` |
| Erros sensíveis | `IntegrityError` tratado sem expor detalhes internos |
| Transações | Context manager com ROLLBACK automático |
| Env vars | `.env` no `.gitignore` — segredos fora do código |

## Como executar

```bash
cd fastAPI/db-api
pip install -r requirements.txt
cp .env.example .env
python seed.py    # popula o banco
python main.py    # executa demo
```
""")
    commit_and_push("docs: README final com tabela de modulos, estrutura e guia de seguranca")
    wait("Commit 5 — main final")

    w("main.py", '''\
"""
main.py — Demo final: todas as funcionalidades integradas
"""
from seed import run_seed
from database import get_db
from usuarios import buscar_todos_usuarios
from posts import buscar_posts_publicados, buscar_posts_como_dict, contar_posts
from transacoes import transferir_post, demo_rollback
from boas_praticas import usar_context_manager

def linha(n=55): print("─" * n)

def main():
    print("\\n[INIT] Populando banco...")
    run_seed()

    conn = get_db()
    linha()
    print("  DB API — Demo Final | DIO Bootcamp")
    linha()

    print("\\n[1] Usuarios cadastrados:")
    for u in buscar_todos_usuarios(conn):
        print(f"  {u['id']:>3} | {u['nome']:<20} | {u['email']}")

    print("\\n[2] Posts publicados:")
    for p in buscar_posts_publicados(conn):
        print(f"  {p['id']:>3} | {p['titulo']:<35} | {p['autor']}")

    print("\\n[3] Posts como dict (para JSON/API):")
    for p in buscar_posts_como_dict(conn)[:2]:
        print(f"  {p}")

    total = contar_posts(conn)
    pub   = contar_posts(conn, True)
    print(f"\\n[4] Total: {total} posts | Publicados: {pub}")

    print("\\n[5] Context Manager:")
    usar_context_manager()

    print("\\n[6] Demonstracao de ROLLBACK:")
    demo_rollback(conn)

    linha()
    print("  Demo concluido com sucesso!")
    linha()
    conn.close()

if __name__ == "__main__":
    main()
''')
    commit_and_push("feat: main.py final integra todas as funcionalidades do modulo db-api")

    # Push final garantido
    run("git push")
    ok("Push final realizado.")

# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════
def main():
    print(f"""\n{C.BOLD}{C.CYAN}
╔══════════════════════════════════════════════════════════╗
║   DB API AutoBuilder v2 — DIO Bootcamp                   ║
║   11 aulas | push apos cada commit | delays organicos    ║
╚══════════════════════════════════════════════════════════╝{C.RESET}

  Projeto : fastAPI/db-api/
  Repo    : {REPO_ROOT}
  Delays  : {DELAY_MIN}s – {DELAY_MAX}s
""")

    if not os.path.exists(os.path.join(REPO_ROOT, ".git")):
        erro("Repo .git nao encontrado. Verifique REPO_ROOT.")
        sys.exit(1)

    ok(f"Repo encontrado: {REPO_ROOT}")
    resp = input(f"\n  {C.YELLOW}Iniciar? (s/n): {C.RESET}").strip().lower()
    if resp != "s":
        sys.exit(0)

    inicio = datetime.now()
    fases = [aula01, aula02, aula03, aula04, aula05, aula06,
             aula07, aula08, aula09, aula10, aula11]

    for i, fn in enumerate(fases, 1):
        fn()
        if i < len(fases):
            wait(f"Proxima aula: {i+1}/11")

    dur = datetime.now() - inicio
    print(f"""\n{C.BOLD}{C.GREEN}
╔══════════════════════════════════════════════════════════╗
║   Concluido!                                             ║
║   11 aulas | ~45 commits | push em cada um              ║
║   Duracao: {str(dur).split('.')[0]:<45} ║
╚══════════════════════════════════════════════════════════╝{C.RESET}""")

if __name__ == "__main__":
    main()
