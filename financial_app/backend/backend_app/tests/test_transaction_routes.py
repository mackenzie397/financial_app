from http import HTTPStatus

def test_add_transaction(auth_client, new_category, new_payment_method):
    client, user = auth_client
    response = client.post('/api/transactions', json={
        'description': 'Groceries',
        'amount': 150.0,
        'transaction_type': 'expense',
        'category_id': new_category.id,
        'payment_method_id': new_payment_method.id
    })

    assert response.status_code == HTTPStatus.CREATED
    assert response.json['description'] == 'Groceries'

def test_get_transactions(auth_client, new_transaction):
    client, user = auth_client
    response = client.get(f'/api/transactions')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json) == 1
    assert response.json[0]['id'] == new_transaction.id

def test_get_single_transaction(auth_client, new_transaction):
    client, user = auth_client
    response = client.get(f'/api/transactions/{new_transaction.id}')
    assert response.status_code == HTTPStatus.OK
    assert response.json['id'] == new_transaction.id

def test_update_transaction(auth_client, new_transaction):
    client, user = auth_client
    response = client.put(f'/api/transactions/{new_transaction.id}', json={
        'description': 'Updated Transaction'
    })
    assert response.status_code == HTTPStatus.OK
    assert response.json['description'] == 'Updated Transaction'

def test_delete_transaction(auth_client, new_transaction):
    client, user = auth_client
    response = client.delete(f'/api/transactions/{new_transaction.id}')
    assert response.status_code == HTTPStatus.OK

    response = client.get(f'/api/transactions/{new_transaction.id}')
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_get_transactions_summary(auth_client, new_category, new_payment_method):
    client, user = auth_client
    client.post('/api/transactions', json={'description': 'Income 1', 'amount': 100.0, 'transaction_type': 'income', 'category_id': new_category.id})
    client.post('/api/transactions', json={'description': 'Expense 1', 'amount': 50.0, 'transaction_type': 'expense', 'category_id': new_category.id, 'payment_method_id': new_payment_method.id})
    client.post('/api/transactions', json={'description': 'Income 2', 'amount': 200.0, 'transaction_type': 'income', 'category_id': new_category.id})

    response = client.get(f'/api/transactions/summary')
    assert response.status_code == HTTPStatus.OK
    summary = response.json
    assert summary['total_income'] == 300.0
    assert summary['total_expense'] == 50.0
    assert summary['balance'] == 250.0
    assert summary['transaction_count'] == 3

def test_add_transaction_unauthenticated(client):
    response = client.post('/api/transactions', json={
        'description': 'Unauthorized Trans',
        'amount': 10.0,
        'transaction_type': 'expense',
        'category_id': 1,
        'payment_method_id': 1
    })
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_get_transactions_unauthenticated(client):
    response = client.get('/api/transactions')
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_get_single_transaction_unauthenticated(client):
    response = client.get('/api/transactions/1')
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_update_transaction_unauthenticated(client):
    response = client.put('/api/transactions/1', json={'description': 'Unauthorized Update'})
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_delete_transaction_unauthenticated(client):
    response = client.delete('/api/transactions/1')
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_get_transaction_not_found(auth_client):
    client, user = auth_client
    response = client.get('/api/transactions/999')
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_update_transaction_not_found(auth_client):
    client, user = auth_client
    response = client.put('/api/transactions/999', json={'description': 'Nonexistent'})
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_delete_transaction_not_found(auth_client):
    client, user = auth_client
    response = client.delete('/api/transactions/999')
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_get_transaction_other_user(auth_client, client):
    client1, user1 = auth_client
    # User 1 creates a transaction
    category = client1.post('/api/categories', json={'name': 'User1Category', 'category_type': 'expense'}).json
    payment_method = client1.post('/api/payment-methods', json={'name': 'User1PaymentMethod'}).json
    transaction = client1.post('/api/transactions', json={
        'description': 'User1 Trans',
        'amount': 10.0,
        'transaction_type': 'expense',
        'category_id': category['id'],
        'payment_method_id': payment_method['id']
    }).json

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

    # User 2 tries to access User 1's transaction
    response = client.get(f'/api/transactions/{transaction["id"]}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_update_transaction_other_user(auth_client, client):
    client1, user1 = auth_client
    # User 1 creates a transaction
    category = client1.post('/api/categories', json={'name': 'User1Category', 'category_type': 'expense'}).json
    payment_method = client1.post('/api/payment-methods', json={'name': 'User1PaymentMethod'}).json
    transaction = client1.post('/api/transactions', json={
        'description': 'User1 Trans',
        'amount': 10.0,
        'transaction_type': 'expense',
        'category_id': category['id'],
        'payment_method_id': payment_method['id']
    }).json

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

    # User 2 tries to update User 1's transaction
    response = client.put(f'/api/transactions/{transaction["id"]}', json={'description': 'Updated by Other User'}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_delete_transaction_other_user(auth_client, client):
    client1, user1 = auth_client
    # User 1 creates a transaction
    category = client1.post('/api/categories', json={'name': 'User1Category', 'category_type': 'expense'}).json
    payment_method = client1.post('/api/payment-methods', json={'name': 'User1PaymentMethod'}).json
    transaction = client1.post('/api/transactions', json={
        'description': 'User1 Trans',
        'amount': 10.0,
        'transaction_type': 'expense',
        'category_id': category['id'],
        'payment_method_id': payment_method['id']
    }).json

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

    # User 2 tries to delete User 1's transaction
    response = client.delete(f'/api/transactions/{transaction["id"]}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.NOT_FOUND
