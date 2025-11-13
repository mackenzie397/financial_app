# Financial App

Um aplicativo de organização financeira pessoal para gerenciar suas finanças de forma inteligente e eficiente.

## Visão Geral

Este projeto é um aplicativo financeiro full-stack, desenvolvido com um backend em Python (Flask) e um frontend em React. Ele permite aos usuários registrar transações, definir metas, acompanhar investimentos e visualizar relatórios detalhados de suas finanças.

## Funcionalidades

- **Autenticação de Usuário:** Registro e login seguros para gerenciar suas finanças pessoais.
  - Novo usuários recebem automaticamente categorias, formas de pagamento e tipos de investimento padrão
  
- **Gestão de Conta:** Editar informações da conta e alterar senha com segurança reforçada.
  - Menu dropdown com opções "Minha Conta" e "Sair"
  - Página "Minha Conta" com formulário de alteração de senha
  - Validação de senha antiga antes de permitir alteração
  - Requisitos de força de senha enforçados

- **Dashboard Interativo:** Visão geral rápida de saldo, receitas, despesas e investimentos.

- **Gestão de Transações:** Adicione, edite e exclua receitas e despesas, categorizando-as e associando-as a formas de pagamento.

- **Definição e Acompanhamento de Metas:** Crie metas financeiras e acompanhe seu progresso.

- **Gestão de Investimentos:** Registre e monitore seus investimentos, com diferentes tipos.

- **Relatórios Detalhados:** Visualize gráficos de despesas por categoria, uso por forma de pagamento e resumos de período.

- **Configurações Centralizadas:** Gerencie categorias e formas de pagamento em um único lugar.
  - Aba de Categorias para criar/editar/deletar categorias (despesa e receita)
  - Aba de Formas de Pagamento para gerenciar métodos de pagamento
  - Interface organizada com abas para melhor usabilidade

## Tecnologias Utilizadas

### Backend
- **Python:** Linguagem de programação principal.
- **Flask:** Microframework web para a API RESTful.
- **Flask-SQLAlchemy:** ORM para interação com o banco de dados.
- **Flask-JWT-Extended:** Para autenticação baseada em JWT.
- **SQLite:** Banco de dados leve e embutido (`app.db`).

### Frontend
- **React:** Biblioteca JavaScript para construção da interface do usuário.
- **Vite:** Ferramenta de build rápida para desenvolvimento frontend.
- **Tailwind CSS:** Framework CSS utilitário para estilização rápida e responsiva.
- **shadcn/ui:** Coleção de componentes UI reutilizáveis e acessíveis, construídos com Radix UI e Tailwind CSS.
- **Axios:** Cliente HTTP para comunicação com a API do backend.
- **React Router DOM:** Para roteamento no lado do cliente.

## Como Configurar e Rodar o Projeto

Siga as instruções abaixo para configurar e rodar o aplicativo em seu ambiente local.

### Pré-requisitos

Certifique-se de ter o seguinte instalado em sua máquina:
- Python 3.8+
- Node.js 18+
- pnpm (gerenciador de pacotes Node.js)

### 1. Configuração do Backend

```bash
# Navegue até o diretório do backend
cd financial_app/backend/backend_app

# Crie e ative um ambiente virtual
python -m venv venv
# No Windows
.\venv\Scripts\activate
# No macOS/Linux
source venv/bin/activate

# Instale as dependências do Python
pip install -r requirements.txt

# Inicialize o banco de dados (se necessário, pode ser feito via um script de migração ou ao rodar a aplicação pela primeira vez)
# Exemplo: flask --app src.main db upgrade (se houver Flask-Migrate configurado)
# Ou, se o banco de dados for criado automaticamente ao rodar:
# flask --app src.main run

# Rode o servidor Flask (o banco de dados será criado se não existir)
flask --app src.main run
```

O servidor backend estará rodando em `http://127.0.0.1:5000` (ou outra porta configurada).

### 2. Configuração do Frontend

```bash
# Navegue até o diretório do frontend
cd financial_app/frontend/frontend_app

# Instale as dependências do Node.js usando pnpm
pnpm install

# Rode o servidor de desenvolvimento do React
pnpm dev
```

O aplicativo frontend estará disponível em `http://localhost:5173` (ou outra porta que o Vite configurar).

## API Endpoints

### Autenticação
- `POST /api/register` - Registrar novo usuário (cria seeds automáticos)
- `POST /api/login` - Login de usuário
- `POST /api/logout` - Logout de usuário
- `GET /api/current_user` - Obter dados do usuário autenticado

### Conta do Usuário
- `POST /api/account/change-password` - Alterar senha (requer autenticação)
  - Body: `{ old_password: string, new_password: string }`
  - Validações: Senha antiga deve estar correta, nova senha deve ter força mínima, não pode ser igual a antiga
  - Rate limit: 5 tentativas por 15 minutos
  
- `PUT /api/account/update-profile` - Atualizar perfil (requer autenticação)
  - Body: `{ email?: string, username?: string }`
  - Validações: Email e username devem ser únicos

### Categorias
- `GET /api/categories` - Listar categorias do usuário
  - Query: `?category_type=expense|income` (opcional)
- `POST /api/categories` - Criar nova categoria
- `PUT /api/categories/{id}` - Atualizar categoria
- `DELETE /api/categories/{id}` - Deletar categoria

### Formas de Pagamento
- `GET /api/payment-methods` - Listar formas de pagamento
- `POST /api/payment-methods` - Criar nova forma de pagamento
- `PUT /api/payment-methods/{id}` - Atualizar forma de pagamento
- `DELETE /api/payment-methods/{id}` - Deletar forma de pagamento

### Transações, Metas, Investimentos
- Endpoints completos para CRUD de transações, metas, investimentos e tipos de investimento
- Veja `src/routes/` para documentação completa no Swagger (http://localhost:5000/apidocs/)

## Estrutura do Projeto

```
financial_app/
├── start_backend.ps1
├── start_frontend.ps1
├── .gitignore
├── README.md
├── CHANGELOG.md
├── PLANO_TECNICO.md
├── financial_app/
│   ├── backend/
│   │   └── backend_app/
│   │       ├── .env
│   │       ├── requirements.txt
│   │       ├── src/
│   │       │   ├── database/app.db
│   │       │   ├── models/...
│   │       │   ├── routes/...
│   │       │   └── main.py
│   │       └── ...
│   └── frontend/
│       └── frontend_app/
│           ├── .env
│           ├── package.json
│           ├── pnpm-lock.yaml
│           ├── vite.config.js
│           ├── src/
│           │   ├── components/...
│           │   ├── hooks/...
│           │   ├── lib/...
│           │   └── main.jsx
│           └── ...
```

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests.

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
