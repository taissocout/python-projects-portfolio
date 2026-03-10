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
