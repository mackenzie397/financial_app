import json

def test_create_payment_method(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN a payment method is posted to the '/api/payment-methods' endpoint
    THEN check that a '201' status code is returned and the payment method is created
    """
    response = auth_client.post('/api/payment-methods', data=json.dumps({
        'name': 'Credit Card'
    }), content_type='application/json')

    assert response.status_code == 201
    assert 'id' in response.get_json()
    assert response.get_json()['name'] == 'Credit Card'

def test_get_payment_methods(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN the '/api/payment-methods' endpoint is requested (GET)
    THEN check that a '200' status code is returned and a list of payment methods is returned
    """
    auth_client.post('/api/payment-methods', data=json.dumps({
        'name': 'Credit Card'
    }), content_type='application/json')
    auth_client.post('/api/payment-methods', data=json.dumps({
        'name': 'Debit Card'
    }), content_type='application/json')

    response = auth_client.get('/api/payment-methods')
    assert response.status_code == 200
    assert len(response.get_json()) == 2

def test_get_single_payment_method(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN the '/api/payment-methods/<id>' endpoint is requested (GET)
    THEN check that a '200' status code is returned and the correct payment method is returned
    """
    post_response = auth_client.post('/api/payment-methods', data=json.dumps({
        'name': 'Credit Card'
    }), content_type='application/json')
    payment_method_id = post_response.get_json()['id']

    response = auth_client.get(f'/api/payment-methods/{payment_method_id}')
    assert response.status_code == 200
    assert response.get_json()['name'] == 'Credit Card'

def test_update_payment_method(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN the '/api/payment-methods/<id>' endpoint is requested (PUT)
    THEN check that a '200' status code is returned and the payment method is updated
    """
    post_response = auth_client.post('/api/payment-methods', data=json.dumps({
        'name': 'Credit Card'
    }), content_type='application/json')
    payment_method_id = post_response.get_json()['id']

    response = auth_client.put(f'/api/payment-methods/{payment_method_id}', data=json.dumps({
        'name': 'New Credit Card'
    }), content_type='application/json')

    assert response.status_code == 200
    assert response.get_json()['name'] == 'New Credit Card'

def test_delete_payment_method(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN the '/api/payment-methods/<id>' endpoint is requested (DELETE)
    THEN check that a '200' status code is returned and the payment method is deleted
    """
    post_response = auth_client.post('/api/payment-methods', data=json.dumps({
        'name': 'Credit Card'
    }), content_type='application/json')
    payment_method_id = post_response.get_json()['id']

    response = auth_client.delete(f'/api/payment-methods/{payment_method_id}')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Payment method deleted'

    # Verify payment method is deleted
    get_response = auth_client.get(f'/api/payment-methods/{payment_method_id}')
    assert get_response.status_code == 404

def test_create_payment_method_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN a payment method is posted to the '/api/payment-methods' endpoint
    THEN check that a '401' status code is returned
    """
    response = client.post('/api/payment-methods', data=json.dumps({
        'name': 'Credit Card'
    }), content_type='application/json')

    assert response.status_code == 401

def test_get_payment_methods_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN the '/api/payment-methods' endpoint is requested (GET)
    THEN check that a '401' status code is returned
    """
    response = client.get('/api/payment-methods')
    assert response.status_code == 401

def test_get_single_payment_method_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN the '/api/payment-methods/<id>' endpoint is requested (GET)
    THEN check that a '401' status code is returned
    """
    response = client.get('/api/payment-methods/1')
    assert response.status_code == 401

def test_update_payment_method_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN the '/api/payment-methods/<id>' endpoint is requested (PUT)
    THEN check that a '401' status code is returned
    """
    response = client.put('/api/payment-methods/1', data=json.dumps({
        'name': 'New Credit Card'
    }), content_type='application/json')

    assert response.status_code == 401

def test_delete_payment_method_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN the '/api/payment-methods/<id>' endpoint is requested (DELETE)
    THEN check that a '401' status code is returned
    """
    response = client.delete('/api/payment-methods/1')
    assert response.status_code == 401

def test_get_payment_method_not_found(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN a nonexistent payment method is requested
    THEN check that a '404' status code is returned
    """
    response = auth_client.get('/api/payment-methods/999')
    assert response.status_code == 404

def test_update_payment_method_not_found(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN a nonexistent payment method is updated
    THEN check that a '404' status code is returned
    """
    response = auth_client.put('/api/payment-methods/999', data=json.dumps({
        'name': 'Nonexistent'
    }), content_type='application/json')
    assert response.status_code == 404

def test_delete_payment_method_not_found(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN a nonexistent payment method is deleted
    THEN check that a '404' status code is returned
    """
    response = auth_client.delete('/api/payment-methods/999')
    assert response.status_code == 404

def test_get_payment_method_other_user(auth_client, client):
    """
    GIVEN a Flask application and two authenticated users
    WHEN one user tries to access another user's payment method
    THEN check that a '404' status code is returned
    """
    # User 1 creates a payment method
    post_response = auth_client.post('/api/payment-methods', data=json.dumps({
        'name': 'User1PaymentMethod'
    }), content_type='application/json')
    payment_method_id = post_response.get_json()['id']

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

    # User 2 tries to access User 1's payment method
    response = client.get(f'/api/payment-methods/{payment_method_id}', headers={
        'Authorization': f'Bearer {token2}'
    })
    assert response.status_code == 404

def test_update_payment_method_other_user(auth_client, client):
    """
    GIVEN a Flask application and two authenticated users
    WHEN one user tries to update another user's payment method
    THEN check that a '404' status code is returned
    """
    # User 1 creates a payment method
    post_response = auth_client.post('/api/payment-methods', data=json.dumps({
        'name': 'User1PaymentMethod'
    }), content_type='application/json')
    payment_method_id = post_response.get_json()['id']

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

    # User 2 tries to update User 1's payment method
    response = client.put(f'/api/payment-methods/{payment_method_id}', data=json.dumps({
        'name': 'UpdatedPaymentMethod'
    }), content_type='application/json', headers={
        'Authorization': f'Bearer {token2}'
    })
    assert response.status_code == 404

def test_delete_payment_method_other_user(auth_client, client):
    """
    GIVEN a Flask application and two authenticated users
    WHEN one user tries to delete another user's payment method
    THEN check that a '404' status code is returned
    """
    # User 1 creates a payment method
    post_response = auth_client.post('/api/payment-methods', data=json.dumps({
        'name': 'User1PaymentMethod'
    }), content_type='application/json')
    payment_method_id = post_response.get_json()['id']

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

    # User 2 tries to delete User 1's payment method
    response = client.delete(f'/api/payment-methods/{payment_method_id}', headers={
        'Authorization': f'Bearer {token2}'
    })
    assert response.status_code == 404