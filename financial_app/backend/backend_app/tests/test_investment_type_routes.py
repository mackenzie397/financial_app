from http import HTTPStatus

def test_add_investment_type(auth_client):
    client, user = auth_client
    response = client.post('/api/investment-types', json={'name': 'Stocks'})
    assert response.status_code == HTTPStatus.CREATED
    assert response.json['name'] == 'Stocks'

def test_get_investment_types(auth_client, new_investment_type):
    client, user = auth_client
    response = client.get('/api/investment-types')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json) == 1
    assert response.json[0]['id'] == new_investment_type.id

def test_get_single_investment_type(auth_client, new_investment_type):
    client, user = auth_client
    response = client.get(f'/api/investment-types/{new_investment_type.id}')
    assert response.status_code == HTTPStatus.OK
    assert response.json['id'] == new_investment_type.id

def test_update_investment_type(auth_client, new_investment_type):
    client, user = auth_client
    response = client.put(f'/api/investment-types/{new_investment_type.id}', json={'name': 'Updated Type'})
    assert response.status_code == HTTPStatus.OK
    assert response.json['name'] == 'Updated Type'

def test_delete_investment_type(auth_client, new_investment_type):
    client, user = auth_client
    response = client.delete(f'/api/investment-types/{new_investment_type.id}')
    assert response.status_code == HTTPStatus.OK

    response = client.get(f'/api/investment-types/{new_investment_type.id}')
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_add_investment_type_unauthenticated(client):
    response = client.post('/api/investment-types', json={'name': 'Unauthorized Type'})
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_get_investment_types_unauthenticated(client):
    response = client.get('/api/investment-types')
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_get_single_investment_type_unauthenticated(client):
    response = client.get('/api/investment-types/1')
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_update_investment_type_unauthenticated(client):
    response = client.put('/api/investment-types/1', json={'name': 'Unauthorized Update'})
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_delete_investment_type_unauthenticated(client):
    response = client.delete('/api/investment-types/1')
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_get_investment_type_not_found(auth_client):
    client, user = auth_client
    response = client.get('/api/investment-types/999')
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_update_investment_type_not_found(auth_client):
    client, user = auth_client
    response = client.put('/api/investment-types/999', json={'name': 'Nonexistent'})
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_delete_investment_type_not_found(auth_client):
    client, user = auth_client
    response = client.delete('/api/investment-types/999')
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_get_investment_type_other_user(auth_client, client):
    client1, user1 = auth_client
    # User 1 creates an investment type
    post_response = client1.post('/api/investment-types', json={'name': 'User1 Type'})
    investment_type_id = post_response.json['id']

    # Register and login User 2
    client.post('/api/register', json={
        'username': 'testuser2',
        'email': 'test2@example.com',
        'password': 'Password123!'
    })
    client.post('/api/login', json={
        'username': 'testuser2',
        'password': 'Password123!'
    })

    # User 2 tries to access User 1's investment type
    response = client.get(f'/api/investment-types/{investment_type_id}')
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_update_investment_type_other_user(auth_client, client):
    client1, user1 = auth_client
    # User 1 creates an investment type
    post_response = client1.post('/api/investment-types', json={'name': 'User1 Type'})
    investment_type_id = post_response.json['id']

    # Register and login User 2
    client.post('/api/register', json={
        'username': 'testuser2',
        'email': 'test2@example.com',
        'password': 'Password123!'
    })
    client.post('/api/login', json={
        'username': 'testuser2',
        'password': 'Password123!'
    })

    # User 2 tries to update User 1's investment type
    response = client.put(f'/api/investment-types/{investment_type_id}', json={'name': 'Updated by Other User'})
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_delete_investment_type_other_user(auth_client, client):
    client1, user1 = auth_client
    # User 1 creates an investment type
    post_response = client1.post('/api/investment-types', json={'name': 'User1 Type'})
    investment_type_id = post_response.json['id']

    # Register and login User 2
    client.post('/api/register', json={
        'username': 'testuser2',
        'email': 'test2@example.com',
        'password': 'Password123!'
    })
    client.post('/api/login', json={
        'username': 'testuser2',
        'password': 'Password123!'
    })

    # User 2 tries to delete User 1's investment type
    response = client.delete(f'/api/investment-types/{investment_type_id}')
    assert response.status_code == HTTPStatus.NOT_FOUND
