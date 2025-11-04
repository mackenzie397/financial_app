import pytest
from src.main import create_app
from src.models.user import db, User
import json

@pytest.fixture
def app():
    app = create_app('testing')
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def new_user(app):
    with app.app_context():
        user = User(username='testuser_fixture', email='fixture@example.com')
        user.set_password('Password123!')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def auth_client():
    app = create_app('testing')
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )
    with app.app_context():
        db.create_all()
        client = app.test_client()

        # Register a user with a strong password
        register_response = client.post('/api/register', data=json.dumps({
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Password123!'
        }), content_type='application/json')

        # Login the user
        client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'Password123!'
        }), content_type='application/json')

        yield client
        db.drop_all()