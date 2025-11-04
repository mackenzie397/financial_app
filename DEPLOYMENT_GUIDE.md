# Guia de Implantação: Vercel e PythonAnywhere

Este guia detalha os passos para publicar sua aplicação de forma gratuita, utilizando a Vercel para o frontend e o PythonAnywhere para o backend, sem a necessidade de cadastrar um cartão de crédito.

## Passo 1: Publicar o Backend no PythonAnywhere

O PythonAnywhere é uma plataforma especializada em hospedar aplicações Python. O plano gratuito é ideal para projetos pessoais.

### 1.1 Crie sua Conta
- Acesse [www.pythonanywhere.com](https://www.pythonanywhere.com) e crie uma conta gratuita ("Beginner").

### 1.2 Crie o Banco de Dados MySQL
1.  No painel do PythonAnywhere, vá para a aba **Databases**.
2.  Crie uma nova base de dados MySQL. Defina uma senha para o banco de dados e anote-a.
3.  Após a criação, o PythonAnywhere fornecerá o **host**, **nome de usuário** e **nome do banco de dados**. Anote essas informações.

### 1.3 Faça o Upload do Código
1.  Vá para a aba **Files**.
2.  Faça o download do seu projeto como um arquivo ZIP a partir do seu repositório Git (GitHub, GitLab, etc.).
3.  Faça o upload desse arquivo ZIP para o PythonAnywhere e descompacte-o. O seu código do backend deverá ficar em um diretório como `/home/seu-username/financial_app/backend/backend_app`.

### 1.4 Configure a Aplicação Web
1.  Vá para a aba **Web**.
2.  Clique em **"Add a new web app"**.
3.  Selecione o framework **Flask** e a versão do Python que você está usando (ex: Python 3.10).
4.  O PythonAnywhere criará um arquivo de configuração WSGI. **É crucial editá-lo corretamente.** Clique no link para o arquivo WSGI (algo como `/var/www/seu-username_pythonanywhere_com_wsgi.py`) e substitua o conteúdo pelo seguinte:

    ```python
    import sys
    import os

    # Adicione o caminho do seu projeto ao path
    project_home = u'/home/seu-username/financial_app/backend/backend_app'
    if project_home not in sys.path:
        sys.path = [project_home] + sys.path

    # Importe a aplicação a partir do seu arquivo wsgi.py
    from wsgi import app as application
    ```

### 1.5 Instale as Dependências e Configure o Banco de Dados
1.  Abra um **Bash console** a partir da aba **Consoles**.
2.  Crie e ative um ambiente virtual:
    ```bash
    virtualenv --python=python3.10 venv
    source venv/bin/activate
    ```
3.  Instale as dependências:
    ```bash
    pip install -r /home/seu-username/financial_app/backend/backend_app/requirements.txt
    ```
4.  Execute os comandos para criar as tabelas e popular o banco:
    ```bash
    python /home/seu-username/financial_app/backend/backend_app/manage.py create_db
    python /home/seu-username/financial_app/backend/backend_app/manage.py seed_db
    ```

### 1.6 Configure as Variáveis de Ambiente
1.  Na aba **Web**, vá para a seção **"Virtualenv"** e insira o caminho para o seu ambiente virtual: `/home/seu-username/venv`.
2.  Ainda na aba **Web**, vá para a seção **"Code"** e clique em **"Go to Directory"** ao lado de "Working directory" para garantir que o diretório de trabalho seja `/home/seu-username/financial_app/backend/backend_app`.
3.  Você precisará definir as variáveis de ambiente em um arquivo `.env` dentro do seu diretório de trabalho. Crie o arquivo `/home/seu-username/financial_app/backend/backend_app/.env` com o seguinte conteúdo:

    ```
    SECRET_KEY='gere-uma-chave-aleatoria-longa'
    JWT_SECRET_KEY='gere-outra-chave-aleatoria-longa'
    FLASK_CONFIG='production'
    CORS_ORIGINS='URL_DO_SEU_FRONTEND_NA_VERCEL'
    DATABASE_URL='mysql+pymysql://seu-username:sua-senha-mysql@host-mysql/seu-banco-de-dados'
    ```
    - **Importante:** Substitua os valores de `DATABASE_URL` pelos dados que você anotou no passo 1.2. Deixaremos o `CORS_ORIGINS` para depois.

### 1.7 Finalize
- Volte para a aba **Web** e clique no botão verde **Reload** para aplicar todas as alterações.
- Anote a URL do seu backend (ex: `seu-username.pythonanywhere.com`).

---

## Passo 2: Publicar o Frontend na Vercel

A Vercel é perfeita para hospedar aplicações frontend modernas.

### 2.1 Crie sua Conta
- Acesse [vercel.com](https://vercel.com) e crie uma conta gratuita, preferencialmente usando sua conta do GitHub/GitLab para facilitar a integração.

### 2.2 Importe o Projeto
1.  No painel da Vercel, clique em **"Add New... -> Project"**.
2.  Selecione o seu repositório Git.
3.  A Vercel detectará automaticamente que é um projeto Vite/React. Ela irá preencher os comandos de build e o diretório de publicação para você.

### 2.3 Configure as Variáveis de Ambiente
1.  Durante a configuração do projeto, vá para a seção **"Environment Variables"**.
2.  Adicione a seguinte variável:
    - **Name:** `VITE_API_BASE_URL`
    - **Value:** `https://seu-username.pythonanywhere.com/api` (a URL do seu backend com `/api` no final).

### 2.4 Faça o Deploy
- Clique em **"Deploy"**. A Vercel fará o build e a publicação do seu frontend.
- Ao final, ela fornecerá a URL pública do seu site (ex: `seu-projeto.vercel.app`).

---

## Passo 3: Conectar Tudo
1.  Pegue a URL do seu frontend na Vercel (ex: `https://seu-projeto.vercel.app`).
2.  Volte ao **PythonAnywhere**, vá para a aba **Files**, abra o seu arquivo `.env` e atualize a variável `CORS_ORIGINS` com a URL da Vercel.
3.  Vá para a aba **Web** no PythonAnywhere e clique no botão **Reload** mais uma vez.

**Pronto! Sua aplicação deve estar no ar e funcionando.**
