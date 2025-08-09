import json
from src.models.user import User, db
from io import BytesIO

def test_register(app, client):
    """
    GIVEN a Flask application
    WHEN the '/api/register' page is posted to (POST)
    THEN check that a '201' status code is returned
    """
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Password123!'
    }

    response = client.post('/api/register', json=data)
    response_json = response.json

    assert response.status_code == 201
    assert response_json['message'] == 'User registered successfully'

def test_register_duplicate_username(app, client):
    """
    GIVEN a Flask application
    WHEN the '/api/register' page is posted to with a duplicate username
    THEN check that a '409' status code is returned
    """
    data1 = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Password123!'
    }
    client.post('/api/register', json=data1)

    data2 = {
        'username': 'testuser',
        'email': 'test2@example.com',
        'password': 'Password123!'
    }
    response = client.post('/api/register', json=data2)
    response_json = response.json

    assert response.status_code == 409
    assert response_json['message'] == 'Username already exists'

def test_register_duplicate_email(app, client):
    """
    GIVEN a Flask application
    WHEN the '/api/register' page is posted to with a duplicate email
    THEN check that a '409' status code is returned
    """
    data1 = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Password123!'
    }
    client.post('/api/register', json=data1)

    data2 = {
        'username': 'testuser2',
        'email': 'test@example.com',
        'password': 'Password123!'
    }
    response = client.post('/api/register', json=data2)
    response_json = response.json

    assert response.status_code == 409
    assert response_json['message'] == 'Email already exists'

def test_register_missing_data(app, client):
    """
    GIVEN a Flask application
    WHEN the '/api/register' page is posted to with missing data
    THEN check that a '400' status code is returned
    """
    data = {
        'username': 'testuser',
        'email': 'test@example.com'
    }

    response = client.post('/api/register', json=data)
    response_json = response.json

    assert response.status_code == 400
    assert response_json['message'] == 'Missing username, email or password'

def test_login_with_valid_credentials(app, client):
    """
    GIVEN a Flask application and a registered user
    WHEN the '/api/login' page is posted to with valid credentials
    THEN check that a '200' status code and an access token are returned
    """
    register_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Password123!'
    }
    client.post('/api/register', json=register_data)

    login_data = {
        'username': 'testuser',
        'password': 'Password123!'
    }
    response = client.post('/api/login', json=login_data)
    response_json = response.json

    assert response.status_code == 200
    assert response_json['access_token'] is not None

def test_login_with_invalid_password(app, client):
    """
    GIVEN a Flask application and a registered user
    WHEN the '/api/login' page is posted to with an invalid password
    THEN check that a '401' status code is returned
    """
    register_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Password123!'
    }
    client.post('/api/register', json=register_data)

    login_data = {
        'username': 'testuser',
        'password': 'wrongpassword'
    }
    response = client.post('/api/login', json=login_data)
    response_json = response.json

    assert response.status_code == 401
    assert response_json['message'] == 'Invalid credentials'

def test_login_with_nonexistent_user(app, client):
    """
    GIVEN a Flask application
    WHEN the '/api/login' page is posted to with a nonexistent user
    THEN check that a '401' status code is returned
    """
    data = {
        'username': 'nonexistentuser',
        'password': 'Password123!'
    }

    response = client.post('/api/login', json=data)
    response_json = response.json

    assert response.status_code == 401
    assert response_json['message'] == 'Invalid credentials'

def test_access_protected_route_with_token(app, client):
    """
    GIVEN a Flask application and a logged-in user
    WHEN the '/api/protected' page is requested with a valid token
    THEN check that a '200' status code is returned
    """
    register_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Password123!'
    }
    client.post('/api/register', json=register_data)

    login_data = {
        'username': 'testuser',
        'password': 'Password123!'
    }
    login_response = client.post('/api/login', json=login_data)
    token = login_response.json['access_token']

    protected_response = client.get('/api/protected', headers={'Authorization': f'Bearer {token}'})
    protected_json = protected_response.json

    assert protected_response.status_code == 200
    assert protected_json['message'] == 'Protected data'

def test_access_protected_route_without_token(client):
    """
    GIVEN a Flask application
    WHEN the '/api/protected' page is requested without a token
    THEN check that a '401' status code is returned
    """
    response = client.get('/api/protected')
    assert response.status_code == 401