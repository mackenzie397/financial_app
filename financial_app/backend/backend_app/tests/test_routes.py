from http import HTTPStatus

def test_register(client):
    response = client.post('/api/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Password123!'
    })
    assert response.status_code == HTTPStatus.OK
    assert response.json['message'] == 'Registration successful, logged in.'
    assert 'access_token_cookie' in response.headers['Set-Cookie']

def test_login_with_valid_credentials(client):
    client.post('/api/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Password123!'
    })
    response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'Password123!'
    })
    assert response.status_code == HTTPStatus.OK
    assert response.json['message'] == 'Login successful'
    assert 'access_token_cookie' in response.headers['Set-Cookie']

def test_access_protected_route_with_token(auth_client):
    client, user = auth_client
    response = client.get('/api/protected')
    assert response.status_code == HTTPStatus.OK

def test_access_protected_route_without_token(client):
    response = client.get('/api/protected')
    assert response.status_code == HTTPStatus.UNAUTHORIZED
