#!/usr/bin/env bash
# exit on error
set -o errexit

# Navegar para o diretório onde manage.py está localizado
cd financial_app/backend/backend_app

# Executar os comandos de banco de dados
python manage.py create_db
python manage.py seed_db
