# conftest_check.py — verifica compatibilidade antes de rodar os testes
# Execute: python conftest_check.py
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

issues = []

try:
    from main import app
    print("  OK  main.app importado")
except Exception as e:
    issues.append(f"  ERR main.app: {e}")

try:
    from database import get_db, Base
    print("  OK  database.get_db importado")
except ImportError:
    issues.append("  WARN database.get_db nao encontrado — conftest usara fallback")

if issues:
    print("\nAtenção:")
    for i in issues:
        print(i)
    print("\nOs testes de integracao podem falhar. Verifique database.py")
else:
    print("\n  Tudo OK — pode rodar: pytest tests/ -v")
