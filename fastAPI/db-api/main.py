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
