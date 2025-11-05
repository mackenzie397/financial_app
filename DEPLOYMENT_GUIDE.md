# Guia de Implantação Automatizada: Vercel e PythonAnywhere

Este guia detalha os passos para publicar sua aplicação de forma gratuita e **automatizada**, utilizando a Vercel para o frontend e o PythonAnywhere para o backend. O deploy do backend será acionado automaticamente a cada `git push`.

**LEIA COM ATENÇÃO:** Siga os passos na ordem exata para garantir uma configuração correta.

---

## Passo 1: Configuração Inicial do Backend no PythonAnywhere

### 1.1 Crie sua Conta e Banco de Dados
1.  Acesse [www.pythonanywhere.com](https://www.pythonanywhere.com) e crie uma conta gratuita ("Beginner").
2.  No painel, vá para a aba **Databases**.
3.  Crie uma base de dados MySQL. **Defina uma senha segura e anote-a.**
4.  Anote as informações de conexão para usar no próximo passo.

### 1.2 Clone o Repositório e Crie o Arquivo de Configuração
1.  Abra um **"Bash console"** a partir do painel do PythonAnywhere.
2.  Clone seu repositório do GitHub (substitua com a URL do seu fork, se aplicável):
    ```bash
    git clone https://github.com/mackenzie397/financial_app.git
    ```
3.  Abra o editor de texto `nano` para criar seu arquivo de configuração:
    ```bash
    nano ~/financial_app/financial_app/backend/backend_app/.env
    ```
4.  **Copie, cole e edite** o conteúdo abaixo, substituindo os placeholders com suas informações reais.
    ```
    SECRET_KEY='gere-uma-chave-aleatoria-longa-e-segura-aqui'
    JWT_SECRET_KEY='gere-outra-chave-aleatoria-diferente-aqui'
    FLASK_CONFIG='production'
    CORS_ORIGINS='URL_DO_SEU_FRONTEND_NA_VERCEL' # Será preenchido depois
    WEBHOOK_SECRET='gere-uma-terceira-chave-aleatoria-para-o-webhook'

    # Configuração do Banco de Dados
    DB_USER='seu-username-do-pythonanywhere'
    DB_PASSWORD='sua-senha-do-banco-de-dados'
    DB_HOST='seu-username.mysql.pythonanywhere-services.com'
    DB_NAME='seu-username$default'
    ```
    - **IMPORTANTE:** Gere chaves seguras e aleatórias. Anote a `WEBHOOK_SECRET`, pois você a usará no GitHub.
    - Pressione **Ctrl+O** (salvar) e **Ctrl+X** (sair).

### 1.3 Crie o Ambiente Virtual e Instale as Dependências
1.  No mesmo console Bash, crie e ative o ambiente virtual:
    ```bash
    virtualenv --python=python3.10 ~/venv
    source ~/venv/bin/activate
    ```
    - Seu prompt deve mudar para `(venv) $`.
2.  Instale as dependências do projeto:
    ```bash
    pip install -r ~/financial_app/financial_app/backend/backend_app/requirements.txt
    ```

### 1.4 Crie as Tabelas e Popule os Dados
1.  Certifique-se de que o `(venv)` ainda está ativo.
2.  Execute os comandos para preparar o banco de dados:
    ```bash
    python ~/financial_app/financial_app/backend/backend_app/manage.py create_db
    python ~/financial_app/financial_app/backend/backend_app/manage.py seed_db
    ```

---

## Passo 2: Configurar a Aplicação Web e o Script de Deploy

### 2.1 Crie e Configure a Aplicação Web
1.  Vá para a aba **Web** no painel do PythonAnywhere.
2.  Clique em **"Add a new web app"**. Selecione **Flask** e **Python 3.10**.
3.  Na seção **"Virtualenv"**, insira o caminho: `/home/seu-username/venv`.
4.  Na seção **"Code"**, clique no link **"WSGI configuration file"**. Apague todo o conteúdo e substitua pelo código abaixo (ajuste `seu-username`):
    ```python
    import sys
    from dotenv import load_dotenv
    import os

    # Caminho para a pasta do projeto que contém o .env
    project_path = f'/home/{os.environ["USER"]}/financial_app/financial_app/backend/backend_app'

    # Caminho para a pasta 'src' que contém o 'main.py'
    src_path = os.path.join(project_path, 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    # Carrega as variáveis de ambiente
    dotenv_path = os.path.join(project_path, '.env')
    load_dotenv(dotenv_path)

    # Cria a aplicação
    from main import create_app
    application = create_app(os.getenv('FLASK_CONFIG') or 'production')
    ```
5.  Salve o arquivo e volte para a aba **Web**.

### 2.2 Crie o Script de Deploy
1.  Volte ao seu **console Bash**.
2.  Crie o script de deploy com o `nano`:
    ```bash
    nano ~/deploy.sh
    ```
3.  Copie e cole o conteúdo abaixo (ajuste `seu-username`):
    ```bash
    #!/bin/bash
    cd /home/seu-username/financial_app/
    source /home/seu-username/venv/bin/activate
    git fetch --all
    git reset --hard origin/master
    pip install -r /home/seu-username/financial_app/financial_app/backend/backend_app/requirements.txt
    touch /var/www/seu-username_pythonanywhere_com_wsgi.py
    echo "Deploy finalizado!"
    ```
4.  Salve com **Ctrl+O** e **Ctrl+X**.
5.  Torne o script executável:
    ```bash
    chmod +x ~/deploy.sh
    ```

---

## Passo 3: Publicar o Frontend e Ativar o Deploy Automático

### 3.1 Publique o Frontend na Vercel
1.  Acesse [vercel.com](https://vercel.com), crie uma conta e conecte seu repositório Git.
2.  Adicione um novo projeto e selecione seu repositório.
3.  Em **"Environment Variables"**, adicione:
    - **Name:** `VITE_API_BASE_URL`
    - **Value:** `https://seu-username.pythonanywhere.com/api` (substitua com a URL do seu backend).
4.  Clique em **"Deploy"**. Ao final, anote a URL pública do seu site.

### 3.2 Conexão Final e Webhook
1.  Volte ao **PythonAnywhere** e edite seu arquivo `.env` para atualizar a variável `CORS_ORIGINS` com a URL da Vercel.
2.  Vá para a aba **Web** no PythonAnywhere e clique no botão verde **Reload**.
3.  **No GitHub**, vá para o seu repositório -> **Settings** -> **Webhooks**.
4.  Clique em **"Add webhook"** e preencha:
    - **Payload URL:** `http://seu-username.pythonanywhere.com/webhook-deploy`
    - **Content type:** `application/json`
    - **Secret:** Cole o valor da sua `WEBHOOK_SECRET` que você anotou.
5.  Clique em **"Add webhook"**.

**Pronto!** A partir de agora, todo `git push` para a branch `master` irá automaticamente atualizar sua aplicação no PythonAnywhere.
