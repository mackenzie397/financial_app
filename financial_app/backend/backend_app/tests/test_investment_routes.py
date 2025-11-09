from http import HTTPStatus

def test_add_investment(auth_client, new_investment_type):
    client, user = auth_client
    response = client.post('/api/investments', json={
        'name': 'Tech Stock',
        'amount': 1000.0,
        'investment_type_id': new_investment_type.id
    })
    assert response.status_code == HTTPStatus.CREATED
    assert response.json['name'] == 'Tech Stock'

def test_get_investments(auth_client, new_investment):
    client, user = auth_client
    response = client.get('/api/investments')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json) == 1
    assert response.json[0]['id'] == new_investment.id

def test_get_single_investment(auth_client, new_investment):
    client, user = auth_client
    response = client.get(f'/api/investments/{new_investment.id}')
    assert response.status_code == HTTPStatus.OK
    assert response.json['id'] == new_investment.id

def test_update_investment(auth_client, new_investment):
    client, user = auth_client
    response = client.put(f'/api/investments/{new_investment.id}', json={'name': 'Updated Investment'})
    assert response.status_code == HTTPStatus.OK
    assert response.json['name'] == 'Updated Investment'

def test_delete_investment(auth_client, new_investment):
    client, user = auth_client
    response = client.delete(f'/api/investments/{new_investment.id}')
    assert response.status_code == HTTPStatus.OK

    response = client.get(f'/api/investments/{new_investment.id}')
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_contribute_to_investment(auth_client, new_investment):
    client, user = auth_client
    response = client.post(f'/api/investments/{new_investment.id}/contribute', json={'amount': 100})
    assert response.status_code == HTTPStatus.OK
    assert response.json['current_value'] == 1100

def test_withdraw_from_investment(auth_client, new_investment):
    client, user = auth_client
    response = client.post(f'/api/investments/{new_investment.id}/withdraw', json={'amount': 100})
    assert response.status_code == HTTPStatus.OK
    assert response.json['current_value'] == 900

def test_get_investment_summary(auth_client, new_investment_type):
    client, user = auth_client
    client.post('/api/investments', json={'name': 'Stock A', 'amount': 100.0, 'current_value': 120.0, 'investment_type_id': new_investment_type.id})
    client.post('/api/investments', json={'name': 'Stock B', 'amount': 200.0, 'current_value': 180.0, 'investment_type_id': new_investment_type.id})
    client.post('/api/investments', json={'name': 'Bond C', 'amount': 50.0, 'current_value': 60.0, 'investment_type_id': new_investment_type.id})

    response = client.get(f'/api/investments/summary')
    assert response.status_code == HTTPStatus.OK
    summary = response.json
    assert summary['investment_count'] == 3
    assert summary['total_invested'] == 350.0
    assert summary['total_current_value'] == 360.0
    assert summary['total_profit_loss'] == 10.0

def test_add_investment_unauthenticated(client):
    response = client.post('/api/investments', json={
        'name': 'Unauthorized Investment',
        'amount': 100.0,
        'investment_type_id': 1
    })
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_get_investments_unauthenticated(client):
    response = client.get('/api/investments')
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_get_single_investment_unauthenticated(client):
    response = client.get('/api/investments/1')
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_update_investment_unauthenticated(client):
    response = client.put('/api/investments/1', json={'name': 'Unauthorized Update'})
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_delete_investment_unauthenticated(client):
    response = client.delete('/api/investments/1')
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_get_investment_not_found(auth_client):
    client, user = auth_client
    response = client.get('/api/investments/999')
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_update_investment_not_found(auth_client):
    client, user = auth_client
    response = client.put('/api/investments/999', json={'name': 'Nonexistent'})
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_delete_investment_not_found(auth_client):
    client, user = auth_client
    response = client.delete('/api/investments/999')
    assert response.status_code == HTTPStatus.NOT_FOUND

from src.models.user import db, User
from flask_jwt_extended import create_access_token

def test_get_investment_other_user(auth_client, client, app):
    client1, user1 = auth_client
    investment_type = client1.post('/api/investment-types', json={'name': 'User1 Type'}).json
    investment = client1.post('/api/investments', json={
        'name': 'User1 Investment',
        'amount': 100.0,
        'investment_type_id': investment_type['id']
    }).json

    with app.app_context():
        user2 = User(username='testuser2', email='test2@example.com')
        user2.set_password('Password123!')
        db.session.add(user2)
        db.session.commit()
        token = create_access_token(identity=str(user2.id))

    response = client.get(f'/api/investments/{investment["id"]}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_update_investment_other_user(auth_client, client, app):
    client1, user1 = auth_client
    investment_type = client1.post('/api/investment-types', json={'name': 'User1 Type'}).json
    investment = client1.post('/api/investments', json={
        'name': 'User1 Investment',
        'amount': 100.0,
        'investment_type_id': investment_type['id']
    }).json

    with app.app_context():
        user2 = User(username='testuser2', email='test2@example.com')
        user2.set_password('Password123!')
        db.session.add(user2)
        db.session.commit()
        token = create_access_token(identity=str(user2.id))

    response = client.put(f'/api/investments/{investment["id"]}', json={'name': 'Updated by Other User'}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_delete_investment_other_user(auth_client, client, app):
    client1, user1 = auth_client
    investment_type = client1.post('/api/investment-types', json={'name': 'User1 Type'}).json
    investment = client1.post('/api/investments', json={
        'name': 'User1 Investment',
        'amount': 100.0,
        'investment_type_id': investment_type['id']
    }).json

    with app.app_context():
        user2 = User(username='testuser2', email='test2@example.com')
        user2.set_password('Password123!')
        db.session.add(user2)
        db.session.commit()
        token = create_access_token(identity=str(user2.id))

    response = client.delete(f'/api/investments/{investment["id"]}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.NOT_FOUND
