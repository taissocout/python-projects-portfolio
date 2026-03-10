"""
boas_praticas.py — Demonstracao de boas praticas com Python DB API

1. Sempre usar parametros ? (nunca f-string em SQL)
2. Fechar conexoes e cursores
3. Usar context manager
4. Nunca logar dados sensiveis
5. Tratar excecoes especificas
"""
import sqlite3
from database import get_db
