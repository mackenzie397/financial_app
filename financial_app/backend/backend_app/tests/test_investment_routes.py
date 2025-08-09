import json
from datetime import date

# Helper function to create an investment type for a user
def create_investment_type_for_user(client, name="Stock"):
    response = client.post('/api/investment-types', data=json.dumps({
        'name': name
    }), content_type='application/json')
    return response.get_json()

# Helper function to create an investment for a user
def create_investment_for_user(client, investment_type_id, name="My Investment", amount=100.0, current_value=100.0, purchase_date=None):
    data = {
        'name': name,
        'amount': amount,
        'current_value': current_value,
        'investment_type_id': investment_type_id
    }
    if purchase_date:
        data['purchase_date'] = purchase_date.isoformat()
    response = client.post('/api/investments', data=json.dumps(data), content_type='application/json')
    return response.get_json()

# --- Investment Routes Tests ---

def test_add_investment(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN an investment is posted to the '/api/investments' endpoint
    THEN check that a '201' status code is returned and the investment is created
    """
    investment_type = create_investment_type_for_user(auth_client)

    response = auth_client.post('/api/investments', data=json.dumps({
        'name': 'Tech Stock',
        'amount': 1000.0,
        'current_value': 1050.0,
        'purchase_date': date.today().isoformat(),
        'investment_type_id': investment_type['id']
    }), content_type='application/json')

    assert response.status_code == 201
    assert 'id' in response.get_json()
    assert response.get_json()['name'] == 'Tech Stock'

def test_get_investments(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN the '/api/investments' endpoint is requested (GET)
    THEN check that a '200' status code is returned and a list of investments is returned
    """
    investment_type = create_investment_type_for_user(auth_client)
    create_investment_for_user(auth_client, investment_type['id'], name='Investment 1')
    create_investment_for_user(auth_client, investment_type['id'], name='Investment 2')

    response = auth_client.get(f'/api/investments')
    assert response.status_code == 200
    investments = response.get_json()
    assert len(investments) == 2
    assert any(i['name'] == 'Investment 1' for i in investments)
    assert any(i['name'] == 'Investment 2' for i in investments)
    # Verify order if created_date is distinct
    if investments[0]['name'] == 'Investment 2':
        assert investments[1]['name'] == 'Investment 1'
    elif investments[0]['name'] == 'Investment 1':
        assert investments[1]['name'] == 'Investment 2'

def test_get_single_investment(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN the '/api/investments/<id>' endpoint is requested (GET)
    THEN check that a '200' status code is returned and the correct investment is returned
    """
    investment_type = create_investment_type_for_user(auth_client)
    investment = create_investment_for_user(auth_client, investment_type['id'], name='Single Investment')

    response = auth_client.get(f'/api/investments/{investment["id"]}')
    assert response.status_code == 200
    assert response.get_json()['name'] == 'Single Investment'

def test_update_investment(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN the '/api/investments/<id>' endpoint is requested (PUT)
    THEN check that a '200' status code is returned and the investment is updated
    """
    investment_type = create_investment_type_for_user(auth_client)
    investment = create_investment_for_user(auth_client, investment_type['id'], name='Old Investment')

    response = auth_client.put(f'/api/investments/{investment["id"]}', data=json.dumps({
        'name': 'Updated Investment',
        'current_value': 1200.0
    }), content_type='application/json')

    assert response.status_code == 200
    assert response.get_json()['name'] == 'Updated Investment'
    assert response.get_json()['current_value'] == 1200.0

def test_delete_investment(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN the '/api/investments/<id>' endpoint is requested (DELETE)
    THEN check that a '200' status code is returned and the investment is deleted
    """
    investment_type = create_investment_type_for_user(auth_client)
    investment = create_investment_for_user(auth_client, investment_type['id'], name='Investment to Delete')

    response = auth_client.delete(f'/api/investments/{investment["id"]}')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Investment deleted'

    # Verify investment is deleted
    get_response = auth_client.get(f'/api/investments/{investment["id"]}')
    assert get_response.status_code == 404

def test_add_investment_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN an investment is posted to the '/api/investments' endpoint
    THEN check that a '401' status code is returned
    """
    response = client.post('/api/investments', data=json.dumps({
        'name': 'Unauthorized Investment',
        'amount': 100.0,
        'investment_type_id': 1
    }), content_type='application/json')
    assert response.status_code == 401

def test_get_investments_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN the '/api/investments' endpoint is requested (GET)
    THEN check that a '401' status code is returned
    """
    response = client.get('/api/investments')
    assert response.status_code == 401

def test_get_single_investment_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN the '/api/investments/<id>' endpoint is requested (GET)
    THEN check that a '401' status code is returned
    """
    response = client.get('/api/investments/1')
    assert response.status_code == 401

def test_update_investment_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN the '/api/investments/<id>' endpoint is requested (PUT)
    THEN check that a '401' status code is returned
    """
    response = client.put('/api/investments/1', data=json.dumps({
        'name': 'Unauthorized Update'
    }), content_type='application/json')
    assert response.status_code == 401

def test_delete_investment_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN the '/api/investments/<id>' endpoint is requested (DELETE)
    THEN check that a '401' status code is returned
    """
    response = client.delete('/api/investments/1')
    assert response.status_code == 401

def test_get_investment_not_found(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN a nonexistent investment is requested
    THEN check that a '404' status code is returned
    """
    response = auth_client.get('/api/investments/999')
    assert response.status_code == 404

def test_update_investment_not_found(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN a nonexistent investment is updated
    THEN check that a '404' status code is returned
    """
    response = auth_client.put('/api/investments/999', data=json.dumps({
        'name': 'Nonexistent'
    }), content_type='application/json')
    assert response.status_code == 404

def test_delete_investment_not_found(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN a nonexistent investment is deleted
    THEN check that a '404' status code is returned
    """
    response = auth_client.delete('/api/investments/999')
    assert response.status_code == 404

def test_get_investment_other_user(auth_client, client):
    """
    GIVEN a Flask application and two authenticated users
    WHEN one user tries to access another user's investment
    THEN check that a '404' status code is returned
    """
    # User 1 creates an investment
    investment_type = create_investment_type_for_user(auth_client)
    investment = create_investment_for_user(auth_client, investment_type['id'], name='User1 Investment')

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

    # User 2 tries to access User 1's investment
    response = client.get(f'/api/investments/{investment["id"]}', headers={
        'Authorization': f'Bearer {token2}'
    })
    assert response.status_code == 404

def test_update_investment_other_user(auth_client, client):
    """
    GIVEN a Flask application and two authenticated users
    WHEN one user tries to update another user's investment
    THEN check that a '404' status code is returned
    """
    # User 1 creates an investment
    investment_type = create_investment_type_for_user(auth_client)
    investment = create_investment_for_user(auth_client, investment_type['id'], name='User1 Investment')

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

    # User 2 tries to update User 1's investment
    response = client.put(f'/api/investments/{investment["id"]}', data=json.dumps({
        'name': 'Updated by Other User'
    }), content_type='application/json', headers={
        'Authorization': f'Bearer {token2}'
    })
    assert response.status_code == 404

def test_delete_investment_other_user(auth_client, client):
    """
    GIVEN a Flask application and two authenticated users
    WHEN one user tries to delete another user's investment
    THEN check that a '404' status code is returned
    """
    # User 1 creates an investment
    investment_type = create_investment_type_for_user(auth_client)
    investment = create_investment_for_user(auth_client, investment_type['id'], name='User1 Investment')

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

    # User 2 tries to delete User 1's investment
    response = client.delete(f'/api/investments/{investment["id"]}', headers={
        'Authorization': f'Bearer {token2}'
    })
    assert response.status_code == 404

def test_contribute_to_investment(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN a contribution is posted to the '/api/investments/<id>/contribute' endpoint
    THEN check that the current_amount is updated
    """
    investment_type = create_investment_type_for_user(auth_client)
    investment = create_investment_for_user(auth_client, investment_type['id'], name='My Investment', amount=100.0, current_value=100.0)

    response = auth_client.post(f'/api/investments/{investment["id"]}/contribute', data=json.dumps({
        'amount': 50.0
    }), content_type='application/json')

    assert response.status_code == 200
    assert response.get_json()['current_value'] == 150.0

def test_withdraw_from_investment(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN a withdrawal is posted to the '/api/investments/<id>/withdraw' endpoint
    THEN check that the current_amount is updated
    """
    investment_type = create_investment_type_for_user(auth_client)
    investment = create_investment_for_user(auth_client, investment_type['id'], name='My Investment', amount=100.0, current_value=100.0)

    response = auth_client.post(f'/api/investments/{investment["id"]}/withdraw', data=json.dumps({
        'amount': 25.0
    }), content_type='application/json')

    assert response.status_code == 200
    assert response.get_json()['current_value'] == 75.0

def test_get_investment_summary(auth_client, client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN the '/api/investments/summary' endpoint is requested (GET)
    THEN check that a '200' status code is returned and the summary is correct
    """
    investment_type1 = create_investment_type_for_user(auth_client, name='Stocks')
    investment_type2 = create_investment_type_for_user(auth_client, name='Bonds')

    create_investment_for_user(auth_client, investment_type1['id'], name='Stock A', amount=100.0, current_value=120.0)
    create_investment_for_user(auth_client, investment_type1['id'], name='Stock B', amount=200.0, current_value=180.0)
    create_investment_for_user(auth_client, investment_type2['id'], name='Bond C', amount=50.0, current_value=60.0)

    response = auth_client.get(f'/api/investments/summary')
    assert response.status_code == 200
    summary = response.get_json()

    assert summary['investment_count'] == 3
    assert summary['total_invested'] == 350.0 # 100 + 200 + 50
    assert summary['total_current_value'] == 360.0 # 120 + 180 + 60
    assert summary['total_profit_loss'] == 10.0 # 360 - 350

    # Test with no investments
    # Need a new user or clear investments for current user
    # For simplicity, this test assumes a fresh state or focuses on the calculation logic.
    # In a real scenario, you might create a separate fixture for this.

    # Create a new user for this specific test case
    client.post('/api/register', data=json.dumps({
        'username': 'noinvestuser',
        'email': 'noinvest@example.com',
        'password': 'Password123!'
    }), content_type='application/json')

    login_response = client.post('/api/login', data=json.dumps({
        'username': 'noinvestuser',
        'password': 'Password123!'
    }), content_type='application/json')
    no_invest_token = login_response.get_json()['access_token']

    response_no_invest = client.get(f'/api/investments/summary', headers={'Authorization': f'Bearer {no_invest_token}'})
    assert response_no_invest.status_code == 200
    summary_no_invest = response_no_invest.get_json()
    assert summary_no_invest['investment_count'] == 0
    assert summary_no_invest['total_invested'] == 0.0
    assert summary_no_invest['total_current_value'] == 0.0
    assert summary_no_invest['total_profit_loss'] == 0.0