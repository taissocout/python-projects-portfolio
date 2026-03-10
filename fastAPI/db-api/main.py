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
