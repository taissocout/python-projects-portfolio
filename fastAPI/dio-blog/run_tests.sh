#!/usr/bin/env bash
# run_tests.sh — executa todos os testes do dio-blog
# Uso: bash run_tests.sh [--coverage]

set -e

echo ""
echo "=========================================="
echo "  dio-blog — Suite de Testes"
echo "  Módulo: Testando APIs RESTful Assíncronas"
echo "=========================================="
echo ""

if [ "$1" == "--coverage" ]; then
    echo "Executando com cobertura de código..."
    python -m pytest tests/ -v --tb=short         --cov=. --cov-report=term-missing         --cov-report=html:htmlcov
    echo ""
    echo "Relatório HTML gerado em: htmlcov/index.html"
else
    echo "Executando testes..."
    python -m pytest tests/ -v --tb=short
fi

echo ""
echo "=========================================="
echo "  Testes concluídos!"
echo "=========================================="
