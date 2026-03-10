<div align="center">

# 🏦 Sistema Bancário — POO · Banking System — OOP

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![DIO](https://img.shields.io/badge/DIO-Trilha%20Python-E83F5B?style=for-the-badge)](https://www.dio.me/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Concluído%20%7C%20Done-brightgreen?style=for-the-badge)]()

> **PT** · Implementação de um sistema bancário orientado a objetos seguindo diagrama UML — Desafio DIO Trilha Python  
> **EN** · Object-oriented banking system following a UML class diagram — DIO Python Track Challenge

</div>

---

## 🌐 Idiomas · Languages

- [🇧🇷 Português](#-português)
- [🇺🇸 English](#-english)

---

# 🇧🇷 Português

## 📋 Sobre o Projeto

Evolução do sistema bancário da DIO, migrando de dicionários para **Programação Orientada a Objetos (POO)** completa. O sistema modela clientes, contas e transações usando classes, herança, classes abstratas e iteradores customizados.

## ✨ Funcionalidades

- Cadastro de clientes (Pessoa Física com CPF, nome, data de nascimento e endereço)
- Criação de Contas Correntes vinculadas a clientes
- Depósito e Saque com validações de negócio
- Limite de 3 saques diários e limite por operação (R$ 500,00)
- Extrato bancário com histórico de transações filtráveis por tipo
- Listagem de clientes e contas com iterador customizado
- Gerador (`yield`) para relatórios de histórico

## 🗂️ Diagrama UML de Classes

```
┌─────────────────────┐        ┌──────────────────────────┐
│      Cliente        │        │         Conta            │
├─────────────────────┤        ├──────────────────────────┤
│ - endereco          │1      *│ - saldo                  │
│ - contas: list      │────────│ - numero                 │
├─────────────────────┤        │ - agencia                │
│ + realizar_transacao│        │ - cliente                │
│ + adicionar_conta   │        │ - historico: Historico   │
└────────┬────────────┘        ├──────────────────────────┤
         │                     │ + sacar(valor)           │
         │ herda               │ + depositar(valor)       │
         ▼                     │ + nova_conta() [cls]     │
┌─────────────────────┐        └────────────┬─────────────┘
│   PessoaFisica      │                     │ herda
├─────────────────────┤                     ▼
│ - cpf               │        ┌──────────────────────────┐
│ - nome              │        │     ContaCorrente        │
│ - data_nascimento   │        ├──────────────────────────┤
└─────────────────────┘        │ - limite                 │
                               │ - limite_saques          │
┌─────────────────────┐        └──────────────────────────┘
│     Historico       │
├─────────────────────┤        ┌──────────────────────────┐
│ - transacoes: list  │        │      Transacao (ABC)     │
├─────────────────────┤        ├──────────────────────────┤
│ + adicionar_transacao│       │ + valor (abstract)       │
│ + gerar_relatorio() │        │ + registrar() (abstract) │
└─────────────────────┘        └────────────┬─────────────┘
                                            │ herda
                               ┌────────────┴─────────────┐
                               ▼                          ▼
                    ┌──────────────────┐     ┌──────────────────┐
                    │    Deposito      │     │      Saque       │
                    ├──────────────────┤     ├──────────────────┤
                    │ + valor          │     │ + valor          │
                    │ + registrar()    │     │ + registrar()    │
                    └──────────────────┘     └──────────────────┘
```

## 🛠️ Tecnologias

| Tecnologia | Uso |
|---|---|
| Python 3.10+ | Linguagem principal |
| `abc` (ABC, abstractmethod) | Classes e métodos abstratos |
| `datetime` | Registro temporal das transações |
| POO nativa | Herança, encapsulamento, polimorfismo |

## 🚀 Como Executar

**Pré-requisito:** Python 3.10 ou superior instalado.

```bash
# 1. Clone o repositório
git clone https://github.com/taissocout/sistema-bancario-POO.git

# 2. Acesse a pasta
cd sistema-bancario-POO

# 3. Execute o sistema
python sistema-POO.py
```

## 🎮 Como Usar

```
╔══════════════════════════════════╗
║       BANCO DIO  •  Sistema      ║
╠══════════════════════════════════╣
║  [d] Depositar                   ║
║  [s] Sacar                       ║
║  [e] Extrato                     ║
║  [nc] Nova conta                 ║
║  [lc] Listar contas              ║
║  [nu] Novo usuário               ║
║  [lu] Listar usuários            ║
║  [q] Sair                        ║
╚══════════════════════════════════╝
```

**Fluxo recomendado:**
1. `[nu]` → Cadastrar um novo cliente
2. `[nc]` → Criar uma conta corrente para o cliente
3. `[d]`  → Realizar depósito
4. `[s]`  → Realizar saque
5. `[e]`  → Consultar extrato

## 🧱 Conceitos de POO Aplicados

| Conceito | Implementação |
|---|---|
| **Herança** | `PessoaFisica → Cliente`, `ContaCorrente → Conta`, `Deposito/Saque → Transacao` |
| **Abstração** | Classe `Transacao(ABC)` com `@abstractmethod` |
| **Encapsulamento** | Atributos `_privados` com `@property` |
| **Polimorfismo** | `ContaCorrente.sacar()` sobrescreve `Conta.sacar()` |
| **Iterator Protocol** | `ContasIterador` com `__iter__` e `__next__` |
| **Generator** | `Historico.gerar_relatorio()` com `yield` |
| **`__repr__` / `__str__`** | Representações legíveis de contas e clientes |
| **`@classmethod`** | `Conta.nova_conta()` como factory method |

## 📁 Estrutura do Projeto

```
sistema-bancario-POO/
│
├── sistema-POO.py   # Código principal — todas as classes e menu
└── README.md        # Documentação do projeto
```

---

# 🇺🇸 English

## 📋 About the Project

An evolution of the DIO banking system, migrating from plain dictionaries to **full Object-Oriented Programming (OOP)**. The system models customers, accounts, and transactions using classes, inheritance, abstract base classes, and custom iterators.

## ✨ Features

- Customer registration (Individual with CPF, name, date of birth and address)
- Checking account creation linked to customers
- Deposits and Withdrawals with business rule validation
- Limit of 3 daily withdrawals and per-operation limit (R$ 500.00)
- Bank statement with filterable transaction history
- Customer and account listing with custom iterator
- Generator (`yield`) for history reports

## 🗂️ UML Class Diagram

```
┌─────────────────────┐        ┌──────────────────────────┐
│      Cliente        │        │         Conta            │
├─────────────────────┤        ├──────────────────────────┤
│ - endereco          │1      *│ - saldo                  │
│ - contas: list      │────────│ - numero                 │
├─────────────────────┤        │ - agencia                │
│ + realizar_transacao│        │ - cliente                │
│ + adicionar_conta   │        │ - historico: Historico   │
└────────┬────────────┘        ├──────────────────────────┤
         │                     │ + sacar(valor)           │
         │ inherits            │ + depositar(valor)       │
         ▼                     │ + nova_conta() [cls]     │
┌─────────────────────┐        └────────────┬─────────────┘
│   PessoaFisica      │                     │ inherits
├─────────────────────┤                     ▼
│ - cpf               │        ┌──────────────────────────┐
│ - nome              │        │     ContaCorrente        │
│ - data_nascimento   │        ├──────────────────────────┤
└─────────────────────┘        │ - limite                 │
                               │ - limite_saques          │
┌─────────────────────┐        └──────────────────────────┘
│     Historico       │
├─────────────────────┤        ┌──────────────────────────┐
│ - transacoes: list  │        │      Transacao (ABC)     │
├─────────────────────┤        ├──────────────────────────┤
│ + adicionar_transacao│       │ + valor (abstract)       │
│ + gerar_relatorio() │        │ + registrar() (abstract) │
└─────────────────────┘        └────────────┬─────────────┘
                                            │ inherits
                               ┌────────────┴─────────────┐
                               ▼                          ▼
                    ┌──────────────────┐     ┌──────────────────┐
                    │    Deposito      │     │      Saque       │
                    ├──────────────────┤     ├──────────────────┤
                    │ + valor          │     │ + valor          │
                    │ + registrar()    │     │ + registrar()    │
                    └──────────────────┘     └──────────────────┘
```

## 🛠️ Tech Stack

| Technology | Usage |
|---|---|
| Python 3.10+ | Main language |
| `abc` (ABC, abstractmethod) | Abstract classes and methods |
| `datetime` | Timestamping transactions |
| Native OOP | Inheritance, encapsulation, polymorphism |

## 🚀 How to Run

**Prerequisite:** Python 3.10 or higher installed.

```bash
# 1. Clone the repository
git clone https://github.com/taissocout/sistema-bancario-POO.git

# 2. Enter the directory
cd sistema-bancario-POO

# 3. Run the system
python sistema-POO.py
```

## 🎮 Usage

```
╔══════════════════════════════════╗
║       BANCO DIO  •  Sistema      ║
╠══════════════════════════════════╣
║  [d] Deposit                     ║
║  [s] Withdraw                    ║
║  [e] Statement                   ║
║  [nc] New account                ║
║  [lc] List accounts              ║
║  [nu] New user                   ║
║  [lu] List users                 ║
║  [q] Quit                        ║
╚══════════════════════════════════╝
```

**Recommended flow:**
1. `[nu]` → Register a new customer
2. `[nc]` → Create a checking account for the customer
3. `[d]`  → Make a deposit
4. `[s]`  → Make a withdrawal
5. `[e]`  → Check the statement

## 🧱 OOP Concepts Applied

| Concept | Implementation |
|---|---|
| **Inheritance** | `PessoaFisica → Cliente`, `ContaCorrente → Conta`, `Deposito/Saque → Transacao` |
| **Abstraction** | `Transacao(ABC)` class with `@abstractmethod` |
| **Encapsulation** | `_private` attributes exposed via `@property` |
| **Polymorphism** | `ContaCorrente.sacar()` overrides `Conta.sacar()` |
| **Iterator Protocol** | `ContasIterador` with `__iter__` and `__next__` |
| **Generator** | `Historico.gerar_relatorio()` using `yield` |
| **`__repr__` / `__str__`** | Human-readable representations |
| **`@classmethod`** | `Conta.nova_conta()` as a factory method |

## 📁 Project Structure

```
sistema-bancario-POO/
│
├── sistema-POO.py   # Main code — all classes and menu
└── README.md        # Project documentation
```

---

<div align="center">

**Desenvolvido com 💙 durante a Trilha Python — [DIO](https://www.dio.me/)**  
**Developed with 💙 during the Python Track — [DIO](https://www.dio.me/)**

[![GitHub](https://img.shields.io/badge/GitHub-taissocout-181717?style=flat-square&logo=github)](https://github.com/taissocout)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-taissocout--cybersecurity-0A66C2?style=flat-square&logo=linkedin)](https://linkedin.com/in/taissocout-cybersecurity)

</div>
