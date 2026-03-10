"""
row_factory_demo.py — Demonstra diferenca entre acesso por indice e por nome
"""
from database import get_db
from schema import criar_schema
from seed import run_seed

def demo():
    run_seed()
    conn = get_db()

    cursor = conn.cursor()

    # SEM row_factory: acesso por indice — fragil
    conn_plain = __import__("sqlite3").connect("blog.db")
    c2 = conn_plain.cursor()
    c2.execute("SELECT * FROM usuarios LIMIT 1")
    row = c2.fetchone()
    print(f"Sem row_factory — indice [0]: {row[0]}, [1]: {row[1]}")

    # COM row_factory = sqlite3.Row: acesso por nome — legivel e seguro
    cursor.execute("SELECT * FROM usuarios LIMIT 1")
    row = cursor.fetchone()
    print(f"Com row_factory — row['id']: {row['id']}, row['nome']: {row['nome']}")

    # Conversao para dict
    row_dict = dict(row)
    print(f"Como dict: {row_dict}")

    conn.close()
    conn_plain.close()

if __name__ == "__main__":
    demo()
