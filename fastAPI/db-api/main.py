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
