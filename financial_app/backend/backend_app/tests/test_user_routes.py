from http import HTTPStatus
from src.models.category import Category
from src.models.payment_method import PaymentMethod
from src.models.investment_type import InvestmentType

def test_register_successfully(client):
    response = client.post('/api/register', json={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'Password123!'
    })
    assert response.status_code == HTTPStatus.CREATED
    assert response.json['message'] == 'User registered successfully'

def test_register_creates_default_seeds(client, app):
    """Verifica que novo usuário recebe categorias, formas de pagamento e tipos de investimento padrão"""
    response = client.post('/api/register', json={
        'username': 'seeduser',
        'email': 'seed@example.com',
        'password': 'Password123!'
    })
    assert response.status_code == HTTPStatus.CREATED
    
    # Login e verifica se há categorias
    client.post('/api/login', json={
        'username': 'seeduser',
        'password': 'Password123!'
    })
    
    categories_response = client.get('/api/categories')
    assert categories_response.status_code == HTTPStatus.OK
    assert len(categories_response.json) > 0  # Verifica se há categorias
    
    payment_methods_response = client.get('/api/payment-methods')
    assert payment_methods_response.status_code == HTTPStatus.OK
    assert len(payment_methods_response.json) > 0  # Verifica se há formas de pagamento
    
    investment_types_response = client.get('/api/investment-types')
    assert investment_types_response.status_code == HTTPStatus.OK
    assert len(investment_types_response.json) > 0  # Verifica se há tipos de investimento

def test_login_successfully(client):
    client.post('/api/register', json={
        'username': 'loginuser',
        'email': 'login@example.com',
        'password': 'Password123!'
    })
    response = client.post('/api/login', json={
        'username': 'loginuser',
        'password': 'Password123!'
    })
    assert response.status_code == HTTPStatus.OK
    assert response.json['message'] == 'Login successful'
    assert 'access_token_cookie' in response.headers['Set-Cookie']

def test_get_current_user_data(auth_client):
    client, user = auth_client
    response = client.get('/api/current_user')
    assert response.status_code == HTTPStatus.OK
    assert response.json['id'] == user.id

def test_change_password_requires_old_password(auth_client):
    """Testa que alterar senha requer a senha antiga correta"""
    client, user = auth_client
    response = client.post('/api/account/change-password', json={
        'old_password': 'WrongPassword123!',
        'new_password': 'NewPassword123!'
    })
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert 'incorrect' in response.json['message'].lower()

def test_change_password_validates_strength(auth_client):
    """Testa que nova senha precisa cumprir requisitos de força"""
    client, user = auth_client
    response = client.post('/api/account/change-password', json={
        'old_password': 'Password123!',
        'new_password': 'weak'
    })
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'password' in response.json['message'].lower()

def test_change_password_cannot_reuse_old(auth_client):
    """Testa que nova senha deve ser diferente da atual"""
    client, user = auth_client
    response = client.post('/api/account/change-password', json={
        'old_password': 'Password123!',
        'new_password': 'Password123!'
    })
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'different' in response.json['message'].lower()

def test_change_password_success(auth_client):
    """Testa mudança de senha bem-sucedida"""
    client, user = auth_client
    response = client.post('/api/account/change-password', json={
        'old_password': 'Password123!',
        'new_password': 'NewPassword123!'
    })
    assert response.status_code == HTTPStatus.OK
    assert response.json['message'] == 'Password changed successfully'
    
    # Verifica que login com nova senha funciona
    login_response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'NewPassword123!'
    })
    assert login_response.status_code == HTTPStatus.OK

def test_change_password_rate_limit(auth_client):
    """Testa rate limiting para alterar senha (5 tentativas por 15 minutos)"""
    client, user = auth_client
    
    # Faz 5 requisições bem-sucedidas/falhadas
    for i in range(5):
        response = client.post('/api/account/change-password', json={
            'old_password': 'WrongPassword123!',
            'new_password': 'NewPassword123!'
        })
        assert response.status_code == HTTPStatus.UNAUTHORIZED
    
    # A 6ª requisição deve retornar 429 (Too Many Requests)
    response = client.post('/api/account/change-password', json={
        'old_password': 'WrongPassword123!',
        'new_password': 'NewPassword123!'
    })
    assert response.status_code == HTTPStatus.TOO_MANY_REQUESTS

