from http import HTTPStatus

def test_add_goal(auth_client):
    client, user = auth_client
    response = client.post('/api/goals', json={
        'name': 'Dream Vacation',
        'target_amount': 5000.0,
    })
    assert response.status_code == HTTPStatus.CREATED
    assert response.json['name'] == 'Dream Vacation'

def test_get_goals(auth_client, new_goal):
    client, user = auth_client
    response = client.get('/api/goals')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json) == 1
    assert response.json[0]['id'] == new_goal.id

def test_get_single_goal(auth_client, new_goal):
    client, user = auth_client
    response = client.get(f'/api/goals/{new_goal.id}')
    assert response.status_code == HTTPStatus.OK
    assert response.json['id'] == new_goal.id

def test_update_goal(auth_client, new_goal):
    client, user = auth_client
    response = client.put(f'/api/goals/{new_goal.id}', json={'name': 'Updated Goal'})
    assert response.status_code == HTTPStatus.OK
    assert response.json['name'] == 'Updated Goal'

def test_delete_goal(auth_client, new_goal):
    client, user = auth_client
    response = client.delete(f'/api/goals/{new_goal.id}')
    assert response.status_code == HTTPStatus.OK

    response = client.get(f'/api/goals/{new_goal.id}')
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_contribute_to_goal(auth_client, new_goal):
    client, user = auth_client
    response = client.post(f'/api/goals/{new_goal.id}/contribute', json={'amount': 100})
    assert response.status_code == HTTPStatus.OK
    assert response.json['current_amount'] == 100

def test_get_goals_summary(auth_client):
    client, user = auth_client
    client.post('/api/goals', json={'name': 'Goal 1', 'target_amount': 100.0, 'current_amount': 50.0, 'status': 'active'})
    client.post('/api/goals', json={'name': 'Goal 2', 'target_amount': 200.0, 'current_amount': 200.0, 'status': 'completed'})
    client.post('/api/goals', json={'name': 'Goal 3', 'target_amount': 300.0, 'current_amount': 150.0, 'status': 'active'})

    response = client.get(f'/api/goals/summary')
    assert response.status_code == HTTPStatus.OK
    summary = response.json
    assert summary['total_goals'] == 3
    assert summary['active_goals'] == 2
    assert summary['completed_goals'] == 1
    assert summary['total_target_amount'] == 400.0
    assert summary['total_current_amount'] == 200.0
    assert summary['total_progress_percentage'] == 50.0

def test_add_goal_unauthenticated(client):
    response = client.post('/api/goals', json={
        'name': 'Unauthorized Goal',
        'target_amount': 100.0
    })
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_get_goals_unauthenticated(client):
    response = client.get('/api/goals')
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_get_single_goal_unauthenticated(client):
    response = client.get('/api/goals/1')
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_update_goal_unauthenticated(client):
    response = client.put('/api/goals/1', json={'name': 'Unauthorized Update'})
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_delete_goal_unauthenticated(client):
    response = client.delete('/api/goals/1')
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_contribute_to_goal_unauthenticated(client):
    response = client.post('/api/goals/1/contribute', json={'amount': 10.0})
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_get_goal_not_found(auth_client):
    client, user = auth_client
    response = client.get('/api/goals/999')
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_update_goal_not_found(auth_client):
    client, user = auth_client
    response = client.put('/api/goals/999', json={'name': 'Nonexistent'})
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_delete_goal_not_found(auth_client):
    client, user = auth_client
    response = client.delete('/api/goals/999')
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_contribute_to_goal_not_found(auth_client):
    client, user = auth_client
    response = client.post('/api/goals/999/contribute', json={'amount': 10.0})
    assert response.status_code == HTTPStatus.NOT_FOUND

from src.models.user import db, User
from flask_jwt_extended import create_access_token

def test_get_goal_other_user(auth_client, client, app):
    client1, user1 = auth_client
    post_response = client1.post('/api/goals', json={'name': 'User1 Goal', 'target_amount': 1000})
    goal_id = post_response.json['id']

    with app.app_context():
        user2 = User(username='testuser2', email='test2@example.com')
        user2.set_password('Password123!')
        db.session.add(user2)
        db.session.commit()
        token = create_access_token(identity=str(user2.id))

    response = client.get(f'/api/goals/{goal_id}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_update_goal_other_user(auth_client, client, app):
    client1, user1 = auth_client
    post_response = client1.post('/api/goals', json={'name': 'User1 Goal', 'target_amount': 1000})
    goal_id = post_response.json['id']

    with app.app_context():
        user2 = User(username='testuser2', email='test2@example.com')
        user2.set_password('Password123!')
        db.session.add(user2)
        db.session.commit()
        token = create_access_token(identity=str(user2.id))

    response = client.put(f'/api/goals/{goal_id}', json={'name': 'Updated by Other User'}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_delete_goal_other_user(auth_client, client, app):
    client1, user1 = auth_client
    post_response = client1.post('/api/goals', json={'name': 'User1 Goal', 'target_amount': 1000})
    goal_id = post_response.json['id']

    with app.app_context():
        user2 = User(username='testuser2', email='test2@example.com')
        user2.set_password('Password123!')
        db.session.add(user2)
        db.session.commit()
        token = create_access_token(identity=str(user2.id))

    response = client.delete(f'/api/goals/{goal_id}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_contribute_to_goal_other_user(auth_client, client, app):
    client1, user1 = auth_client
    post_response = client1.post('/api/goals', json={'name': 'User1 Goal', 'target_amount': 1000})
    goal_id = post_response.json['id']

    with app.app_context():
        user2 = User(username='testuser2', email='test2@example.com')
        user2.set_password('Password123!')
        db.session.add(user2)
        db.session.commit()
        token = create_access_token(identity=str(user2.id))

    response = client.post(f'/api/goals/{goal_id}/contribute', json={'amount': 10.0}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.NOT_FOUND
