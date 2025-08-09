import json

# Helper function to create an investment type for a user
def create_investment_type_for_user(client, name="Stock"):
    response = client.post('/api/investment-types', data=json.dumps({
        'name': name
    }), content_type='application/json')
    return response.get_json()

# --- Investment Type Routes Tests ---

def test_add_investment_type(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN an investment type is posted to the '/api/investment-types' endpoint
    THEN check that a '201' status code is returned and the investment type is created
    """
    response = auth_client.post('/api/investment-types', data=json.dumps({
        'name': 'Stocks'
    }), content_type='application/json')

    assert response.status_code == 201
    assert 'id' in response.get_json()
    assert response.get_json()['name'] == 'Stocks'

def test_get_investment_types(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN the '/api/investment-types' endpoint is requested (GET)
    THEN check that a '200' status code is returned and a list of investment types is returned
    """
    create_investment_type_for_user(auth_client, name='Stocks')
    create_investment_type_for_user(auth_client, name='Bonds')

    response = auth_client.get(f'/api/investment-types')
    assert response.status_code == 200
    assert len(response.get_json()) == 2
    assert response.get_json()[0]['name'] == 'Stocks'
    assert response.get_json()[1]['name'] == 'Bonds'

def test_get_single_investment_type(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN the '/api/investment-types/<id>' endpoint is requested (GET)
    THEN check that a '200' status code is returned and the correct investment type is returned
    """
    investment_type = create_investment_type_for_user(auth_client, name='Single Type')

    response = auth_client.get(f'/api/investment-types/{investment_type["id"]}')
    assert response.status_code == 200
    assert response.get_json()['name'] == 'Single Type'

def test_update_investment_type(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN the '/api/investment-types/<id>' endpoint is requested (PUT)
    THEN check that a '200' status code is returned and the investment type is updated
    """
    investment_type = create_investment_type_for_user(auth_client, name='Old Type')

    response = auth_client.put(f'/api/investment-types/{investment_type["id"]}', data=json.dumps({
        'name': 'Updated Type'
    }), content_type='application/json')

    assert response.status_code == 200
    assert response.get_json()['name'] == 'Updated Type'

def test_delete_investment_type(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN the '/api/investment-types/<id>' endpoint is requested (DELETE)
    THEN check that a '200' status code is returned and the investment type is deleted
    """
    investment_type = create_investment_type_for_user(auth_client, name='Type to Delete')

    response = auth_client.delete(f'/api/investment-types/{investment_type["id"]}')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Investment type deleted'

    # Verify investment type is deleted
    get_response = auth_client.get(f'/api/investment-types/{investment_type["id"]}')
    assert get_response.status_code == 404

def test_add_investment_type_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN an investment type is posted to the '/api/investment-types' endpoint
    THEN check that a '401' status code is returned
    """
    response = client.post('/api/investment-types', data=json.dumps({
        'name': 'Unauthorized Type'
    }), content_type='application/json')
    assert response.status_code == 401

def test_get_investment_types_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN the '/api/investment-types' endpoint is requested (GET)
    THEN check that a '401' status code is returned
    """
    response = client.get('/api/investment-types')
    assert response.status_code == 401

def test_get_single_investment_type_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN the '/api/investment-types/<id>' endpoint is requested (GET)
    THEN check that a '401' status code is returned
    """
    response = client.get('/api/investment-types/1')
    assert response.status_code == 401

def test_update_investment_type_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN the '/api/investment-types/<id>' endpoint is requested (PUT)
    THEN check that a '401' status code is returned
    """
    response = client.put('/api/investment-types/1', data=json.dumps({
        'name': 'Unauthorized Update'
    }), content_type='application/json')
    assert response.status_code == 401

def test_delete_investment_type_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN the '/api/investment-types/<id>' endpoint is requested (DELETE)
    THEN check that a '401' status code is returned
    """
    response = client.delete('/api/investment-types/1')
    assert response.status_code == 401

def test_get_investment_type_not_found(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN a nonexistent investment type is requested
    THEN check that a '404' status code is returned
    """
    response = auth_client.get('/api/investment-types/999')
    assert response.status_code == 404

def test_update_investment_type_not_found(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN a nonexistent investment type is updated
    THEN check that a '404' status code is returned
    """
    response = auth_client.put('/api/investment-types/999', data=json.dumps({
        'name': 'Nonexistent'
    }), content_type='application/json')
    assert response.status_code == 404

def test_delete_investment_type_not_found(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN a nonexistent investment type is deleted
    THEN check that a '404' status code is returned
    """
    response = auth_client.delete('/api/investment-types/999')
    assert response.status_code == 404

def test_get_investment_type_other_user(auth_client, client):
    """
    GIVEN a Flask application and two authenticated users
    WHEN one user tries to access another user's investment type
    THEN check that a '404' status code is returned
    """
    # User 1 creates an investment type
    investment_type = create_investment_type_for_user(auth_client, name='User1 Type')

    # Register and login User 2
    client.post('/api/register', data=json.dumps({
        'username': 'testuser2',
        'email': 'test2@example.com',
        'password': 'Password123!'
    }), content_type='application/json')

    login_response = client.post('/api/login', data=json.dumps({
        'username': 'testuser2',
        'password': 'Password123!'
    }), content_type='application/json')
    token2 = login_response.get_json()['access_token']

    # User 2 tries to access User 1's investment type
    response = client.get(f'/api/investment-types/{investment_type["id"]}', headers={
        'Authorization': f'Bearer {token2}'
    })
    assert response.status_code == 404

def test_update_investment_type_other_user(auth_client, client):
    """
    GIVEN a Flask application and two authenticated users
    WHEN one user tries to update another user's investment type
    THEN check that a '404' status code is returned
    """
    # User 1 creates an investment type
    investment_type = create_investment_type_for_user(auth_client, name='User1 Type')

    # Register and login User 2
    client.post('/api/register', data=json.dumps({
        'username': 'testuser2',
        'email': 'test2@example.com',
        'password': 'Password123!'
    }), content_type='application/json')

    login_response = client.post('/api/login', data=json.dumps({
        'username': 'testuser2',
        'password': 'Password123!'
    }), content_type='application/json')
    token2 = login_response.get_json()['access_token']

    # User 2 tries to update User 1's investment type
    response = client.put(f'/api/investment-types/{investment_type["id"]}', data=json.dumps({
        'name': 'Updated by Other User'
    }), content_type='application/json', headers={
        'Authorization': f'Bearer {token2}'
    })
    assert response.status_code == 404

def test_delete_investment_type_other_user(auth_client, client):
    """
    GIVEN a Flask application and two authenticated users
    WHEN one user tries to delete another user's investment type
    THEN check that a '404' status code is returned
    """
    # User 1 creates an investment type
    investment_type = create_investment_type_for_user(auth_client, name='User1 Type')

    # Register and login User 2
    client.post('/api/register', data=json.dumps({
        'username': 'testuser2',
        'email': 'test2@example.com',
        'password': 'Password123!'
    }), content_type='application/json')

    login_response = client.post('/api/login', data=json.dumps({
        'username': 'testuser2',
        'password': 'Password123!'
    }), content_type='application/json')
    token2 = login_response.get_json()['access_token']

    # User 2 tries to delete User 1's investment type
    response = client.delete(f'/api/investment-types/{investment_type["id"]}', headers={
        'Authorization': f'Bearer {token2}'
    })
    assert response.status_code == 404