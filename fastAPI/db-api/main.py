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
