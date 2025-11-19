from http import HTTPStatus

def test_register_successfully(client):
    response = client.post('/api/register', json={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'Password123!'
    })
    assert response.status_code == HTTPStatus.OK
    assert response.json['message'] == 'Registration successful, logged in.'
    assert 'access_token_cookie' in response.headers['Set-Cookie']

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
