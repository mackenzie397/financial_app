# PLANO TÉCNICO - Melhorias de Configurações e Conta do Usuário

## 1. ANÁLISE DO REPOSITÓRIO ATUAL

### 1.1 Frameworks e Tecnologias

#### Backend
- **Framework**: Flask (3.1.2) - Microframework web Python
- **ORM**: Flask-SQLAlchemy (3.1.1) com SQLite
- **Autenticação**: Flask-JWT-Extended (4.7.1) com cookies seguros
- **Migrations**: Alembic (1.17.1) via Flask-Migrate (4.1.0)
- **Validações**: Bleach (6.3.0) para sanitizar entrada
- **API Documentation**: Flasgger (0.9.7.1) com Swagger
- **Rate Limiting**: Flask-Limiter (4.0.0)
- **CORS**: Flask-CORS (6.0.1)

#### Frontend
- **Framework**: React 18+ com Vite (build tool)
- **Roteamento**: React Router DOM
- **Estilização**: Tailwind CSS 4 com shadcn/ui
- **Cliente HTTP**: Axios
- **Componentes**: shadcn/ui + Radix UI (acessível)
- **Ícones**: Lucide React
- **Validação**: React Hook Form com resolvers
- **Notificações**: Sonner (toasts)

### 1.2 Estrutura de Pastas

#### Backend
```
backend_app/
├── src/
│   ├── main.py                    # App factory + seed_initial_data()
│   ├── config.py                  # Configurações (dev/test/prod)
│   ├── extensions.py              # JWT, Limiter, Migrate
│   ├── middleware.py              # CSP headers
│   ├── logging_config.py          # Logging setup
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── user.py                # User model (id, username, email, password_hash)
│   │   ├── category.py            # Category (id, name, user_id, category_type)
│   │   ├── payment_method.py       # PaymentMethod (id, name, user_id)
│   │   ├── transaction.py          # Transaction model
│   │   ├── goal.py                # Goal model
│   │   ├── investment.py          # Investment model
│   │   └── investment_type.py      # InvestmentType model
│   ├── routes/                    # API endpoints (blueprints)
│   │   ├── user.py                # /register, /login, /logout, /current_user
│   │   ├── category.py            # CRUD categorias
│   │   ├── payment_method.py       # CRUD formas de pagamento
│   │   ├── transaction.py          # CRUD transações
│   │   ├── goal.py                # CRUD metas
│   │   ├── investment.py          # CRUD investimentos
│   │   ├── investment_type.py      # CRUD tipos de investimento
│   │   └── admin.py               # Admin routes
│   └── static/                    # Frontend SPA (index.html)
├── tests/                         # Pytest unit/integration tests
│   ├── conftest.py                # Fixtures (app, client, auth_client)
│   ├── test_seeding.py            # Tests para seed_initial_data()
│   └── test_*_routes.py           # Tests para cada rota
├── requirements.txt               # Dependências pip
└── manage.py                      # Flask CLI manager

migrations/
├── alembic.ini                    # Alembic config
├── env.py                         # Migration script
└── versions/
    └── 0462e90aa02c_initial_migration.py
```

#### Frontend
```
frontend_app/
├── src/
│   ├── App.jsx                    # Root component com Routes
│   ├── main.jsx                   # React entry point
│   ├── components/
│   │   ├── Dashboard.jsx          # Componente principal (header + nav + views)
│   │   ├── AuthPage.jsx           # Login/Register
│   │   ├── DashboardPage.jsx      # Vista do Dashboard
│   │   ├── Categories.jsx         # CRUD de Categorias (será movido para Settings)
│   │   ├── PaymentMethods.jsx     # CRUD de Formas de Pagamento (novo)
│   │   ├── Settings.jsx           # Configurações (stub, será expandido)
│   │   ├── GoalsPage.jsx          # Metas
│   │   ├── Charts.jsx             # Relatórios
│   │   ├── ProtectedRoute.jsx     # Wrapper para rotas protegidas
│   │   ├── TransactionForm.jsx    # Formulário de transações
│   │   └── ui/                    # shadcn/ui components
│   ├── hooks/
│   │   ├── useAuth.jsx            # Context + hooks para autenticação
│   │   └── useDashboard.jsx       # Hooks para dados do dashboard
│   ├── context/
│   │   ├── ThemeProvider.jsx      # Tema (claro/escuro)
│   │   └── AuthContext.jsx        # (já dentro useAuth.jsx)
│   ├── lib/
│   │   ├── api.js                 # Axios instance + todas as chamadas API
│   │   └── utils.js               # Funções utilitárias
│   ├── assets/                    # Imagens, ícones estáticos
│   └── index.css                  # CSS global
├── vite.config.js                 # Vite build config
├── tailwind.config.js             # Tailwind CSS config
├── package.json                   # Dependências npm
└── public/                        # Arquivos estáticos
```

### 1.3 Pontos de Entrada

#### Backend
1. **`src/main.py:create_app()`** - Factory que cria a aplicação Flask
   - Inicializa extensões (db, jwt, limiter, migrate)
   - Registra blueprints (rotas)
   - Configura CORS, error handlers, logging
   - **IMPORTANTE**: `seed_initial_data()` é chamado no `flask --app src.main run`

2. **`src/main.py:seed_initial_data()`** - Função que popula dados iniciais
   - Cria usuário padrão se não existir
   - Seed de categorias, payment methods, investment types para o usuário
   - **PROBLEMA ATUAL**: Só faz seed de dados genéricos, não por usuário no registro

3. **Blueprints registrados**:
   - `user_bp` → `/api/register`, `/api/login`, `/api/logout`, `/api/current_user`
   - `category_bp` → `/api/categories/*`
   - `payment_method_bp` → `/api/payment-methods/*`
   - `transaction_bp`, `investment_bp`, `goal_bp`, `investment_type_bp`

#### Frontend
1. **`src/App.jsx`** - Root component com routing (ProtectedRoute + AuthProvider)
2. **`src/components/Dashboard.jsx`** - Layout principal
   - Header com "Sair" button e "Bem vindo, {username}!"
   - Nav com abas: Dashboard, Metas, Categorias, Relatórios, Configurações
   - Renderização condicional por `activeView`
3. **`src/hooks/useAuth.jsx`** - AuthProvider + useAuth hook
   - Gerencia estado do usuário, login, logout
   - Verifica `/current_user` no mount

---

## 2. ONDE É FEITO O CADASTRO DE NOVOS USUÁRIOS

### Backend: Fluxo de Registro

**Arquivo**: `src/routes/user.py:register()`

```python
@user_bp.route("/register", methods=["POST"])
def register():
    # Valida username, email, password (force strength requirements)
    # Cria User no banco
    # Retorna 201 (sem fazer seed automático!)
```

**PROBLEMA IDENTIFICADO**:
- Após `POST /register`, o novo usuário é criado **SEM** categorias, payment methods ou investment types
- Isso causa erro quando o usuário tenta adicionar uma transação (precisa de category_id)
- A função `seed_initial_data()` só é executada quando chamada manualmente

### Frontend: Fluxo de Registro

**Arquivo**: `src/hooks/useAuth.jsx:register()`

```javascript
const register = async (username, email, password) => {
  await api.post('/register', { username, email, password });
  return { success: true };
  // Não faz login automático após registro
};
```

**Arquivo**: `src/components/AuthPage.jsx`
- Form de registro que chama `register()`
- Após sucesso, redireciona para login

---

## 3. ESTRUTURA ATUAL DE CATEGORIAS E FORMAS DE PAGAMENTO

### Backend - Modelos

**Category** (`src/models/category.py`):
```python
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_type = db.Column(db.String(20), nullable=False, default='expense')
    # Pode ser 'expense' ou 'income'
```

**PaymentMethod** (`src/models/payment_method.py`):
```python
class PaymentMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
```

### Backend - Rotas (CRUD)

Ambas têm rotas completas com `@jwt_required()`:

**Categories**: 
- `POST /api/categories` - add
- `GET /api/categories` - list (com filtro `?category_type=expense|income`)
- `GET /api/categories/<id>`
- `PUT /api/categories/<id>` - update
- `DELETE /api/categories/<id>`

**Payment Methods**:
- `POST /api/payment-methods` - add
- `GET /api/payment-methods` - list
- `GET /api/payment-methods/<id>`
- `PUT /api/payment-methods/<id>` - update
- `DELETE /api/payment-methods/<id>`

### Frontend - Componentes

**Categories.jsx** (`src/components/Categories.jsx`):
- Chama `getCategories()`, `addCategory()`, `deleteCategory()` via `lib/api.js`
- Form com Input + Select (tipo) + Button "Adicionar"
- Table com lista de categorias + delete button

**Settings.jsx** (`src/components/Settings.jsx`):
- **Está vazio!** Só tem placeholder
- É mostrado quando `activeView === 'settings'`

---

## 4. PLANO DETALHADO DE IMPLEMENTAÇÃO

### 4.1 Objetivo 1: Criar Automaticamente Categorias e Formas de Pagamento para Novos Usuários

#### Problema Atual
- Usuário registra → sem categorias → erro ao tentar criar transação
- Seeds só existem para usuário padrão (`default_user`)

#### Solução Proposta

**Backend** - Modificar `src/routes/user.py:register()`:

```python
@user_bp.route("/register", methods=["POST"])
def register():
    # ... validações existentes ...
    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()  # Commita o user
    
    # ✅ NOVO: Seed automático para este usuário
    _seed_user_defaults(new_user.id)
    
    return jsonify({"message": "User registered successfully"}), 201

def _seed_user_defaults(user_id):
    """Cria categorias e formas de pagamento padrão para novo usuário"""
    default_categories = [
        Category(user_id=user_id, name='Alimentação', category_type='expense'),
        Category(user_id=user_id, name='Transporte', category_type='expense'),
        Category(user_id=user_id, name='Diversão', category_type='expense'),
        Category(user_id=user_id, name='Saúde', category_type='expense'),
        Category(user_id=user_id, name='Moradia', category_type='expense'),
        Category(user_id=user_id, name='Salário', category_type='income'),
        Category(user_id=user_id, name='Freelance', category_type='income'),
    ]
    
    default_payment_methods = [
        PaymentMethod(user_id=user_id, name='Dinheiro'),
        PaymentMethod(user_id=user_id, name='Cartão de Débito'),
        PaymentMethod(user_id=user_id, name='Cartão de Crédito'),
        PaymentMethod(user_id=user_id, name='PIX'),
    ]
    
    default_investment_types = [
        InvestmentType(user_id=user_id, name='Renda Fixa'),
        InvestmentType(user_id=user_id, name='Ações'),
        InvestmentType(user_id=user_id, name='Fundos Imobiliários'),
    ]
    
    db.session.bulk_save_objects(default_categories + default_payment_methods + default_investment_types)
    db.session.commit()
```

#### Impacto
- ✅ Novo usuário já tem dados básicos
- ✅ Sem necessidade de seed manual
- ✅ Reduz erros de categoria não encontrada
- ⚠️ Migration não necessária (mesma estrutura de tabelas)

---

### 4.2 Objetivo 2: Adicionar CRUD de Formas de Pagamento em Configurações

#### Estrutura Proposta

**Frontend - Nova Estrutura de Settings**:

```jsx
// src/components/Settings.jsx

<div className="space-y-6">
  <Tabs defaultValue="categories">
    <TabsList>
      <TabsTrigger value="categories">Categorias</TabsTrigger>
      <TabsTrigger value="payment-methods">Formas de Pagamento</TabsTrigger>
      <TabsTrigger value="investment-types">Tipos de Investimento</TabsTrigger>
    </TabsList>
    
    <TabsContent value="categories">
      <CategoriesManager />  {/* Componente refatorado de Categories.jsx */}
    </TabsContent>
    
    <TabsContent value="payment-methods">
      <PaymentMethodsManager />  {/* Novo componente */}
    </TabsContent>
    
    <TabsContent value="investment-types">
      <InvestmentTypesManager />  {/* Novo componente */}
    </TabsContent>
  </Tabs>
</div>
```

**Arquivo**: `src/components/Settings.jsx` (será reescrito)

**Componentes Filhos**:
- `src/components/settings/CategoriesManager.jsx` (refatorado de Categories.jsx)
- `src/components/settings/PaymentMethodsManager.jsx` (novo)
- `src/components/settings/InvestmentTypesManager.jsx` (novo, opcional)

#### Backend
- Rotas já existem! Só precisa refatorar frontend
- Routs estão em `/api/payment-methods`, `/api/categories`, `/api/investment-types`

#### Impacto
- ✅ CRUD de formas de pagamento acessível no mesmo lugar que categorias
- ✅ Melhor UX - tudo em um lugar
- ✅ Backend já suporta (sem mudanças)
- ⚠️ Migração de componentes (Categories.jsx → CategoriesManager.jsx)

---

### 4.3 Objetivo 3: Remover Aba "Categorias" do Menu Principal

#### Mudanças Propostas

**Frontend - Dashboard.jsx**:

```jsx
// ❌ REMOVER este button:
<button onClick={() => setActiveView('categories')}>
  Categorias
</button>

// ✅ MANTER:
<button onClick={() => setActiveView('settings')}>
  Configurações
</button>
```

**Mudança de Lógica**:
```jsx
// Remover este bloco:
{activeView === 'categories' && (
  <div>
    <Categories />
  </div>
)}
```

#### Backend
- Sem mudanças (rotas continuam funcionando)

#### Impacto
- ✅ Menu mais limpo
- ✅ Funcionalidade completa mantida (em Settings)
- ✅ Sem breaking changes
- ⚠️ Redirecionar usuários que tiverem abas salvass

---

### 4.4 Objetivo 4: Menu Logout com Opções ("Minha Conta", "Sair")

#### Novo Layout do Header

```jsx
// Antes:
<button onClick={logout}>Sair</button>

// Depois:
<DropdownMenu>
  <DropdownMenuTrigger>
    {user.username} ▼
  </DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuItem onClick={() => setActiveView('account')}>
      Minha Conta
    </DropdownMenuItem>
    <DropdownMenuSeparator />
    <DropdownMenuItem onClick={logout}>
      Sair
    </DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

#### Componentes Novos

**Frontend - `src/components/AccountPage.jsx`**:

```jsx
// Nova página com:
// - Exibir usuário (username, email)
// - Form para alterar senha
// - Opcionalmente: editar email, etc.
// - Botão "Salvar" chama POST /api/account/change-password
```

**Frontend - Dashboard.jsx**:
- Adiciona `activeView === 'account'` com `<AccountPage />`

#### Backend - Nova Rota em `src/routes/user.py`

```python
@user_bp.route("/account/change-password", methods=["POST"])
@jwt_required()
def change_password():
    """
    Altera a senha do usuário autenticado.
    Requer:
    - old_password: senha atual (para validação)
    - new_password: nova senha (mesmos requisitos de força)
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not user.check_password(old_password):
        return jsonify({"message": "Old password is incorrect"}), 401
    
    if len(new_password) < 8 or ...  # validações de força
        return jsonify({"message": "Password does not meet requirements"}), 400
    
    if old_password == new_password:
        return jsonify({"message": "New password must be different"}), 400
    
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({"message": "Password changed successfully"}), 200
```

**Endpoint adicional (opcional)**:
```python
@user_bp.route("/account/update-profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """
    Atualiza dados do perfil do usuário (email, username)
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    
    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"message": "Email already in use"}), 409
        user.email = data['email']
    
    if 'username' in data and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({"message": "Username already in use"}), 409
        user.username = data['username']
    
    db.session.commit()
    return jsonify(user.to_dict()), 200
```

#### API Frontend - Adicionar em `src/lib/api.js`

```javascript
// Account/User Profile
export const changePassword = (passwordData) => 
  api.post('/account/change-password', passwordData);

export const updateProfile = (profileData) => 
  api.put('/account/update-profile', profileData);
```

#### Impacto
- ✅ Menu mais profissional
- ✅ Acesso a dados de conta
- ✅ Possibilidade de trocar senha
- ✅ Segurança: valida senha antiga antes de trocar
- ⚠️ Migration de BD não necessária
- ⚠️ Nova rota que requer JWT

---

## 5. RISCOS E DEPENDÊNCIAS

### 5.1 Riscos Identificados

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|--------|-----------|
| Usuários antigos sem seeds | Alta | Alto | Criar migration que seed dados para users sem categorias |
| Transaction sem category válida | Alto | Crítico | Validar que novo user tem categorias antes de permitir transação |
| Breaking change em API existente | Baixo | Alto | Manter rotas antigas, adicionar novas endpoints |
| Password strength validation inconsistência | Média | Médio | Centralizar validação em helper function |
| CSRF/XSS em form de senha | Baixo | Crítico | Usar Bleach para sanitização, manter HTTPS, implementar rate limit |
| Conflito de abas no Dashboard | Baixo | Baixo | Valor padrão de `activeView` ao remover 'categories' |

### 5.2 Dependências Técnicas

- ✅ Flask-JWT-Extended (autenticação) - já instalado
- ✅ SQLAlchemy ORM - já instalado
- ✅ Radix UI/shadcn/ui (DropdownMenu, Tabs) - já instalado
- ⚠️ Password hashing via werkzeug - já instalado, validar complexity
- ⚠️ Rate limiting - Flask-Limiter já instalado, aplicar em change-password
- ⚠️ Frontend routing - React Router já instalado

### 5.3 Testes Necessários

**Backend**:
- [ ] `test_register_creates_default_seeds()` - Novo user tem categorias
- [ ] `test_change_password_validation()` - Valida senha força
- [ ] `test_change_password_requires_old_password()` - Segurança
- [ ] `test_payment_methods_accessible()` - CRUD funciona

**Frontend**:
- [ ] Categoria com aba removida redireciona para settings
- [ ] Dropdown menu carrega com user.username
- [ ] AccountPage form valida força de senha
- [ ] PaymentMethodsManager CRUD completo

---

## 6. ESTRUTURA DE COMMITS PROPOSTOS

```bash
# Branch: feature/settings-account-improvements

# Commit 1: Seeds automáticos para novos usuários
git commit -m "feat: seed default categories and payment methods on user registration"

# Commit 2: Componente Settings expandido com tabs
git commit -m "feat: create Settings page with tabs for categories and payment methods"

# Commit 3: Refatorar Categories.jsx
git commit -m "refactor: move Categories to Settings/CategoriesManager component"

# Commit 4: Novo componente PaymentMethodsManager
git commit -m "feat: add PaymentMethodsManager component to Settings"

# Commit 5: Remover aba Categorias do menu
git commit -m "feat: remove Categories tab from main navigation"

# Commit 6: Implementar dropdown menu de usuário
git commit -m "feat: implement user dropdown menu with My Account and Logout"

# Commit 7: Nova página AccountPage
git commit -m "feat: create AccountPage with change password functionality"

# Commit 8: Backend endpoint change-password
git commit -m "feat: add POST /api/account/change-password endpoint"

# Commit 9: API frontend para change-password
git commit -m "feat: add changePassword function to api.js"

# Commit 10: Testes para novos endpoints
git commit -m "test: add tests for user registration seeds and change password"

# Commit 11: Migration para seed usuários existentes (if needed)
git commit -m "feat: create migration to seed categories for existing users"

# Commit 12: Documentação
git commit -m "docs: update README and CHANGELOG with new features"
```

---

## 7. MUDANÇAS RESUMIDAS POR ARQUIVO

### Backend (src/)

| Arquivo | Mudança | Tipo |
|---------|---------|------|
| `routes/user.py` | Adicionar `_seed_user_defaults()` + call em `register()` | FEATURE |
| `routes/user.py` | Adicionar `POST /account/change-password` | FEATURE |
| `routes/user.py` | Adicionar `PUT /account/update-profile` (opcional) | FEATURE |
| `tests/test_user_routes.py` | Adicionar testes para novos endpoints | TEST |
| `tests/test_seeding.py` | Verificar seeds para novo user | TEST |

### Frontend (src/)

| Arquivo | Mudança | Tipo |
|---------|---------|------|
| `components/Dashboard.jsx` | Remover button categories, implementar dropdown | FEATURE |
| `components/Settings.jsx` | Reescrever com Tabs + ManagerComponents | FEATURE |
| `components/AccountPage.jsx` | NOVO - Página de conta do usuário | FEATURE |
| `components/settings/CategoriesManager.jsx` | NOVO - Categories refatorado | REFACTOR |
| `components/settings/PaymentMethodsManager.jsx` | NOVO - CRUD de formas de pagamento | FEATURE |
| `lib/api.js` | Adicionar `changePassword()`, `updateProfile()` | FEATURE |

### Database

| Item | Mudança | Tipo |
|------|---------|------|
| Migrations | (Nenhuma necessária) | N/A |
| Seeds | Automatizar no register | FEATURE |

---

## 8. SEGURANÇA

### 8.1 Autenticação e Autorização

✅ **JWT com Cookies Seguros**:
- Já implementado via `flask-jwt-extended`
- Cookies com `JWT_COOKIE_SECURE=True` (HTTPS only)
- SameSite=None para CORS

✅ **Rate Limiting**:
- Implementar em `/account/change-password` (limite: 5 tentativas/15min)
- Já existe rate limit em `/register` (10/min) e `/login` (10/min)

### 8.2 Validação de Entrada

✅ **Password Strength**:
- Mínimo 8 caracteres
- 1 letra maiúscula
- 1 letra minúscula
- 1 número
- 1 caractere especial

⚠️ **Sanitização**:
- Usar `bleach.clean()` para username, email no change-password
- Não sanitizar password (pode conter caracteres válidos)

### 8.3 Operações Sensíveis

⚠️ **Change Password**:
- Requer senha antiga (validação)
- Não pode usar mesma senha
- Não fazer logout automático (deixa sessão ativa)
- Rate limit: 5 tentativas por 15 minutos

⚠️ **Update Profile**:
- Validar email unique
- Validar username unique
- Não permitir duplicação de conta

---

## 9. PLANO DE TESTES

### 9.1 Testes Backend

**Arquivo**: `tests/test_user_routes.py`

```python
def test_register_seeds_default_categories(client):
    """Verifica que novo user tem categorias padrão após registro"""
    response = client.post('/api/register', json={...})
    assert response.status_code == 201
    
    # Login e verifica categorias
    login_response = client.post('/api/login', json={...})
    categories = client.get('/api/categories', headers={...})
    assert len(categories.json) > 0

def test_change_password_requires_old_password(auth_client):
    """Testa segurança: precisa senha antiga"""
    client, user = auth_client
    response = client.post('/api/account/change-password', json={
        'old_password': 'WrongPassword123!',
        'new_password': 'NewPassword123!'
    })
    assert response.status_code == 401

def test_change_password_validates_strength(auth_client):
    """Testa que nova senha precisa cumprir requisitos"""
    client, user = auth_client
    response = client.post('/api/account/change-password', json={
        'old_password': 'Password123!',
        'new_password': 'weak'
    })
    assert response.status_code == 400

def test_change_password_success(auth_client):
    """Testa mudança de senha bem-sucedida"""
    client, user = auth_client
    response = client.post('/api/account/change-password', json={
        'old_password': 'Password123!',
        'new_password': 'NewPassword123!'
    })
    assert response.status_code == 200
    
    # Verify login com nova senha funciona
    login = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'NewPassword123!'
    })
    assert login.status_code == 200
```

### 9.2 Testes Frontend

**Arquivo**: `src/components/__tests__/Settings.test.jsx` (novo)

```javascript
import { render, screen, userEvent } from '@testing-library/react';
import Settings from '../Settings';

describe('Settings', () => {
  test('renders tabs for categories and payment methods', () => {
    render(<Settings />);
    expect(screen.getByText('Categorias')).toBeInTheDocument();
    expect(screen.getByText('Formas de Pagamento')).toBeInTheDocument();
  });

  test('clicking payment methods tab shows manager', async () => {
    render(<Settings />);
    await userEvent.click(screen.getByText('Formas de Pagamento'));
    expect(screen.getByText(/adicionar nova forma/i)).toBeInTheDocument();
  });
});
```

---

## 10. PROCEDIMENTO DE DEPLOYMENT

### 10.1 Pré-deployment

```bash
# Criar branch
git checkout -b feature/settings-account-improvements

# Atualizar requirements/package.json se necessário
# Neste caso, não há novas dependências

# Rodar testes
pytest tests/
npm test

# Build frontend
npm run build
```

### 10.2 Database Migration (se houver usuários antigos)

```python
# migrations/versions/XXXX_seed_existing_users.py
def upgrade():
    """Seed categories/payment methods para usuários sem dados"""
    from src.models.user import User
    from src.models.category import Category
    from src.models.payment_method import PaymentMethod
    
    users_without_categories = User.query.outerjoin(Category).filter(
        Category.id == None
    ).all()
    
    for user in users_without_categories:
        _seed_user_defaults(user.id)
```

### 10.3 Deployment

```bash
# Backend
pip install -r requirements.txt
alembic upgrade head
flask --app src.main run

# Frontend
npm install
npm run build
# Servir dist/ via web server
```

---

## 11. PRÓXIMOS PASSOS (Após Aprovação)

1. ✅ Você aprova este plano
2. 🔨 Implementação começa:
   - Criar branch feature/settings-account-improvements
   - Commits pequenos conforme listado na seção 6
   - Testes para cada commit
   - PR review antes de merge para master
3. 📚 Documentação:
   - Atualizar README.md com novos endpoints
   - Adicionar CHANGELOG.md com mudanças
4. 🚀 Deploy:
   - Test em staging
   - Deploy em produção

---

## CHECKLIST DE APROVAÇÃO

- [ ] Plano técnico aprovado pelo usuário
- [ ] Nenhuma mudança fora do escopo proposto
- [ ] Todos os riscos aceitos ou mitigados
- [ ] Testes planejados para cada funcionalidade
- [ ] Schedule de implementação acordado

