# 🔧 Admin Dashboard - Clean Database

Dashboard web simples e seguro para gerenciar operações administrativas da aplicação Financial App.

## 📝 Descrição

O Admin Dashboard fornece uma interface visual para executar operações sensíveis no banco de dados, como limpeza completa (drop and recreate de todas as tabelas).

**URL**: `http://seu-dominio/admin/dashboard`

## 🔐 Segurança

O dashboard utiliza **autenticação dupla**:

1. **Login com credenciais de usuário** - Gera um JWT Token
2. **API Key (Secret Key)** - Validação adicional no header `X-API-KEY`

Ambos são **obrigatórios** para executar operações sensíveis.

## 🚀 Como Usar

### 1. Acessar o Dashboard
```
http://seu-dominio/admin/dashboard
```

### 2. Fazer Login
- Insira um **usuário válido** e **senha**
- Clique em "Fazer Login"
- O sistema gerará um JWT Token automaticamente

### 3. Limpar Banco de Dados
- Após login, você verá o formulário de limpeza
- Insira a **Chave de API** (obtida através de variáveis de ambiente)
- Clique em "🗑️ Limpar Banco"
- Confirme na caixa de diálogo de aviso
- Aguarde o processamento

### 4. Fazer Logout
- Clique em "Sair" para encerrar a sessão
- O JWT Token será removido

## 🔑 Variáveis de Ambiente Necessárias

```bash
# Para autenticação (JWT)
JWT_SECRET_KEY=sua_chave_jwt_secreta

# Para operações admin
CLEAN_DB_SECRET_KEY=sua_chave_admin_secreta
```

## ✨ Recursos

- ✅ Interface moderna e responsiva
- ✅ Mensagens de sucesso/erro detalhadas
- ✅ Loading spinner durante processamento
- ✅ Confirmação obrigatória antes de limpar banco
- ✅ Status em tempo real das operações
- ✅ Suporte a dispositivos móveis
- ✅ Autenticação JWT segura
- ✅ API Key adicional para segurança extra

## 📋 Endpoints Utilizados

### Login
```
POST /api/login
Content-Type: application/json

{
  "username": "seu_usuario",
  "password": "sua_senha"
}
```

**Response (200)**:
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Clean Database
```
POST /api/admin/clean-database
Authorization: Bearer {access_token}
X-API-KEY: {secret_key}
Content-Type: application/json
```

**Response (200)**:
```json
{
  "message": "All tables dropped and recreated successfully."
}
```

## ⚠️ Avisos

- **CUIDADO**: A operação de limpeza é irreversível
- Todos os dados do banco serão perdidos
- A operação deve ser executada apenas em ambientes de desenvolvimento
- Certifique-se de ter backup dos dados críticos antes de executar

## 🐛 Troubleshooting

### "Erro de conexão"
- Verifique se a URL do servidor está correta
- Confirme que o servidor está rodando

### "Erro: Invalid credentials"
- Verifique o username e password
- Certifique-se de que o usuário existe no banco

### "Erro: Invalid or missing API key"
- A Chave de API está incorreta
- Verifique a variável `CLEAN_DB_SECRET_KEY` no servidor

### "Sessão expirada"
- Faça login novamente
- O token JWT tem tempo de expiração limitado

## 🔄 Fluxo de Segurança

```
┌─────────────────────────────────────────────────┐
│  1. Usuário acessa /admin/dashboard             │
├─────────────────────────────────────────────────┤
│  2. Insere credenciais (username/password)      │
├─────────────────────────────────────────────────┤
│  3. POST /api/login com credenciais             │
├─────────────────────────────────────────────────┤
│  4. Servidor valida e retorna JWT Token         │
├─────────────────────────────────────────────────┤
│  5. Dashboard armazena token no localStorage    │
├─────────────────────────────────────────────────┤
│  6. Usuário insere Chave de API                 │
├─────────────────────────────────────────────────┤
│  7. POST /admin/clean-database com:             │
│     - Authorization: Bearer {JWT}               │
│     - X-API-KEY: {secret_key}                   │
├─────────────────────────────────────────────────┤
│  8. Servidor valida ambas as credenciais        │
├─────────────────────────────────────────────────┤
│  9. Executa limpeza do banco com sucesso        │
└─────────────────────────────────────────────────┘
```

## 📦 Dependências

- Flask (já incluso)
- Flask-JWT-Extended (já incluso)
- Navegador web moderno (Chrome, Firefox, Safari, Edge)

## 👨‍💻 Desenvolvedor

Desenvolvido como ferramenta interna para administração segura do banco de dados da aplicação Financial App.

---

**Versão**: 1.0  
**Data**: 13 de Novembro de 2025
