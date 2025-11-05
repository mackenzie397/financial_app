# Guia de Implantação: Vercel e PythonAnywhere (Versão Final)

Este guia detalha os passos para publicar sua aplicação de forma gratuita, utilizando a Vercel para o frontend e o PythonAnywhere para o backend.

**LEIA COM ATENÇÃO:** Siga os passos na ordem exata para evitar erros.

---

## Passo 1: Publicar o Backend no PythonAnywhere

### 1.1 Crie sua Conta
- Acesse [www.pythonanywhere.com](https://www.pythonanywhere.com) e crie uma conta gratuita ("Beginner").

### 1.2 Crie o Banco de Dados MySQL
1.  No painel, vá para a aba **Databases**.
2.  Crie uma base de dados MySQL. **Defina uma senha segura e anote-a.**
3.  Anote as informações de conexão:
    - **Hostname:** `seu-username.mysql.pythonanywhere-services.com`
    - **Username:** `seu-username`
    - **Database name:** `seu-username$default`

### 1.3 Upload e Preparação do Código
1.  Vá para a aba **Files**.
2.  Faça o download do seu projeto como um arquivo ZIP a partir do seu repositório Git.
3.  Faça o upload do arquivo ZIP (ex: `financial_app-master.zip`) para o diretório principal.
4.  **Abra um "Bash console"** a partir da aba **Files** ou **Consoles**.
5.  No console, descompacte o arquivo:
    ```bash
    unzip financial_app-master.zip
    ```

### 1.4 Configuração do Ambiente e Banco de Dados (Passos Críticos)

**IMPORTANTE:** Execute os comandos a seguir na ordem exata dentro do mesmo console Bash.

1.  **Crie e Ative o Ambiente Virtual:**
    ```bash
    virtualenv --python=python3.10 venv
    source venv/bin/activate
    ```
    - Seu prompt deve mudar para `(venv) $`.

2.  **Instale as Dependências:**
    ```bash
    pip install -r financial_app-master/financial_app/backend/backend_app/requirements.txt
    ```

3.  **Crie o Arquivo de Variáveis de Ambiente (.env):**
    - Este passo **deve** ser feito antes de criar o banco.
    - Use o editor `nano` para criar o arquivo:
    ```bash
    nano financial_app-master/financial_app/backend/backend_app/.env
    ```
    - Copie, cole e **edite** o conteúdo abaixo, substituindo os placeholders com suas informações reais.
    ```
    SECRET_KEY='gere-uma-chave-aleatoria-longa-e-segura-aqui'
    JWT_SECRET_KEY='gere-outra-chave-aleatoria-diferente-aqui'
    FLASK_CONFIG='production'
    CORS_ORIGINS='URL_DO_SEU_FRONTEND_NA_VERCEL' # Deixe como está por enquanto
    DATABASE_URL='mysql+pymysql://seu-username:sua-senha-aqui@seu-username.mysql.pythonanywhere-services.com/seu-username$default'
    ```
    - Pressione **Ctrl+O** (salvar) e **Ctrl+X** (sair).

4.  **Crie as Tabelas e Popule os Dados:**
    - Certifique-se de que o `(venv)` ainda está ativo.
    - Execute os comandos:
    ```bash
    python financial_app-master/financial_app/backend/backend_app/manage.py create_db
    python financial_app-master/financial_app/backend/backend_app/manage.py seed_db
    ```
    - O segundo comando irá popular o banco com o usuário `default_user` e a senha `default_password`.

### 1.5 Configure a Aplicação Web
1.  Vá para a aba **Web** no painel do PythonAnywhere.
2.  Clique em **"Add a new web app"**. Selecione **Flask** e a mesma versão do Python do seu ambiente virtual.
3.  Edite o arquivo **WSGI configuration file**. Apague tudo e substitua pelo código abaixo (ajuste `seu-username`):
    ```python
    import sys
    project_home = u'/home/seu-username/financial_app-master/financial_app/backend/backend_app'
    if project_home not in sys.path:
        sys.path = [project_home] + sys.path
    from wsgi import app as application
    ```
4.  Na aba **Web**, vá para a seção **"Virtualenv"** e insira o caminho: `/home/seu-username/venv`.
5.  Anote a URL do seu backend (ex: `seu-username.pythonanywhere.com`).

---

## Passo 2: Publicar o Frontend na Vercel

1.  Acesse [vercel.com](https://vercel.com) e crie uma conta gratuita, conectando seu repositório Git.
2.  No painel, adicione um novo projeto e selecione seu repositório.
3.  Na configuração, em **"Environment Variables"**, adicione:
    - **Name:** `VITE_API_BASE_URL`
    - **Value:** `https://seu-username.pythonanywhere.com/api` (substitua com a URL do seu backend).
4.  Clique em **"Deploy"**. Ao final, anote a URL pública do seu site.

---

## Passo 3: Conexão Final
1.  Copie a URL do seu frontend da Vercel.
2.  Volte ao **PythonAnywhere**, abra o arquivo `.env` novamente com o `nano`.
3.  Atualize a variável `CORS_ORIGINS` com a URL da Vercel.
4.  Vá para a aba **Web** no PythonAnywhere e clique no botão verde **Reload**.

**Sua aplicação está no ar!** Faça o login com `default_user` e `default_password` e **altere sua senha imediatamente.**

---

## Solução de Problemas (Troubleshooting)

**Se o comando `seed_db` falhar ou você precisar recomeçar:**

1.  Vá para a aba **Databases** no PythonAnywhere.
2.  **Delete** seu banco de dados atual.
3.  Crie um novo banco de dados MySQL (você pode usar a mesma senha).
4.  Abra um **Bash console**, ative o `venv` e execute novamente os comandos `create_db` e `seed_db`.
