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
