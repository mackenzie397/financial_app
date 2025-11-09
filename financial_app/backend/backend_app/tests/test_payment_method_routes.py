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

from src.models.user import db, User
from flask_jwt_extended import create_access_token

def test_get_payment_method_other_user(auth_client, client, app):
    client1, user1 = auth_client
    post_response = client1.post('/api/payment-methods', json={'name': 'User1PaymentMethod'})
    payment_method_id = post_response.json['id']

    with app.app_context():
        user2 = User(username='testuser2', email='test2@example.com')
        user2.set_password('Password123!')
        db.session.add(user2)
        db.session.commit()
        token = create_access_token(identity=str(user2.id))

    response = client.get(f'/api/payment-methods/{payment_method_id}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_update_payment_method_other_user(auth_client, client, app):
    client1, user1 = auth_client
    post_response = client1.post('/api/payment-methods', json={'name': 'User1PaymentMethod'})
    payment_method_id = post_response.json['id']

    with app.app_context():
        user2 = User(username='testuser2', email='test2@example.com')
        user2.set_password('Password123!')
        db.session.add(user2)
        db.session.commit()
        token = create_access_token(identity=str(user2.id))

    response = client.put(f'/api/payment-methods/{payment_method_id}', json={'name': 'UpdatedPaymentMethod'}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_delete_payment_method_other_user(auth_client, client, app):
    client1, user1 = auth_client
    post_response = client1.post('/api/payment-methods', json={'name': 'User1PaymentMethod'})
    payment_method_id = post_response.json['id']

    with app.app_context():
        user2 = User(username='testuser2', email='test2@example.com')
        user2.set_password('Password123!')
        db.session.add(user2)
        db.session.commit()
        token = create_access_token(identity=str(user2.id))

    response = client.delete(f'/api/payment-methods/{payment_method_id}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.NOT_FOUND
