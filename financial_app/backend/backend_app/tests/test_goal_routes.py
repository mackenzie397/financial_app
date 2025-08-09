import json
from datetime import date

# Helper function to create a goal for a user
def create_goal_for_user(client, name="Test Goal", target_amount=1000.0, current_amount=0.0, target_date=None, status="active", created_date=None):
    data = {
        'name': name,
        'target_amount': target_amount,
        'current_amount': current_amount,
        'status': status
    }
    if target_date:
        data['target_date'] = target_date.isoformat()
    if created_date:
        data['created_date'] = created_date.isoformat()
    response = client.post('/api/goals', data=json.dumps(data), content_type='application/json')
    return response.get_json()

# --- Goal Routes Tests ---

def test_add_goal(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN a goal is posted to the '/api/goals' endpoint
    THEN check that a '201' status code is returned and the goal is created
    """
    response = auth_client.post('/api/goals', data=json.dumps({
        'name': 'Dream Vacation',
        'description': 'Save for a trip to Hawaii',
        'target_amount': 5000.0,
        'target_date': date(2025, 12, 31).isoformat()
    }), content_type='application/json')

    assert response.status_code == 201
    assert 'id' in response.get_json()
    assert response.get_json()['name'] == 'Dream Vacation'

def test_get_goals(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN the '/api/goals' endpoint is requested (GET)
    THEN check that a '200' status code is returned and a list of goals is returned
    """
    create_goal_for_user(auth_client, name='Goal 1', created_date=date(2024, 1, 1))
    create_goal_for_user(auth_client, name='Goal 2', created_date=date(2024, 1, 2))

    response = auth_client.get(f'/api/goals')
    assert response.status_code == 200
    goals = response.get_json()
    assert len(goals) == 2
    assert any(g['name'] == 'Goal 1' for g in goals)
    assert any(g['name'] == 'Goal 2' for g in goals)
    # Verify order if created_date is distinct
    if goals[0]['name'] == 'Goal 2':
        assert goals[1]['name'] == 'Goal 1'
    elif goals[0]['name'] == 'Goal 1':
        assert goals[1]['name'] == 'Goal 2'

def test_get_goals_by_status(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN the '/api/goals' endpoint is requested with status filter
    THEN check that a '200' status code is returned and filtered goals are returned
    """
    create_goal_for_user(auth_client, name='Active Goal', status='active')
    create_goal_for_user(auth_client, name='Completed Goal', status='completed')

    response = auth_client.get(f'/api/goals?status=active')
    assert response.status_code == 200
    assert len(response.get_json()) == 1
    assert response.get_json()[0]['name'] == 'Active Goal'

def test_get_single_goal(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN the '/api/goals/<id>' endpoint is requested (GET)
    THEN check that a '200' status code is returned and the correct goal is returned
    """
    goal = create_goal_for_user(auth_client, name='Single Goal')

    response = auth_client.get(f'/api/goals/{goal["id"]}')
    assert response.status_code == 200
    assert response.get_json()['name'] == 'Single Goal'

def test_update_goal(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN the '/api/goals/<id>' endpoint is requested (PUT)
    THEN check that a '200' status code is returned and the goal is updated
    """
    goal = create_goal_for_user(auth_client, name='Old Goal')

    response = auth_client.put(f'/api/goals/{goal["id"]}', data=json.dumps({
        'name': 'Updated Goal',
        'target_amount': 2000.0
    }), content_type='application/json')

    assert response.status_code == 200
    assert response.get_json()['name'] == 'Updated Goal'
    assert response.get_json()['target_amount'] == 2000.0

def test_delete_goal(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN the '/api/goals/<id>' endpoint is requested (DELETE)
    THEN check that a '200' status code is returned and the goal is deleted
    """
    goal = create_goal_for_user(auth_client, name='Goal to Delete')

    response = auth_client.delete(f'/api/goals/{goal["id"]}')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Goal deleted'

    # Verify goal is deleted
    get_response = auth_client.get(f'/api/goals/{goal["id"]}')
    assert get_response.status_code == 404

def test_contribute_to_goal(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN a contribution is posted to the '/api/goals/<id>/contribute' endpoint
    THEN check that the current_amount is updated and status changes if target reached
    """
    goal = create_goal_for_user(auth_client, name='Savings Goal', target_amount=1000.0, current_amount=100.0)

    response = auth_client.post(f'/api/goals/{goal["id"]}/contribute', data=json.dumps({
        'amount': 50.0
    }), content_type='application/json')

    assert response.status_code == 200
    assert response.get_json()['current_amount'] == 150.0
    assert response.get_json()['status'] == 'active'

    # Reach target amount
    response = auth_client.post(f'/api/goals/{goal["id"]}/contribute', data=json.dumps({
        'amount': 850.0
    }), content_type='application/json')

    assert response.status_code == 200
    assert response.get_json()['current_amount'] == 1000.0
    assert response.get_json()['status'] == 'completed'

def test_get_goals_summary(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN the '/api/goals/summary' endpoint is requested (GET)
    THEN check that a '200' status code is returned and the summary is correct
    """
    create_goal_for_user(auth_client, name='Goal 1', target_amount=100.0, current_amount=50.0, status='active')
    create_goal_for_user(auth_client, name='Goal 2', target_amount=200.0, current_amount=200.0, status='completed')
    create_goal_for_user(auth_client, name='Goal 3', target_amount=300.0, current_amount=150.0, status='active')

    response = auth_client.get(f'/api/goals/summary')
    assert response.status_code == 200
    summary = response.get_json()

    assert summary['total_goals'] == 3
    assert summary['active_goals'] == 2
    assert summary['completed_goals'] == 1
    assert summary['total_target_amount'] == 400.0 # Active goals: 100 + 300
    assert summary['total_current_amount'] == 200.0 # Active goals: 50 + 150
    assert summary['total_progress_percentage'] == 50.0 # (200/400)*100


def test_add_goal_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN a goal is posted to the '/api/goals' endpoint
    THEN check that a '401' status code is returned
    """
    response = client.post('/api/goals', data=json.dumps({
        'name': 'Unauthorized Goal',
        'target_amount': 100.0
    }), content_type='application/json')
    assert response.status_code == 401

def test_get_goals_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN the '/api/goals' endpoint is requested (GET)
    THEN check that a '401' status code is returned
    """
    response = client.get('/api/goals')
    assert response.status_code == 401

def test_get_single_goal_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN the '/api/goals/<id>' endpoint is requested (GET)
    THEN check that a '401' status code is returned
    """
    response = client.get('/api/goals/1')
    assert response.status_code == 401

def test_update_goal_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN the '/api/goals/<id>' endpoint is requested (PUT)
    THEN check that a '401' status code is returned
    """
    response = client.put('/api/goals/1', data=json.dumps({
        'name': 'Unauthorized Update'
    }), content_type='application/json')
    assert response.status_code == 401

def test_delete_goal_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN the '/api/goals/<id>' endpoint is requested (DELETE)
    THEN check that a '401' status code is returned
    """
    response = client.delete('/api/goals/1')
    assert response.status_code == 401

def test_contribute_to_goal_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN a contribution is posted to the '/api/goals/<id>/contribute' endpoint
    THEN check that a '401' status code is returned
    """
    response = client.post('/api/goals/1/contribute', data=json.dumps({
        'amount': 10.0
    }), content_type='application/json')
    assert response.status_code == 401

def test_get_goals_summary_unauthenticated(client):
    """
    GIVEN a Flask application and an unauthenticated client
    WHEN the '/api/goals/summary' endpoint is requested (GET)
    THEN check that a '401' status code is returned
    """
    response = client.get('/api/goals/summary')
    assert response.status_code == 401

def test_get_goal_not_found(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN a nonexistent goal is requested
    THEN check that a '404' status code is returned
    """
    response = auth_client.get('/api/goals/999')
    assert response.status_code == 404

def test_update_goal_not_found(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN a nonexistent goal is updated
    THEN check that a '404' status code is returned
    """
    response = auth_client.put('/api/goals/999', data=json.dumps({
        'name': 'Nonexistent'
    }), content_type='application/json')
    assert response.status_code == 404

def test_delete_goal_not_found(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN a nonexistent goal is deleted
    THEN check that a '404' status code is returned
    """
    response = auth_client.delete('/api/goals/999')
    assert response.status_code == 404

def test_contribute_to_goal_not_found(auth_client):
    """
    GIVEN a Flask application and an authenticated client
    WHEN a contribution is posted to a nonexistent goal
    THEN check that a '404' status code is returned
    """
    response = auth_client.post('/api/goals/999/contribute', data=json.dumps({
        'amount': 10.0
    }), content_type='application/json')
    assert response.status_code == 404

def test_get_goal_other_user(auth_client, client):
    """
    GIVEN a Flask application and two authenticated users
    WHEN one user tries to access another user's goal
    THEN check that a '404' status code is returned
    """
    # User 1 creates a goal
    goal = create_goal_for_user(auth_client, name='User1 Goal')

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

    # User 2 tries to access User 1's goal
    response = client.get(f'/api/goals/{goal["id"]}', headers={
        'Authorization': f'Bearer {token2}'
    })
    assert response.status_code == 404

def test_update_goal_other_user(auth_client, client):
    """
    GIVEN a Flask application and two authenticated users
    WHEN one user tries to update another user's goal
    THEN check that a '404' status code is returned
    """
    # User 1 creates a goal
    goal = create_goal_for_user(auth_client, name='User1 Goal')

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

    # User 2 tries to update User 1's goal
    response = client.put(f'/api/goals/{goal["id"]}', data=json.dumps({
        'name': 'Updated by Other User'
    }), content_type='application/json', headers={
        'Authorization': f'Bearer {token2}'
    })
    assert response.status_code == 404

def test_delete_goal_other_user(auth_client, client):
    """
    GIVEN a Flask application and two authenticated users
    WHEN one user tries to delete another user's goal
    THEN check that a '404' status code is returned
    """
    # User 1 creates a goal
    goal = create_goal_for_user(auth_client, name='User1 Goal')

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

    # User 2 tries to delete User 1's goal
    response = client.delete(f'/api/goals/{goal["id"]}', headers={
        'Authorization': f'Bearer {token2}'
    })
    assert response.status_code == 404

def test_contribute_to_goal_other_user(auth_client, client):
    """
    GIVEN a Flask application and two authenticated users
    WHEN one user tries to contribute to another user's goal
    THEN check that a '404' status code is returned
    """
    # User 1 creates a goal
    goal = create_goal_for_user(auth_client, name='User1 Goal')

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

    # User 2 tries to contribute to User 1's goal
    response = client.post(f'/api/goals/{goal["id"]}/contribute', data=json.dumps({
        'amount': 10.0
    }), content_type='application/json', headers={
        'Authorization': f'Bearer {token2}'
    })
    assert response.status_code == 404