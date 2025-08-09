import json
from datetime import date

# Helper function to create a category for a user
def create_category_for_user(client, name="Test Category", category_type="expense"):
    response = client.post('/api/categories', data=json.dumps({
        'name': name,
        'category_type': category_type
    }), content_type='application/json')
    return response.get_json()

# Helper function to create a payment method for a user
def create_payment_method_for_user(client, name="Cash"):
    response = client.post('/api/payment-methods', data=json.dumps({
        'name': name
    }), content_type='application/json')
    return response.get_json()

# Helper function to create a transaction for a user
def create_transaction_for_user(client, description, amount, transaction_type, category_id, payment_method_id, date_str=None):
    data = {
        'description': description,
        'amount': amount,
        'transaction_type': transaction_type,
        'category_id': category_id,
        'payment_method_id': payment_method_id
    }
    if date_str:
        data['date'] = date_str
    response = client.post('/api/transactions', data=json.dumps(data), content_type='application/json')
    return response.get_json()

# --- Transaction Routes Tests ---

def test_add_transaction(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN a transaction is posted to the '/api/transactions' endpoint
    THEN check that a '201' status code is returned and the transaction is created
    """
    category = create_category_for_user(auth_client)
    payment_method = create_payment_method_for_user(auth_client)

    response = auth_client.post('/api/transactions', data=json.dumps({
        'description': 'Groceries',
        'amount': 150.0,
        'date': date.today().isoformat(),
        'transaction_type': 'expense',
        'category_id': category['id'],
        'payment_method_id': payment_method['id']
    }), content_type='application/json')

    assert response.status_code == 201
    assert 'id' in response.get_json()
    assert response.get_json()['description'] == 'Groceries'

def test_add_income_transaction_without_payment_method(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN an income transaction is posted without a payment_method_id
    THEN check that a '201' status code is returned and the transaction is created
    """
    category = create_category_for_user(auth_client, name="Freelance Income", category_type="income")

    response = auth_client.post('/api/transactions', data=json.dumps({
        'description': 'Freelance Payment',
        'amount': 500.0,
        'date': date.today().isoformat(),
        'transaction_type': 'income',
        'category_id': category['id']
    }), content_type='application/json')

    assert response.status_code == 201
    assert 'id' in response.get_json()
    assert response.get_json()['description'] == 'Freelance Payment'
    assert response.get_json()['payment_method_id'] is None

def test_get_transactions(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN the '/api/transactions' endpoint is requested (GET)
    THEN check that a '200' status code is returned and a list of transactions is returned
    """
    category = create_category_for_user(auth_client)
    payment_method = create_payment_method_for_user(auth_client)

    create_transaction_for_user(auth_client, 'Transaction 1', 10.0, 'expense', category['id'], payment_method['id'], date_str='2024-01-01')
    create_transaction_for_user(auth_client, 'Transaction 2', 20.0, 'income', category['id'], None, date_str='2024-01-02') # Pass None for payment_method_id

    response = auth_client.get(f'/api/transactions')
    assert response.status_code == 200
    assert len(response.get_json()) == 2
    assert response.get_json()[0]['description'] == 'Transaction 2' # Ordered by date desc
    assert response.get_json()[1]['description'] == 'Transaction 1'

def test_get_transactions_by_year_and_month(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN the '/api/transactions' endpoint is requested with year and month filters
    THEN check that a '200' status code is returned and filtered transactions are returned
    """
    category = create_category_for_user(auth_client)
    payment_method = create_payment_method_for_user(auth_client)

    create_transaction_for_user(auth_client, 'Jan Trans', 10.0, 'expense', category['id'], payment_method['id'], date_str='2023-01-15')
    create_transaction_for_user(auth_client, 'Feb Trans', 20.0, 'income', category['id'], None, date_str='2023-02-10')
    create_transaction_for_user(auth_client, 'Jan Trans 2', 30.0, 'expense', category['id'], payment_method['id'], date_str='2023-01-20')

    response = auth_client.get(f'/api/transactions?year=2023&month=1')
    assert response.status_code == 200
    assert len(response.get_json()) == 2
    assert response.get_json()[0]['description'] == 'Jan Trans 2' # Ordered by date desc
    assert response.get_json()[1]['description'] == 'Jan Trans'

def test_get_single_transaction(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN the '/api/transactions/<id>' endpoint is requested (GET)
    THEN check that a '200' status code is returned and the correct transaction is returned
    """
    category = create_category_for_user(auth_client)
    payment_method = create_payment_method_for_user(auth_client)
    transaction = create_transaction_for_user(auth_client, 'Single Trans', 100.0, 'expense', category['id'], payment_method['id'])

    response = auth_client.get(f'/api/transactions/{transaction["id"]}')
    assert response.status_code == 200
    assert response.get_json()['description'] == 'Single Trans'

def test_update_transaction(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN the '/api/transactions/<id>' endpoint is requested (PUT)
    THEN check that a '200' status code is returned and the transaction is updated
    """
    category = create_category_for_user(auth_client)
    payment_method = create_payment_method_for_user(auth_client)
    transaction = create_transaction_for_user(auth_client, 'Old Trans', 50.0, 'expense', category['id'], payment_method['id'])

    response = auth_client.put(f'/api/transactions/{transaction["id"]}', data=json.dumps({
        'description': 'Updated Trans',
        'amount': 75.0
    }), content_type='application/json')

    assert response.status_code == 200
    assert response.get_json()['description'] == 'Updated Trans'
    assert response.get_json()['amount'] == 75.0

def test_delete_transaction(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN the '/api/transactions/<id>' endpoint is requested (DELETE)
    THEN check that a '200' status code is returned and the transaction is deleted
    """
    category = create_category_for_user(auth_client)
    payment_method = create_payment_method_for_user(auth_client)
    transaction = create_transaction_for_user(auth_client, 'Trans to Delete', 10.0, 'expense', category['id'], payment_method['id'])

    response = auth_client.delete(f'/api/transactions/{transaction["id"]}')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Transaction deleted'

    # Verify transaction is deleted
    get_response = auth_client.get(f'/api/transactions/{transaction["id"]}')
    assert get_response.status_code == 404

def test_get_transactions_summary(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN the '/api/transactions/summary' endpoint is requested (GET)
    THEN check that a '200' status code is returned and the summary is correct
    """
    category = create_category_for_user(auth_client)
    payment_method = create_payment_method_for_user(auth_client)

    create_transaction_for_user(auth_client, 'Income 1', 100.0, 'income', category['id'], None, date_str='2024-01-01')
    create_transaction_for_user(auth_client, 'Expense 1', 50.0, 'expense', category['id'], payment_method['id'], date_str='2024-01-02')
    create_transaction_for_user(auth_client, 'Income 2', 200.0, 'income', category['id'], None, date_str='2024-01-03')

    response = auth_client.get(f'/api/transactions/summary?year=2024&month=1')
    assert response.status_code == 200
    summary = response.get_json()

    assert summary['total_income'] == 300.0
    assert summary['total_expense'] == 50.0
    assert summary['balance'] == 250.0
    assert summary['transaction_count'] == 3

def test_add_transaction_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN a transaction is posted to the '/api/transactions' endpoint
    THEN check that a '401' status code is returned
    """
    response = client.post('/api/transactions', data=json.dumps({
        'description': 'Unauthorized Trans',
        'amount': 10.0,
        'transaction_type': 'expense',
        'category_id': 1,
        'payment_method_id': 1
    }), content_type='application/json')
    assert response.status_code == 401

def test_get_transactions_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN the '/api/transactions' endpoint is requested (GET)
    THEN check that a '401' status code is returned
    """
    response = client.get('/api/transactions')
    assert response.status_code == 401

def test_get_single_transaction_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN the '/api/transactions/<id>' endpoint is requested (GET)
    THEN check that a '401' status code is returned
    """
    response = client.get('/api/transactions/1')
    assert response.status_code == 401

def test_update_transaction_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN the '/api/transactions/<id>' endpoint is requested (PUT)
    THEN check that a '401' status code is returned
    """
    response = client.put('/api/transactions/1', data=json.dumps({
        'description': 'Unauthorized Update'
    }), content_type='application/json')
    assert response.status_code == 401

def test_delete_transaction_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN the '/api/transactions/<id>' endpoint is requested (DELETE)
    THEN check that a '401' status code is returned
    """
    response = client.delete('/api/transactions/1')
    assert response.status_code == 401

def test_get_transactions_summary_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN the '/api/transactions/summary' endpoint is requested (GET)
    THEN check that a '401' status code is returned
    """
    response = client.get('/api/transactions/summary')
    assert response.status_code == 401

def test_get_transaction_not_found(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN a nonexistent transaction is requested
    THEN check that a '404' status code is returned
    """
    response = auth_client.get('/api/transactions/999')
    assert response.status_code == 404

def test_update_transaction_not_found(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN a nonexistent transaction is updated
    THEN check that a '404' status code is returned
    """
    response = auth_client.put('/api/transactions/999', data=json.dumps({
        'description': 'Nonexistent'
    }), content_type='application/json')
    assert response.status_code == 404

def test_delete_transaction_not_found(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN a nonexistent transaction is deleted
    THEN check that a '404' status code is returned
    """
    response = auth_client.delete('/api/transactions/999')
    assert response.status_code == 404

def test_get_transaction_other_user(auth_client, client):
    """
    GIVEN a Flask application and two authenticated users
    WHEN one user tries to access another user's transaction
    THEN check that a '404' status code is returned
    """
    # User 1 creates a transaction
    category = create_category_for_user(auth_client)
    payment_method = create_payment_method_for_user(auth_client)
    transaction = create_transaction_for_user(auth_client, 'User1 Trans', 10.0, 'expense', category['id'], payment_method['id'])

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

    # User 2 tries to access User 1's transaction
    response = client.get(f'/api/transactions/{transaction["id"]}', headers={
        'Authorization': f'Bearer {token2}'
    })
    assert response.status_code == 404

def test_update_transaction_other_user(auth_client, client):
    """
    GIVEN a Flask application and two authenticated users
    WHEN one user tries to update another user's transaction
    THEN check that a '404' status code is returned
    """
    # User 1 creates a transaction
    category = create_category_for_user(auth_client)
    payment_method = create_payment_method_for_user(auth_client)
    transaction = create_transaction_for_user(auth_client, 'User1 Trans', 10.0, 'expense', category['id'], payment_method['id'])

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

    # User 2 tries to update User 1's transaction
    response = client.put(f'/api/transactions/{transaction["id"]}', data=json.dumps({
        'description': 'Updated by Other User'
    }), content_type='application/json', headers={
        'Authorization': f'Bearer {token2}'
    })
    assert response.status_code == 404

def test_delete_transaction_other_user(auth_client, client):
    """
    GIVEN a Flask application and two authenticated users
    WHEN one user tries to delete another user's transaction
    THEN check that a '404' status code is returned
    """
    # User 1 creates a transaction
    category = create_category_for_user(auth_client)
    payment_method = create_payment_method_for_user(auth_client)
    transaction = create_transaction_for_user(auth_client, 'User1 Trans', 10.0, 'expense', category['id'], payment_method['id'])

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

    # User 2 tries to delete User 1's transaction
    response = client.delete(f'/api/transactions/{transaction["id"]}', headers={
        'Authorization': f'Bearer {token2}'
    })
    assert response.status_code == 404