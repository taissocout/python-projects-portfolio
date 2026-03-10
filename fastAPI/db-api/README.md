# DB API — Banco de Dados Relacionais com Python

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![DIO](https://img.shields.io/badge/DIO-Bootcamp-9B59F7?style=for-the-badge)](https://dio.me)
[![AppSec](https://img.shields.io/badge/AppSec-Hardened-FF4444?style=for-the-badge)]()

> Projeto completo do módulo **Explorando Banco de Dados Relacionais com Python DB API**  
> DIO Bootcamp — Jornada para o Futuro

## Módulos cobertos (11 aulas)

| # | Aula | Duração |
|---|------|---------|
| 1 | Introdução aos Bancos de Dados Relacionais | ~31 min |
| 2 | Conectando com o banco de dados | 8 min |
| 3 | Criando uma tabela | 5 min |
| 4 | Inserindo registros | 6 min |
| 5 | Atualizando registros | 6 min |
| 6 | Removendo registros | 3 min |
| 7 | Inserindo registros em lote | 6 min |
| 8 | Consultando os registros | 10 min |
| 9 | Alterando o row_factory | 7 min |
| 10 | Boas práticas | 10 min |
| 11 | Gerenciando transações | 12 min |

## Estrutura

```
db-api/
├── database.py         ← conexão, row_factory, PRAGMAs
├── schema.py           ← criação de tabelas e reset
├── usuarios.py         ← CRUD + batch
├── posts.py            ← CRUD + batch + generator
├── transacoes.py       ← context manager ACID
├── boas_praticas.py    ← segurança e padrões
├── row_factory_demo.py ← comparativo row_factory
├── seed.py             ← dados de desenvolvimento
├── main.py             ← demo completo
├── requirements.txt
└── .env.example
```

## Segurança (AppSec)

| Prática | Implementação |
|---------|--------------|
| SQL Injection | Parâmetros `?` em todas as queries — nunca f-string |
| Integridade referencial | `PRAGMA foreign_keys=ON` + `ON DELETE CASCADE` |
| Erros sensíveis | `IntegrityError` tratado sem expor detalhes internos |
| Transações | Context manager com ROLLBACK automático |
| Env vars | `.env` no `.gitignore` — segredos fora do código |

## Como executar

```bash
cd fastAPI/db-api
pip install -r requirements.txt
cp .env.example .env
python seed.py    # popula o banco
python main.py    # executa demo
```
