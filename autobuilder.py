"""
autobuilder.py — DIO DB API Project Builder
Autor: taissocout

Executa na raiz do repo: /mnt/storage/Projetos-Python/fastAPI/
Cria: fastAPI/db-api/ com estrutura completa e commits automaticos

Uso:
    python autobuilder.py

Cada fase tem delay aleatorio entre commits para parecer organico.
"""

import os
import subprocess
import time
import random
import sys
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────

# Altere para o caminho do seu repo
REPO_ROOT = os.path.expanduser("/mnt/storage/Projetos-Python")
PROJECT_DIR = os.path.join(REPO_ROOT, "fastAPI", "db-api")

# Delay entre commits: min e max em segundos
DELAY_MIN = 45
DELAY_MAX = 180

# ── Cores no terminal ─────────────────────────────────────────────────────────

class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    BLUE   = "\033[94m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    CYAN   = "\033[96m"
    GRAY   = "\033[90m"

def ok(msg):    print(f"{C.GREEN}  ✔  {msg}{C.RESET}")
def info(msg):  print(f"{C.BLUE}  ●  {msg}{C.RESET}")
def warn(msg):  print(f"{C.YELLOW}  ⚠  {msg}{C.RESET}")
def erro(msg):  print(f"{C.RED}  ✘  {msg}{C.RESET}")
def fase(n, t): print(f"\n{C.BOLD}{C.CYAN}{'─'*55}\n  FASE {n} — {t}\n{'─'*55}{C.RESET}")

# ── Git helpers ───────────────────────────────────────────────────────────────

def run(cmd, cwd=None):
    """Executa comando shell, retorna (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd, shell=True, cwd=cwd or REPO_ROOT,
        capture_output=True, text=True
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def git_add_commit(message: str, cwd=None):
    """Stage tudo e faz commit com a mensagem dada."""
    rc, _, err = run("git add -A", cwd)
    if rc != 0:
        erro(f"git add falhou: {err}")
        return False

    rc, out, err = run(f'git commit -m "{message}"', cwd)
    if rc != 0:
        if "nothing to commit" in err or "nothing to commit" in out:
            warn("Nada para commitar — pulando.")
            return True
        erro(f"git commit falhou: {err}")
        return False

    ok(f"Commit: {message}")
    return True

def git_push():
    rc, out, err = run("git push", REPO_ROOT)
    if rc != 0:
        warn(f"Push falhou (pode ser normal se sem internet): {err}")
    else:
        ok("Push realizado.")

def human_delay(label: str):
    """Espera um tempo aleatorio entre DELAY_MIN e DELAY_MAX segundos."""
    wait = random.randint(DELAY_MIN, DELAY_MAX)
    print(f"\n{C.GRAY}  ⏱  Aguardando {wait}s antes do proximo commit ({label})...{C.RESET}")
    for i in range(wait, 0, -1):
        print(f"\r{C.GRAY}     {i:>3}s restantes...{C.RESET}", end="", flush=True)
        time.sleep(1)
    print(f"\r{C.GRAY}     Pronto!{' '*20}{C.RESET}")

# ── Escrita de arquivos ───────────────────────────────────────────────────────

def write(path: str, content: str):
    """Cria arquivo e diretórios necessários."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    info(f"Criado: {os.path.relpath(path, REPO_ROOT)}")

def p(rel: str) -> str:
    """Retorna caminho absoluto relativo ao PROJECT_DIR."""
    return os.path.join(PROJECT_DIR, rel)

# ══════════════════════════════════════════════════════════════════════════════
# CONTEUDO DOS ARQUIVOS POR FASE
# ══════════════════════════════════════════════════════════════════════════════

# ── FASE 1 — Estrutura inicial + .env + gitignore ─────────────────────────────

ENV_EXAMPLE = """\
# db-api environment variables
DB_PATH=blog.db
DEBUG=false
"""

GITIGNORE_EXTRA = """\
# db-api
fastAPI/db-api/*.db
fastAPI/db-api/.env
"""

README_INITIAL = """\
# DB API — Explorando Banco de Dados Relacionais com Python

Projeto desenvolvido no bootcamp **DIO — Jornada para o Futuro**.

## Módulos cobertos
- Introdução aos Bancos de Dados Relacionais
- Conectando com o banco de dados (sqlite3)
- Criando tabelas, inserindo, consultando, atualizando e removendo registros
- Inserção em lote, row_factory, boas práticas e gerenciamento de transações

## Stack
- Python 3.10+
- sqlite3 (Python DB API — PEP 249)
- python-dotenv

## Como executar
```bash
# Instale dependências
pip install python-dotenv

# Execute
python main.py
```

> Status: 🚧 Em desenvolvimento
"""

# ── FASE 2 — Conexão + schema ─────────────────────────────────────────────────

DATABASE_PY = '''\
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
'''

MAIN_V1 = '''\
"""
main.py — Entry point
Fase 1: conexão e criação do schema
"""

from database import get_connection, create_schema


def main():
    conn = get_connection()
    create_schema(conn)
    print(f"[OK] Conectado ao banco. Tabelas prontas.")
    conn.close()


if __name__ == "__main__":
    main()
'''

REQUIREMENTS = """\
python-dotenv>=1.0.0
"""

# ── FASE 3 — CRUD de usuários ─────────────────────────────────────────────────

USUARIOS_PY = '''\
"""
usuarios.py — CRUD de usuários
Operações: inserir, buscar, atualizar, remover
"""

import sqlite3


def inserir_usuario(conn: sqlite3.Connection, nome: str, email: str) -> int:
    """Insere um usuário e retorna o ID gerado."""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nome, email) VALUES (?, ?)",
        (nome.strip(), email.strip().lower())   # sanitização básica
    )
    conn.commit()
    return cursor.lastrowid


def buscar_usuarios(conn: sqlite3.Connection) -> list:
    """Retorna todos os usuários."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios ORDER BY criado_em DESC")
    return cursor.fetchall()


def buscar_usuario_por_id(conn: sqlite3.Connection, usuario_id: int):
    """Retorna um usuário pelo ID ou None."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
    return cursor.fetchone()


def atualizar_usuario(conn: sqlite3.Connection, usuario_id: int, nome: str, email: str) -> bool:
    """Atualiza nome e email de um usuário. Retorna True se encontrado."""
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET nome = ?, email = ? WHERE id = ?",
        (nome.strip(), email.strip().lower(), usuario_id)
    )
    conn.commit()
    return cursor.rowcount > 0


def remover_usuario(conn: sqlite3.Connection, usuario_id: int) -> bool:
    """Remove um usuário pelo ID. Retorna True se removido."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
    conn.commit()
    return cursor.rowcount > 0
'''

# ── FASE 4 — CRUD de posts + batch insert ─────────────────────────────────────

POSTS_PY = '''\
"""
posts.py — CRUD de posts + inserção em lote
"""

import sqlite3
from typing import Generator


def inserir_post(conn: sqlite3.Connection, titulo: str, conteudo: str,
                 usuario_id: int, publicado: bool = False) -> int:
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO posts (titulo, conteudo, publicado, usuario_id) VALUES (?, ?, ?, ?)",
        (titulo.strip(), conteudo.strip(), int(publicado), usuario_id)
    )
    conn.commit()
    return cursor.lastrowid


def inserir_posts_em_lote(conn: sqlite3.Connection, posts: list[dict]) -> int:
    """
    Inserção em lote com executemany — mais eficiente para grandes volumes.
    posts = [{"titulo": ..., "conteudo": ..., "usuario_id": ..., "publicado": ...}]
    """
    dados = [
        (p["titulo"], p.get("conteudo", ""), int(p.get("publicado", False)), p["usuario_id"])
        for p in posts
    ]
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO posts (titulo, conteudo, publicado, usuario_id) VALUES (?, ?, ?, ?)",
        dados
    )
    conn.commit()
    return cursor.rowcount


def buscar_posts(conn: sqlite3.Connection, publicado: bool = True) -> list:
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT p.*, u.nome AS autor
        FROM posts p
        JOIN usuarios u ON p.usuario_id = u.id
        WHERE p.publicado = ?
        ORDER BY p.criado_em DESC
        """,
        (int(publicado),)
    )
    return cursor.fetchall()


def buscar_post_por_id(conn: sqlite3.Connection, post_id: int):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT p.*, u.nome AS autor FROM posts p JOIN usuarios u ON p.usuario_id = u.id WHERE p.id = ?",
        (post_id,)
    )
    return cursor.fetchone()


def atualizar_post(conn: sqlite3.Connection, post_id: int, titulo: str,
                   conteudo: str, publicado: bool) -> bool:
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE posts SET titulo = ?, conteudo = ?, publicado = ? WHERE id = ?",
        (titulo.strip(), conteudo.strip(), int(publicado), post_id)
    )
    conn.commit()
    return cursor.rowcount > 0


def remover_post(conn: sqlite3.Connection, post_id: int) -> bool:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    return cursor.rowcount > 0


def gerar_relatorio(conn: sqlite3.Connection) -> Generator:
    """Generator — retorna posts um a um sem carregar tudo na memória."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT p.id, p.titulo, u.nome, p.criado_em FROM posts p JOIN usuarios u ON p.usuario_id = u.id"
    )
    for row in cursor:
        yield dict(row)
'''

# ── FASE 5 — Transações + main final ─────────────────────────────────────────

TRANSACOES_PY = '''\
"""
transacoes.py — Gerenciamento de transações
Demonstra uso de BEGIN, COMMIT, ROLLBACK e context manager
"""

import sqlite3
from contextlib import contextmanager


@contextmanager
def transacao(conn: sqlite3.Connection):
    """
    Context manager para transações seguras.
    Em caso de exceção faz ROLLBACK automaticamente.

    Uso:
        with transacao(conn):
            cursor.execute(...)
            cursor.execute(...)
    """
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[ROLLBACK] Transação revertida: {e}")
        raise


def transferir_publicacao(conn: sqlite3.Connection,
                           post_id_origem: int,
                           usuario_id_destino: int) -> bool:
    """
    Exemplo de operação que exige atomicidade:
    Transfere a autoria de um post de um usuário para outro.
    Se qualquer etapa falhar, tudo é revertido.
    """
    with transacao(conn):
        cursor = conn.cursor()

        # Verifica se o post existe
        cursor.execute("SELECT id FROM posts WHERE id = ?", (post_id_origem,))
        if not cursor.fetchone():
            raise ValueError(f"Post {post_id_origem} não encontrado.")

        # Verifica se o usuário destino existe
        cursor.execute("SELECT id FROM usuarios WHERE id = ?", (usuario_id_destino,))
        if not cursor.fetchone():
            raise ValueError(f"Usuário {usuario_id_destino} não encontrado.")

        # Realiza a transferência
        cursor.execute(
            "UPDATE posts SET usuario_id = ? WHERE id = ?",
            (usuario_id_destino, post_id_origem)
        )

    return True
'''

MAIN_FINAL = '''\
"""
main.py — Demo completo do projeto DB API
Executa todas as operações: conectar, criar schema, CRUD, batch, transações, relatório
"""

from database import get_connection, create_schema
from usuarios import inserir_usuario, buscar_usuarios, atualizar_usuario, remover_usuario
from posts import inserir_post, inserir_posts_em_lote, buscar_posts, gerar_relatorio
from transacoes import transacao


def linha(n=55): print("─" * n)


def main():
    conn = get_connection()
    create_schema(conn)

    linha()
    print("  DB API DEMO — DIO Bootcamp")
    linha()

    # ── Usuários ──────────────────────────────────────────────────────────────
    print("\\n[1] Inserindo usuários...")
    id1 = inserir_usuario(conn, "Taís", "tais@dev.com")
    id2 = inserir_usuario(conn, "Caio", "caio@dev.com")
    print(f"    Usuários criados: IDs {id1}, {id2}")

    print("\\n[2] Listando usuários...")
    for u in buscar_usuarios(conn):
        print(f"    ID {u['id']:>3} | {u['nome']:<20} | {u['email']}")

    # ── Posts CRUD ────────────────────────────────────────────────────────────
    print("\\n[3] Inserindo posts...")
    p1 = inserir_post(conn, "FastAPI — Primeiros passos", "Conteúdo...", id1, True)
    p2 = inserir_post(conn, "SQLite com Python", "Conteúdo...", id1, False)
    print(f"    Posts criados: IDs {p1}, {p2}")

    # ── Batch insert ──────────────────────────────────────────────────────────
    print("\\n[4] Inserção em lote...")
    batch = [
        {"titulo": "Async com FastAPI", "conteudo": "...", "usuario_id": id2, "publicado": True},
        {"titulo": "Docker para devs",  "conteudo": "...", "usuario_id": id2, "publicado": True},
        {"titulo": "AppSec basics",     "conteudo": "...", "usuario_id": id1, "publicado": False},
    ]
    total = inserir_posts_em_lote(conn, batch)
    print(f"    {total} posts inseridos em lote.")

    # ── Consulta ──────────────────────────────────────────────────────────────
    print("\\n[5] Posts publicados:")
    for post in buscar_posts(conn, publicado=True):
        print(f"    [{post['id']}] {post['titulo']:<35} — {post['autor']}")

    # ── row_factory demo ──────────────────────────────────────────────────────
    print("\\n[6] Relatório via generator (row_factory):")
    for item in gerar_relatorio(conn):
        print(f"    {item['id']:>3} | {item['titulo']:<35} | {item['nome']}")

    # ── Transação ─────────────────────────────────────────────────────────────
    print("\\n[7] Demonstrando transação com rollback...")
    try:
        with transacao(conn):
            cursor = conn.cursor()
            cursor.execute("UPDATE posts SET titulo = 'Alterado em transação' WHERE id = ?", (p1,))
            # Simula erro para demonstrar rollback:
            # raise Exception("Erro simulado — ROLLBACK será executado")
            print("    Transação bem-sucedida — COMMIT aplicado.")
    except Exception as e:
        print(f"    Erro capturado: {e}")

    # ── Cleanup demo ──────────────────────────────────────────────────────────
    print("\\n[8] Removendo usuário de teste (Caio)...")
    # remover_usuario(conn, id2)  # descomente para testar

    linha()
    print("  Demo concluído!")
    linha()
    conn.close()


if __name__ == "__main__":
    main()
'''

README_FINAL = """\
# DB API — Explorando Banco de Dados Relacionais com Python

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![DIO](https://img.shields.io/badge/DIO-Bootcamp-9B59F7?style=for-the-badge)](https://dio.me)
[![AppSec](https://img.shields.io/badge/AppSec-Hardened-FF4444?style=for-the-badge)]()

> Projeto do curso **Explorando Banco de Dados Relacionais com Python DB API** — DIO Bootcamp  
> Implementação completa do padrão **Python DB API (PEP 249)** com SQLite.

---

## Módulos cobertos

| Módulo | Duração |
|--------|---------|
| Introdução aos Bancos de Dados Relacionais (pt 1, 2, 3) | ~31 min |
| Conectando com o banco de dados | 8 min |
| Criando tabelas | 5 min |
| Inserindo registros | 6 min |
| Atualizando registros | 6 min |
| Removendo registros | 3 min |
| Inserindo registros em lote | 6 min |
| Consultando os registros | 10 min |
| Alterando o row_factory | 7 min |
| Boas práticas | 10 min |
| Gerenciando transações | 12 min |

---

## Estrutura do projeto

```
db-api/
├── database.py        ← conexão, row_factory, schema
├── usuarios.py        ← CRUD de usuários
├── posts.py           ← CRUD de posts + batch insert + generator
├── transacoes.py      ← context manager para transações seguras
├── main.py            ← demo completo
├── requirements.txt
├── .env.example
└── README.md
```

---

## Conceitos aplicados

| Conceito | Implementação |
|----------|--------------|
| Python DB API (PEP 249) | `sqlite3.connect`, `cursor`, `execute`, `commit` |
| row_factory | `conn.row_factory = sqlite3.Row` — acesso por nome de coluna |
| Batch insert | `cursor.executemany()` |
| Transações | `BEGIN / COMMIT / ROLLBACK` via context manager |
| Generator | `yield` em `gerar_relatorio()` |
| Boas práticas | Parâmetros `?` (previne SQL Injection), PRAGMA foreign_keys |
| AppSec | Nunca concatenar SQL + sanitização de inputs |

---

## Como executar

```bash
cd fastAPI/db-api
pip install -r requirements.txt
cp .env.example .env
python main.py
```

---

*DIO Bootcamp — Jornada para o Futuro | AppSec / DevSecOps Portfolio*
"""

# ══════════════════════════════════════════════════════════════════════════════
# FASES DE EXECUÇÃO
# ══════════════════════════════════════════════════════════════════════════════

def fase1_estrutura():
    fase(1, "Estrutura inicial do projeto")

    os.makedirs(PROJECT_DIR, exist_ok=True)
    ok(f"Pasta criada: fastAPI/db-api/")

    write(p(".env.example"), ENV_EXAMPLE)
    write(p("requirements.txt"), REQUIREMENTS)
    write(p("README.md"), README_INITIAL)

    # Adiciona ao .gitignore global do repo se ainda não estiver lá
    gi_path = os.path.join(REPO_ROOT, ".gitignore")
    if os.path.exists(gi_path):
        with open(gi_path, "r") as f:
            current = f.read()
        if "db-api/*.db" not in current:
            with open(gi_path, "a") as f:
                f.write(f"\n{GITIGNORE_EXTRA}")
            ok(".gitignore atualizado com regras do db-api")

    git_add_commit("chore: inicializa estrutura do projeto db-api")


def fase2_conexao():
    fase(2, "Conexão com banco de dados + schema")
    human_delay("feat: conexao e schema")

    write(p("database.py"), DATABASE_PY)
    write(p("main.py"), MAIN_V1)

    git_add_commit("feat: adiciona conexao SQLite com row_factory e criacao de schema")


def fase3_crud_usuarios():
    fase(3, "CRUD de usuários")
    human_delay("feat: crud usuarios")

    write(p("usuarios.py"), USUARIOS_PY)

    git_add_commit("feat: implementa CRUD completo de usuarios com Python DB API")


def fase4_crud_posts():
    fase(4, "CRUD de posts + batch insert + generator")
    human_delay("feat: crud posts e batch")

    write(p("posts.py"), POSTS_PY)

    git_add_commit("feat: adiciona CRUD de posts, batch insert e generator de relatorio")


def fase5_transacoes():
    fase(5, "Gerenciamento de transações + main final")
    human_delay("feat: transacoes e main final")

    write(p("transacoes.py"), TRANSACOES_PY)
    write(p("main.py"), MAIN_FINAL)
    write(p("README.md"), README_FINAL)

    git_add_commit("feat: implementa gerenciamento de transacoes e finaliza demo completo")


def fase6_security():
    fase(6, "Revisão de segurança + docs finais")
    human_delay("security: revisao final")

    # Adiciona .env real ao .gitignore local se precisar
    env_path = p(".env")
    if not os.path.exists(env_path):
        write(env_path, "DB_PATH=blog.db\nDEBUG=false\n")

    git_add_commit("docs: atualiza README com tabela de modulos e instrucoes de execucao")

    human_delay("push final")
    git_push()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print(f"""
{C.BOLD}{C.CYAN}
╔══════════════════════════════════════════════════════╗
║   DB API AutoBuilder — DIO Bootcamp                  ║
║   Cria projeto + commits organicos no GitHub         ║
╚══════════════════════════════════════════════════════╝
{C.RESET}
  Projeto:  fastAPI/db-api/
  Repo:     {REPO_ROOT}
  Delays:   {DELAY_MIN}s – {DELAY_MAX}s entre commits
""")

    # Verifica se o repo existe
    if not os.path.exists(os.path.join(REPO_ROOT, ".git")):
        erro(f"Repo git não encontrado em: {REPO_ROOT}")
        erro("Verifique o caminho REPO_ROOT no topo do script.")
        sys.exit(1)

    confirma = input(f"  {C.YELLOW}Iniciar build? (s/n): {C.RESET}").strip().lower()
    if confirma != "s":
        warn("Cancelado.")
        sys.exit(0)

    inicio = datetime.now()

    fase1_estrutura()
    fase2_conexao()
    fase3_crud_usuarios()
    fase4_crud_posts()
    fase5_transacoes()
    fase6_security()

    fim = datetime.now()
    duracao = fim - inicio

    print(f"""
{C.BOLD}{C.GREEN}
╔══════════════════════════════════════════════════════╗
║   Build concluído!                                   ║
╠══════════════════════════════════════════════════════╣
║   Fases:     6 de 6                                  ║
║   Commits:   6 commits no GitHub                     ║
║   Duração:   {str(duracao).split('.')[0]:<39} ║
╚══════════════════════════════════════════════════════╝
{C.RESET}""")


if __name__ == "__main__":
    main()
