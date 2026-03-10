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
    print("\n[INIT] Populando banco...")
    run_seed()

    conn = get_db()
    linha()
    print("  DB API — Demo Final | DIO Bootcamp")
    linha()

    print("\n[1] Usuarios cadastrados:")
    for u in buscar_todos_usuarios(conn):
        print(f"  {u['id']:>3} | {u['nome']:<20} | {u['email']}")

    print("\n[2] Posts publicados:")
    for p in buscar_posts_publicados(conn):
        print(f"  {p['id']:>3} | {p['titulo']:<35} | {p['autor']}")

    print("\n[3] Posts como dict (para JSON/API):")
    for p in buscar_posts_como_dict(conn)[:2]:
        print(f"  {p}")

    total = contar_posts(conn)
    pub   = contar_posts(conn, True)
    print(f"\n[4] Total: {total} posts | Publicados: {pub}")

    print("\n[5] Context Manager:")
    usar_context_manager()

    print("\n[6] Demonstracao de ROLLBACK:")
    demo_rollback(conn)

    linha()
    print("  Demo concluido com sucesso!")
    linha()
    conn.close()

if __name__ == "__main__":
    main()
