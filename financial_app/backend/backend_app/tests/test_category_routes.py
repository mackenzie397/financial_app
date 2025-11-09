from http import HTTPStatus

def test_create_category(auth_client):
    client, user = auth_client
    response = client.post('/api/categories', json={'name': 'Food', 'category_type': 'expense'})
    assert response.status_code == HTTPStatus.CREATED
    assert response.json['name'] == 'Food'

def test_get_categories(auth_client, new_category):
    client, user = auth_client
    response = client.get('/api/categories')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json) == 1
    assert response.json[0]['id'] == new_category.id

def test_get_categories_filtered_expense(auth_client):
    client, user = auth_client
    client.post('/api/categories', json={'name': 'Food', 'category_type': 'expense'})
    client.post('/api/categories', json={'name': 'Salary', 'category_type': 'income'})
    response = client.get('/api/categories?category_type=expense')
    assert response.status_code == HTTPStatus.OK
    categories = response.json
    assert len(categories) == 1
    assert categories[0]['name'] == 'Food'

def test_get_categories_filtered_income(auth_client):
    client, user = auth_client
    client.post('/api/categories', json={'name': 'Food', 'category_type': 'expense'})
    client.post('/api/categories', json={'name': 'Salary', 'category_type': 'income'})
    response = client.get('/api/categories?category_type=income')
    assert response.status_code == HTTPStatus.OK
    categories = response.json
    assert len(categories) == 1
    assert categories[0]['name'] == 'Salary'

def test_get_categories_filtered_invalid_type(auth_client):
    client, user = auth_client
    response = client.get('/api/categories?category_type=invalid')
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_get_single_category(auth_client, new_category):
    client, user = auth_client
    response = client.get(f'/api/categories/{new_category.id}')
    assert response.status_code == HTTPStatus.OK
    assert response.json['id'] == new_category.id

def test_update_category(auth_client, new_category):
    client, user = auth_client
    response = client.put(f'/api/categories/{new_category.id}', json={'name': 'Groceries'})
    assert response.status_code == HTTPStatus.OK
    assert response.json['name'] == 'Groceries'

def test_delete_category(auth_client, new_category):
    client, user = auth_client
    response = client.delete(f'/api/categories/{new_category.id}')
    assert response.status_code == HTTPStatus.OK

    response = client.get(f'/api/categories/{new_category.id}')
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_create_category_unauthenticated(client):
    response = client.post('/api/categories', json={'name': 'Food', 'category_type': 'expense'})
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_get_categories_unauthenticated(client):
    response = client.get('/api/categories')
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_get_single_category_unauthenticated(client):
    response = client.get('/api/categories/1')
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_update_category_unauthenticated(client):
    response = client.put('/api/categories/1', json={'name': 'Groceries'})
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_delete_category_unauthenticated(client):
    response = client.delete('/api/categories/1')
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_get_category_not_found(auth_client):
    client, user = auth_client
    response = client.get('/api/categories/999')
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_update_category_not_found(auth_client):
    client, user = auth_client
    response = client.put('/api/categories/999', json={'name': 'Nonexistent'})
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_delete_category_not_found(auth_client):
    client, user = auth_client
    response = client.delete('/api/categories/999')
    assert response.status_code == HTTPStatus.NOT_FOUND

from src.models.user import db, User
from flask_jwt_extended import create_access_token

def test_get_category_other_user(auth_client, client, app):
    client1, user1 = auth_client
    post_response = client1.post('/api/categories', json={'name': 'User1Category', 'category_type': 'expense'})
    category_id = post_response.json['id']

    with app.app_context():
        user2 = User(username='testuser2', email='test2@example.com')
        user2.set_password('Password123!')
        db.session.add(user2)
        db.session.commit()
        token = create_access_token(identity=str(user2.id))

    response = client.get(f'/api/categories/{category_id}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_update_category_other_user(auth_client, client, app):
    client1, user1 = auth_client
    post_response = client1.post('/api/categories', json={'name': 'User1Category', 'category_type': 'expense'})
    category_id = post_response.json['id']

    with app.app_context():
        user2 = User(username='testuser2', email='test2@example.com')
        user2.set_password('Password123!')
        db.session.add(user2)
        db.session.commit()
        token = create_access_token(identity=str(user2.id))

    response = client.put(f'/api/categories/{category_id}', json={'name': 'UpdatedCategory'}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_delete_category_other_user(auth_client, client, app):
    client1, user1 = auth_client
    post_response = client1.post('/api/categories', json={'name': 'User1Category', 'category_type': 'expense'})
    category_id = post_response.json['id']

    with app.app_context():
        user2 = User(username='testuser2', email='test2@example.com')
        user2.set_password('Password123!')
        db.session.add(user2)
        db.session.commit()
        token = create_access_token(identity=str(user2.id))

    response = client.delete(f'/api/categories/{category_id}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.NOT_FOUND
