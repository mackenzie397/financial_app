from http import HTTPStatus

def test_create_payment_method(auth_client):
    client, user = auth_client
    response = client.post('/api/payment-methods', json={'name': 'Credit Card'})
    assert response.status_code == HTTPStatus.CREATED
    assert response.json['name'] == 'Credit Card'

def test_get_payment_methods(auth_client, new_payment_method):
    client, user = auth_client
    response = client.get('/api/payment-methods')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json) == 1
    assert response.json[0]['id'] == new_payment_method.id

def test_get_single_payment_method(auth_client, new_payment_method):
    client, user = auth_client
    response = client.get(f'/api/payment-methods/{new_payment_method.id}')
    assert response.status_code == HTTPStatus.OK
    assert response.json['id'] == new_payment_method.id

def test_update_payment_method(auth_client, new_payment_method):
    client, user = auth_client
    response = client.put(f'/api/payment-methods/{new_payment_method.id}', json={'name': 'New Credit Card'})
    assert response.status_code == HTTPStatus.OK
    assert response.json['name'] == 'New Credit Card'

def test_delete_payment_method(auth_client, new_payment_method):
    client, user = auth_client
    response = client.delete(f'/api/payment-methods/{new_payment_method.id}')
    assert response.status_code == HTTPStatus.OK

    response = client.get(f'/api/payment-methods/{new_payment_method.id}')
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_create_payment_method_unauthenticated(client):
    response = client.post('/api/payment-methods', json={'name': 'Credit Card'})
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_get_payment_methods_unauthenticated(client):
    response = client.get('/api/payment-methods')
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_get_single_payment_method_unauthenticated(client):
    response = client.get('/api/payment-methods/1')
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_update_payment_method_unauthenticated(client):
    response = client.put('/api/payment-methods/1', json={'name': 'New Credit Card'})
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_delete_payment_method_unauthenticated(client):
    response = client.delete('/api/payment-methods/1')
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_get_payment_method_not_found(auth_client):
    client, user = auth_client
    response = client.get('/api/payment-methods/999')
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_update_payment_method_not_found(auth_client):
    client, user = auth_client
    response = client.put('/api/payment-methods/999', json={'name': 'Nonexistent'})
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_delete_payment_method_not_found(auth_client):
    client, user = auth_client
    response = client.delete('/api/payment-methods/999')
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_get_payment_method_other_user(auth_client, client):
    client1, user1 = auth_client
    # User 1 creates a payment method
    post_response = client1.post('/api/payment-methods', json={'name': 'User1PaymentMethod'})
    payment_method_id = post_response.json['id']

    # Register and login User 2
    client.post('/api/register', json={
        'username': 'testuser2',
        'email': 'test2@example.com',
        'password': 'Password123!'
    })
    login_response = client.post('/api/login', json={
        'username': 'testuser2',
        'password': 'Password123!'
    })
    token = login_response.json['access_token']

    # User 2 tries to access User 1's payment method
    response = client.get(f'/api/payment-methods/{payment_method_id}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_update_payment_method_other_user(auth_client, client):
    client1, user1 = auth_client
    # User 1 creates a payment method
    post_response = client1.post('/api/payment-methods', json={'name': 'User1PaymentMethod'})
    payment_method_id = post_response.json['id']

    # Register and login User 2
    client.post('/api/register', json={
        'username': 'testuser2',
        'email': 'test2@example.com',
        'password': 'Password123!'
    })
    login_response = client.post('/api/login', json={
        'username': 'testuser2',
        'password': 'Password123!'
    })
    token = login_response.json['access_token']

    # User 2 tries to update User 1's payment method
    response = client.put(f'/api/payment-methods/{payment_method_id}', json={'name': 'UpdatedPaymentMethod'}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_delete_payment_method_other_user(auth_client, client):
    client1, user1 = auth_client
    # User 1 creates a payment method
    post_response = client1.post('/api/payment-methods', json={'name': 'User1PaymentMethod'})
    payment_method_id = post_response.json['id']

    # Register and login User 2
    client.post('/api/register', json={
        'username': 'testuser2',
        'email': 'test2@example.com',
        'password': 'Password123!'
    })
    login_response = client.post('/api/login', json={
        'username': 'testuser2',
        'password': 'Password123!'
    })
    token = login_response.json['access_token']

    # User 2 tries to delete User 1's payment method
    response = client.delete(f'/api/payment-methods/{payment_method_id}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.NOT_FOUND
