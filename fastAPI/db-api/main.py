"""main.py — demonstracao de consultas"""
from seed import run_seed
from database import get_connection, configure_connection
from usuarios import buscar_todos_usuarios
from posts import buscar_posts_publicados, contar_posts

def main():
    run_seed()
    conn = get_connection()
    conn = configure_connection(conn)

    print("\n--- Usuarios ---")
    for u in buscar_todos_usuarios(conn):
        print(f"  [{u[0]}] {u[1]} — {u[2]}")

    print("\n--- Posts publicados ---")
    for p in buscar_posts_publicados(conn):
        print(f"  [{p[0]}] {p[1]} — por {p[4]}")

    total = contar_posts(conn)
    publicados = contar_posts(conn, True)
    print(f"\n  Total: {total} posts | Publicados: {publicados}")
    conn.close()

if __name__ == "__main__":
    main()
