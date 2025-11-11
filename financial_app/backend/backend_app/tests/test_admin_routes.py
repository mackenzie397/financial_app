import os
from http import HTTPStatus
from src.models.user import db, User

def test_clean_database_unauthorized(client):
    """
    Tests that the clean-database endpoint returns 401 without a valid API key.
    """
    # Test without API key
    response = client.post('/api/admin/clean-database')
    assert response.status_code == HTTPStatus.UNAUTHORIZED

    # Test with invalid API key
    response = client.post(
        '/api/admin/clean-database',
        headers={'X-API-KEY': 'invalid-key'}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_clean_database_authorized(auth_client):
    """
    Tests that the clean-database endpoint works with a valid API key and user authentication.
    """
    client, _ = auth_client
    # auth_client fixture already creates a user. Let's ensure it exists.
    assert User.query.count() >= 1

    # 2. Set the secret key in the environment for the test
    secret_key = 'test-secret-key'
    os.environ['CLEAN_DB_SECRET_KEY'] = secret_key

    # 3. Call the endpoint with the correct key (auth_client provides JWT)
    response = client.post(
        '/api/admin/clean-database',
        headers={'X-API-KEY': secret_key}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json['message'] == 'All tables dropped and recreated successfully.'

    # 4. Verify the database is empty
    assert User.query.count() == 0

    # Clean up the environment variable
    del os.environ['CLEAN_DB_SECRET_KEY']

def test_swagger_ui_unauthorized(client):
    """
    Tests that the Swagger UI is inaccessible without a valid API key.
    """
    # Set a dummy key to ensure the protection is active
    os.environ['SWAGGER_UI_API_KEY'] = 'a-real-key-must-be-set'

    response = client.get('/apidocs/')
    assert response.status_code == HTTPStatus.UNAUTHORIZED

    del os.environ['SWAGGER_UI_API_KEY']

def test_swagger_ui_authorized(client):
    """
    Tests that the Swagger UI is accessible with a valid API key.
    """
    secret_key = 'swagger-test-key'
    os.environ['SWAGGER_UI_API_KEY'] = secret_key

    response = client.get(f'/apidocs/?apiKey={secret_key}')
    assert response.status_code == HTTPStatus.OK
    # Decode response data and check for the title text
    response_text = response.data.decode('utf-8')
    assert '<title>Financial App API</title>' in response_text

    del os.environ['SWAGGER_UI_API_KEY']
