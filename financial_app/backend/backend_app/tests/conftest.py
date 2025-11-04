import pytest
from src.main import create_app
from src.models.user import db, User
from src.models.category import Category
from src.models.payment_method import PaymentMethod
from src.models.transaction import Transaction
from src.models.goal import Goal
from src.models.investment import Investment
from src.models.investment_type import InvestmentType
from datetime import date
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
def auth_client(client, app):
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('Password123!')
        db.session.add(user)
        db.session.commit()

        client.post('/api/login', json={
            'username': 'testuser',
            'password': 'Password123!'
        })

        yield client, user

@pytest.fixture
def new_category(auth_client, app):
    client, user = auth_client
    with app.app_context():
        category = Category(name='Test Category', category_type='expense', user_id=user.id)
        db.session.add(category)
        db.session.commit()
        return category

@pytest.fixture
def new_payment_method(auth_client, app):
    client, user = auth_client
    with app.app_context():
        payment_method = PaymentMethod(name='Test Payment Method', user_id=user.id)
        db.session.add(payment_method)
        db.session.commit()
        return payment_method

@pytest.fixture
def new_transaction(auth_client, app, new_category, new_payment_method):
    client, user = auth_client
    with app.app_context():
        transaction = Transaction(
            description='Test Transaction',
            amount=100.0,
            date=date.today(),
            transaction_type='expense',
            category_id=new_category.id,
            payment_method_id=new_payment_method.id,
            user_id=user.id
        )
        db.session.add(transaction)
        db.session.commit()
        return transaction

@pytest.fixture
def new_goal(auth_client, app):
    client, user = auth_client
    with app.app_context():
        goal = Goal(
            name='Test Goal',
            target_amount=1000.0,
            user_id=user.id
        )
        db.session.add(goal)
        db.session.commit()
        return goal

@pytest.fixture
def new_investment_type(auth_client, app):
    client, user = auth_client
    with app.app_context():
        investment_type = InvestmentType(name='Test Investment Type', user_id=user.id)
        db.session.add(investment_type)
        db.session.commit()
        return investment_type

@pytest.fixture
def new_investment(auth_client, app, new_investment_type):
    client, user = auth_client
    with app.app_context():
        investment = Investment(
            name='Test Investment',
            amount=1000.0,
            investment_type_id=new_investment_type.id,
            user_id=user.id
        )
        db.session.add(investment)
        db.session.commit()
        return investment