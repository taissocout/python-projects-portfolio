"""main.py — demonstracao de boas praticas"""
from seed import run_seed
from boas_praticas import usar_context_manager, inserir_com_tratamento
from database import get_db

def main():
    run_seed()
    conn = get_db()

    print("\n--- Context Manager ---")
    usar_context_manager()

    print("\n--- Insert com tratamento de excecoes ---")
    inserir_com_tratamento(conn, "Novo Dev", "tais@dev.com")  # email ja existe -> aviso
    inserir_com_tratamento(conn, "Novo Dev", "novo@dev.com")  # insere com sucesso

    conn.close()

if __name__ == "__main__":
    main()
