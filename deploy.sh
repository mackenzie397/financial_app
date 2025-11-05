#!/bin/bash

# Navega para o diretório do projeto
cd /home/Mackenzie/financial_app

# Ativa o ambiente virtual
source /home/Mackenzie/venv/bin/activate

# Puxa as últimas alterações do GitHub
git fetch --all
git reset --hard origin/master

# Instala novas dependências, se houver
pip install -r /home/Mackenzie/financial_app/backend/backend_app/requirements.txt

# Recarrega a aplicação web no PythonAnywhere
touch /var/www/mackenzie_pythonanywhere_com_wsgi.py
