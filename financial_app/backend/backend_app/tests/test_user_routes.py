import json
from src.models.user import User

# Testes para a rota de registro (/register)
def test_register_successfully(client):
    """Testa o registro de um novo usuário com sucesso."""
    response = client.post('/api/register', data=json.dumps({
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'Password123!'
    }), content_type='application/json')
    assert response.status_code == 201
    assert response.get_json()['message'] == 'User registered successfully'

def test_register_duplicate_username(client):
    """Testa o registro com um nome de usuário que já existe."""
    # Primeiro, cria um usuário para garantir que ele exista
    client.post('/api/register', data=json.dumps({
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Password123!'
    }), content_type='application/json')
    
    # Tenta registrar com o mesmo username
    response = client.post('/api/register', data=json.dumps({
        'username': 'testuser',
        'email': 'another@example.com',
        'password': 'Password123!'
    }), content_type='application/json')
    assert response.status_code == 409
    assert response.get_json()['message'] == 'Username already exists'

def test_register_missing_data(client):
    """Testa o registro com dados ausentes."""
    response = client.post('/api/register', data=json.dumps({
        'username': 'someuser'
        # Faltando email e password
    }), content_type='application/json')
    assert response.status_code == 400
    assert 'Missing' in response.get_json()['message']

# Testes para a rota de login (/login)
def test_login_successfully(client):
    """Testa o login com credenciais corretas."""
    # Primeiro, registra o usuário
    client.post('/api/register', data=json.dumps({
        'username': 'loginuser',
        'email': 'login@example.com',
        'password': 'Password123!'
    }), content_type='application/json')

    # Tenta fazer o login
    response = client.post('/api/login', data=json.dumps({
        'username': 'loginuser',
        'password': 'Password123!'
    }), content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert 'user_id' in data

def test_login_invalid_password(client):
    """Testa o login com a senha incorreta."""
    # Registra o usuário
    client.post('/api/register', data=json.dumps({
        'username': 'testpass',
        'email': 'testpass@example.com',
        'password': 'Password123!'
    }), content_type='application/json')

    # Tenta logar com a senha errada
    response = client.post('/api/login', data=json.dumps({
        'username': 'testpass',
        'password': 'wrong_password'
    }), content_type='application/json')
    assert response.status_code == 401
    assert response.get_json()['message'] == 'Invalid credentials'

def test_login_nonexistent_user(client):
    """Testa o login com um usuário que não existe."""
    response = client.post('/api/login', data=json.dumps({
        'username': 'nouser',
        'password': 'Password123!'
    }), content_type='application/json')
    assert response.status_code == 401
    assert response.get_json()['message'] == 'Invalid credentials'

# Testes para a rota /current_user
def test_get_current_user_data(auth_client):
    """Testa se o endpoint /current_user retorna os dados corretos do usuário e não expõe o hash da senha."""
    response = auth_client.get('/api/current_user')
    assert response.status_code == 200
    user_data = response.get_json()
    assert 'id' in user_data
    assert 'username' in user_data
    assert 'email' in user_data
    assert 'password_hash' not in user_data # Garante que o hash da senha não é exposto

def test_get_current_user_invalid_token(client):
    """Testa o acesso ao endpoint /current_user com um token inválido."""
    headers = {'Authorization': 'Bearer invalid_token'}
    response = client.get('/api/current_user', headers=headers)
    assert response.status_code == 422
    assert response.get_json()['msg'] == 'Not enough segments'