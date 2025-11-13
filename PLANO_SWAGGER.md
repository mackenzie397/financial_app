# 🔐 PLANO TÉCNICO: API SWAGGER COMPLETA E SEGURA

**Data**: 12 de Novembro de 2025  
**Versão**: 1.0  
**Objetivo**: Documentar completamente a API Swagger com autenticação robusta, tornando-a uma API privada e segura.

---

## 📋 RESUMO EXECUTIVO

A aplicação Financial App possui uma API REST robusta com múltiplos endpoints. O objetivo é:

1. **Documentar completamente** todos os endpoints na Swagger UI (OpenAPI 3.0)
2. **Implementar autenticação dupla** na Swagger UI:
   - Login obrigatório (username/password)
   - API Keys (X-API-KEY header e SWAGGER_UI_API_KEY)
3. **Garantir segurança**: Apenas usuário autorizado consegue acessar a API
4. **Facilitar uso**: Swagger UI como interface completa para testar endpoints

---

## 🔍 ANÁLISE DA ESTRUTURA ATUAL

### Endpoints Identificados (33 total)

#### **1. AUTENTICAÇÃO (7 endpoints)**
- `POST /api/register` - Registro de novo usuário
- `POST /api/login` - Login com JWT
- `POST /api/logout` - Logout (limpar cookies)
- `GET /api/protected` - Rota protegida (teste)
- `GET /api/current_user` - Obter usuário atual
- `POST /api/account/change-password` - Trocar senha (rate limited 5/15min)
- `PUT /api/account/update-profile` - Atualizar email/username

#### **2. CATEGORIAS (5 endpoints)**
- `POST /api/categories` - Criar categoria
- `GET /api/categories` - Listar categorias (com filtro por tipo)
- `GET /api/categories/<id>` - Obter categoria específica
- `PUT /api/categories/<id>` - Atualizar categoria
- `DELETE /api/categories/<id>` - Deletar categoria

#### **3. FORMAS DE PAGAMENTO (5 endpoints)**
- `POST /api/payment-methods` - Criar forma de pagamento
- `GET /api/payment-methods` - Listar formas de pagamento
- `GET /api/payment-methods/<id>` - Obter forma de pagamento
- `PUT /api/payment-methods/<id>` - Atualizar forma de pagamento
- `DELETE /api/payment-methods/<id>` - Deletar forma de pagamento

#### **4. TIPOS DE INVESTIMENTO (5 endpoints)**
- `POST /api/investment-types` - Criar tipo de investimento
- `GET /api/investment-types` - Listar tipos de investimento
- `GET /api/investment-types/<id>` - Obter tipo de investimento
- `PUT /api/investment-types/<id>` - Atualizar tipo de investimento
- `DELETE /api/investment-types/<id>` - Deletar tipo de investimento

#### **5. TRANSAÇÕES (6 endpoints)**
- `POST /api/transactions` - Criar transação
- `GET /api/transactions` - Listar transações (com filtros)
- `GET /api/transactions/<id>` - Obter transação específica
- `PUT /api/transactions/<id>` - Atualizar transação
- `DELETE /api/transactions/<id>` - Deletar transação
- `GET /api/transactions/summary` - Resumo de transações

#### **6. METAS/GOALS (6 endpoints)**
- `POST /api/goals` - Criar meta
- `GET /api/goals` - Listar metas (com filtro por status)
- `GET /api/goals/<id>` - Obter meta específica
- `PUT /api/goals/<id>` - Atualizar meta
- `DELETE /api/goals/<id>` - Deletar meta
- `PUT /api/goals/<id>/progress` - Atualizar progresso da meta

#### **7. INVESTIMENTOS (6 endpoints)**
- `POST /api/investments` - Criar investimento
- `GET /api/investments` - Listar investimentos (com filtros)
- `GET /api/investments/<id>` - Obter investimento específico
- `PUT /api/investments/<id>` - Atualizar investimento
- `DELETE /api/investments/<id>` - Deletar investimento
- `GET /api/investments/summary` - Resumo de investimentos

#### **8. ADMIN (1 endpoint)**
- `POST /api/admin/clean-database` - Limpar banco de dados (requer API Key + JWT)

#### **9. SAÚDE (1 endpoint)**
- `GET /api/health` - Health check (sem autenticação)

---

## 🔐 ESTRATÉGIA DE AUTENTICAÇÃO

### Cenário Atual
```
┌─────────────────────────────────────────┐
│        Swagger UI (sem login)           │
│     [Tentar executar clean-database]    │
│                   ↓                      │
│   Endpoint valida API Key no header     │
│   Erro: API Key não fornecida visível   │
└─────────────────────────────────────────┘
```

### Cenário Desejado
```
┌──────────────────────────────────────────┐
│   Swagger UI com Login Obrigatório       │
│   ┌────────────────────────────────────┐ │
│   │ Username: ________________         │ │
│   │ Password: ________________         │ │
│   │ [Login]                            │ │
│   └────────────────────────────────────┘ │
│                   ↓                       │
│   Login POST /swagger/login (novo)       │
│   Valida credenciais (novo usuário)     │
│                   ↓                       │
│   Retorna JWT Token + API Keys           │
│                   ↓                       │
│   Swagger UI armazena tokens             │
│                   ↓                       │
│   Executar endpoints com autenticação    │
│   Headers: Authorization: Bearer {JWT}  │
│            X-API-KEY: {chave}            │
│                   ↓                       │
│   Endpoints validam e executam com êxito │
└──────────────────────────────────────────┘
```

---

## 📝 COMPONENTES A IMPLEMENTAR

### 1. **Novo Endpoint de Login para Swagger** ✅
**Arquivo**: `src/routes/swagger_auth.py` (novo)

**Endpoint**:
```
POST /api/swagger/login
Content-Type: application/json

{
  "username": "swagger_user",
  "password": "swagger_password"
}

Response (200):
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "api_key_admin": "valor_de_CLEAN_DB_SECRET_KEY",
  "api_key_swagger": "valor_de_SWAGGER_UI_API_KEY"
}
```

**Detalhes**:
- Cria novo usuário especial para acesso Swagger (se não existir)
- Valida credenciais contra usuario/password no .env
- Retorna JWT + API Keys
- Rate limited (10/min)
- Sem dependência de usuário autenticado

### 2. **Atualizar swagger_template.yml** ✅
**Arquivo**: `src/swagger_template.yml`

**Mudanças**:
- Adicionar todos os 33 endpoints documentados
- Exemplo de requisição/resposta para cada
- Descrições completas
- Agrupamento por tags (Authentication, Category, Transaction, etc.)
- Esquemas de erro padronizados
- Autenticação via Bearer Token + API Key configurável

### 3. **Atualizar main.py - Swagger Initialization** ✅
**Arquivo**: `src/main.py`

**Mudanças**:
- Remover proteção por API Key no `/apidocs` (permite acesso à interface)
- Manter proteção no `/apidocs` APENAS se necessário
- Registrar novo blueprint `swagger_auth_bp`
- Permitir login via `/swagger/login`

### 4. **Atualizar admin.py - Clean Database** ✅
**Arquivo**: `src/routes/admin.py`

**Mudanças**:
- Adicionar campo visível no Swagger para API Key
- Documentação melhorada
- Exemplos de uso

### 5. **Atualizar config.py** ✅
**Arquivo**: `src/config.py`

**Mudanças**:
- Adicionar variáveis para credenciais Swagger
- `SWAGGER_LOGIN_USERNAME`
- `SWAGGER_LOGIN_PASSWORD`

---

## 📊 ESTRUTURA DO SWAGGER TEMPLATE

```yaml
openapi: 3.0.0
info:
  title: Financial App API
  description: API completa para gerenciar finanças pessoais
  version: 1.0.0
  
servers:
  - url: /api
    description: API Root

security:
  - bearerAuth: []
  - apiKeyAuth: []

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
    apiKeyAuth:
      type: apiKey
      in: header
      name: X-API-KEY

paths:
  /swagger/login:
    post:
      tags: [Swagger Auth]
      summary: Login para Swagger UI
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                username: { type: string }
                password: { type: string }
      responses:
        200:
          description: Login bem-sucedido
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token: { type: string }
                  api_key_admin: { type: string }
                  api_key_swagger: { type: string }

  /register:
    post:
      tags: [Authentication]
      summary: Registrar novo usuário
      # ... mais detalhes

  /categories:
    post:
      tags: [Category]
      summary: Criar categoria
      # ... mais detalhes
    get:
      tags: [Category]
      summary: Listar categorias
      # ... mais detalhes

  # ... mais endpoints
```

---

## 🛠️ PLANO DE EXECUÇÃO (6 COMMITS)

### **COMMIT 1: Criar novo endpoint de autenticação Swagger**
- Arquivo: `src/routes/swagger_auth.py` (novo)
- Função: `swagger_login()` - POST `/swagger/login`
- Valida credentials do .env
- Retorna JWT + API Keys
- Tests: `test_swagger_login.py` (novo)

### **COMMIT 2: Atualizar configuração**
- Arquivo: `src/config.py`
- Adicionar `SWAGGER_LOGIN_USERNAME` e `SWAGGER_LOGIN_PASSWORD`
- Usar variáveis de ambiente

### **COMMIT 3: Documentar endpoint Authentication (7 endpoints)**
- Arquivo: `src/swagger_template.yml`
- Documentar: register, login, logout, protected, current_user, change-password, update-profile
- Adicionar exemplos de requisição/resposta
- Adicionar schemas de erro

### **COMMIT 4: Documentar endpoints de CRUD (22 endpoints)**
- Arquivo: `src/swagger_template.yml`
- Documentar: Categories, PaymentMethods, InvestmentTypes, Transactions, Goals, Investments
- Adicionar filtros, paginação
- Adicionar exemplos

### **COMMIT 5: Documentar endpoints especiais**
- Arquivo: `src/swagger_template.yml`
- Documentar: /transactions/summary, /investments/summary
- Documentar: /admin/clean-database com campo de API Key visível
- Documentar: /health

### **COMMIT 6: Atualizar main.py e adicionar testes**
- Arquivo: `src/main.py`
- Registrar novo blueprint
- Remover proteção obsoleta do `/apidocs` se necessário
- Testes de integração

---

## 🔒 SEGURANÇA

### Fluxo de Autenticação
1. Usuário acessa `/apidocs` (Swagger UI disponível publicamente)
2. Clica em "Authorize" ou um botão customizado
3. Insere username/password
4. Sistema valida contra `SWAGGER_LOGIN_USERNAME` e `SWAGGER_LOGIN_PASSWORD`
5. Retorna JWT Token
6. Swagger UI armazena token automaticamente
7. Todos os requests incluem `Authorization: Bearer {token}`
8. Endpoints protegidos validam JWT

### API Keys
- `SWAGGER_UI_API_KEY`: Para endpoint `/swagger/login` (opcional, pode ser removido)
- `CLEAN_DB_SECRET_KEY`: Para endpoint `/admin/clean-database` (obrigatório)

### Rate Limiting
- `/swagger/login`: 10 requests/minuto
- `/account/change-password`: 5 requests/15 minutos
- Outros endpoints: sem limite (usuário autenticado)

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

### Análise & Planejamento
- [x] Identificar todos os endpoints (33 total)
- [x] Entender estrutura de autenticação atual
- [x] Definir estratégia de segurança
- [x] Criar plano detalhado

### Desenvolvimento
- [ ] Commit 1: swagger_auth.py (novo endpoint)
- [ ] Commit 2: config.py (atualizar variáveis)
- [ ] Commit 3: swagger_template.yml (Authentication)
- [ ] Commit 4: swagger_template.yml (CRUD endpoints)
- [ ] Commit 5: swagger_template.yml (endpoints especiais)
- [ ] Commit 6: main.py + testes

### Testes
- [ ] Testar login via Swagger
- [ ] Testar endpoints com JWT + API Key
- [ ] Testar rate limiting
- [ ] Testar segurança (tentativas não autorizadas)
- [ ] Testar documentação completa no Swagger UI

### Deployment
- [ ] Configurar variáveis de ambiente em produção
- [ ] Testar em instância gratuita
- [ ] Documentação para outros devs

---

## 📝 NOTAS IMPORTANTES

1. **Credenciais Swagger**: As credenciais para acessar Swagger UI devem ser diferentes das credenciais de usuário normal da aplicação. Usar um usuário especial ou configurar via .env.

2. **API Keys**: Manter ambas as chaves (`SWAGGER_UI_API_KEY` e `CLEAN_DB_SECRET_KEY`) no .env. Em produção, configurar direto no servidor.

3. **Swagger UI público**: A interface Swagger UI não precisa de proteção, apenas o login. Uma vez autenticado, todos os endpoints são acessíveis.

4. **Documentação**: Usar docstrings dos endpoints existentes para popular o YAML automaticamente ou atualizar manualmente para melhorar descrições.

5. **Versioning**: Manter versão 1.0.0 da API. Se houver breaking changes, incrementar para 1.1.0 ou 2.0.0.

---

## 🎯 RESULTADO ESPERADO

Após implementação:

```
✅ Swagger UI completa (33 endpoints documentados)
✅ Login obrigatório para usar a API
✅ API Keys configuráveis
✅ Exemplos de requisição/resposta
✅ Erros padronizados
✅ Segurança robusta
✅ Fácil de usar (mesmo para pessoas não-técnicas)
✅ Pronto para produção
```

---

**Próximo passo**: Você aprova este plano? Se sim, começamos com COMMIT 1! 🚀
