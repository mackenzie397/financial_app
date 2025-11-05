# Guia de Implantação: Vercel e PythonAnywhere

Este guia detalha os passos para publicar sua aplicação de forma gratuita, utilizando a Vercel para o frontend e o PythonAnywhere para o backend, sem a necessidade de cadastrar um cartão de crédito.

## Passo 1: Publicar o Backend no PythonAnywhere

### 1.1 Crie sua Conta
- Acesse [www.pythonanywhere.com](https://www.pythonanywhere.com) e crie uma conta gratuita ("Beginner").

### 1.2 Crie o Banco de Dados MySQL
1.  No painel do PythonAnywhere, vá para a aba **Databases**.
2.  Crie uma nova base de dados MySQL. **Defina uma senha segura e anote-a.**
3.  Após a criação, o PythonAnywhere fornecerá o **Hostname**, **Username** e **Database name**. Anote essas informações. Elas serão algo como:
    - **Hostname:** `seu-username.mysql.pythonanywhere-services.com`
    - **Username:** `seu-username`
    - **Database name:** `seu-username$default`

### 1.3 Faça o Upload e Preparação do Código
1.  Vá para a aba **Files**.
2.  Faça o download do seu projeto como um arquivo ZIP a partir do seu repositório Git.
3.  Faça o upload do arquivo ZIP (ex: `financial_app-master.zip`) para o diretório principal no PythonAnywhere.
4.  **Abra um "Bash console"** a partir da aba **Files** ou **Consoles**.
5.  No console, descompacte o arquivo:
    ```bash
    unzip financial_app-master.zip
    ```

### 1.4 Configure o Ambiente Virtual e as Dependências
1.  Ainda no console Bash, crie e ative um ambiente virtual. Use a mesma versão do Python que seu projeto.
    ```bash
    virtualenv --python=python3.10 venv
    source venv/bin/activate
    ```
    - **IMPORTANTE:** O seu prompt de comando deve mudar para `(venv) $`. Você deve reativar o ambiente com `source venv/bin/activate` sempre que abrir um novo console.
2.  Instale as dependências do projeto:
    ```bash
    pip install -r financial_app-master/financial_app/backend/backend_app/requirements.txt
    ```

### 1.5 Configure as Variáveis de Ambiente (.env)
1.  Este é um passo crucial. **Antes de interagir com o banco de dados**, você precisa criar o arquivo `.env`.
2.  No console Bash, use o editor `nano` para criar o arquivo:
    ```bash
    nano financial_app-master/financial_app/backend/backend_app/.env
    ```
3.  Copie e cole o conteúdo abaixo no editor:
    ```
    SECRET_KEY='gere-uma-chave-aleatoria-longa-e-segura-aqui'
    JWT_SECRET_KEY='gere-outra-chave-aleatoria-diferente-aqui'
    FLASK_CONFIG='production'
    CORS_ORIGINS='URL_DO_SEU_FRONTEND_NA_VERCEL'
    DATABASE_URL='mysql+pymysql://USERNAME:PASSWORD@HOSTNAME/DATABASE_NAME'
    ```
4.  **Substitua** `USERNAME`, `PASSWORD`, `HOSTNAME`, e `DATABASE_NAME` na linha `DATABASE_URL` com as informações reais do seu banco de dados que você anotou no **Passo 1.2**. Deixe o `CORS_ORIGINS` para depois.
5.  Pressione **Ctrl+O** para salvar, e **Ctrl+X** para sair do `nano`.

### 1.6 Crie e Popule o Banco de Dados
1.  No console Bash, certifique-se de que seu ambiente virtual ainda está ativo (`(venv) $`).
2.  Agora, execute os scripts de gerenciamento:
    ```bash
    python financial_app-master/financial_app/backend/backend_app/manage.py create_db
    python financial_app-master/financial_app/backend/backend_app/manage.py seed_db
    ```
3.  O segundo comando (`seed_db`) irá criar um usuário padrão e **imprimir a senha no console**. **Anote essas credenciais**, pois você precisará delas para o primeiro login.

### 1.7 Configure a Aplicação Web
1.  Vá para a aba **Web** no painel do PythonAnywhere.
2.  Clique em **"Add a new web app"**. Selecione o framework **Flask** e a mesma versão do Python do seu ambiente virtual.
3.  Clique no link para editar o arquivo **WSGI configuration**. Substitua o conteúdo dele por este:
    ```python
    import sys
    project_home = u'/home/seu-username/financial_app-master/financial_app/backend/backend_app'
    if project_home not in sys.path:
        sys.path = [project_home] + sys.path
    from wsgi import app as application
    ```
    - Lembre-se de substituir `seu-username` pelo seu nome de usuário.
4.  Na aba **Web**, vá para a seção **"Virtualenv"** e insira o caminho: `/home/seu-username/venv`.
5.  Anote a URL do seu backend (ex: `seu-username.pythonanywhere.com`).

---

## Passo 2: Publicar o Frontend na Vercel

### 2.1 Crie sua Conta e Importe o Projeto
1.  Acesse [vercel.com](https://vercel.com) e crie uma conta gratuita, de preferência usando sua conta do GitHub/GitLab.
2.  No painel, clique em **"Add New... -> Project"** e selecione seu repositório.
3.  A Vercel irá detectar automaticamente que é um projeto Vite/React e preencherá as configurações de build.

### 2.2 Configure a Variável de Ambiente
1.  Na tela de configuração do projeto, expanda a seção **"Environment Variables"**.
2.  Adicione a seguinte variável:
    - **Name:** `VITE_API_BASE_URL`
    - **Value:** `https://seu-username.pythonanywhere.com/api` (substitua com a URL do seu backend e adicione `/api` no final).

### 2.3 Faça o Deploy
- Clique em **"Deploy"**. Ao final, a Vercel fornecerá a URL pública do seu site (ex: `seu-projeto.vercel.app`).

---

## Passo 3: Conexão Final
1.  Copie a URL do seu frontend da Vercel.
2.  Volte ao **PythonAnywhere**, abra o arquivo `.env` novamente com o `nano`.
3.  Atualize a variável `CORS_ORIGINS` com a URL da Vercel.
4.  Vá para a aba **Web** no PythonAnywhere e clique no botão verde **Reload** para aplicar a última alteração.

**Sua aplicação está no ar!**
