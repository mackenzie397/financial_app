from src.models.investment_type import InvestmentType
from src.models.user import User, db
import pytest

def test_new_investment_type(app):
    """
    GIVEN an InvestmentType model
    WHEN a new InvestmentType is created
    THEN check the name and user_id fields are defined correctly
    """
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        investment_type = InvestmentType(name='Stocks', user_id=user.id)
        db.session.add(investment_type)
        db.session.commit()

        assert investment_type.name == 'Stocks'
        assert investment_type.user_id == user.id
        assert investment_type.id is not None

def test_investment_type_repr(app):
    """
    GIVEN an InvestmentType model
    WHEN a new InvestmentType is created
    THEN check the __repr__ method returns the correct string
    """
    with app.app_context():
        user = User(username='testuser2', email='test2@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        investment_type = InvestmentType(name='Bonds', user_id=user.id)
        db.session.add(investment_type)
        db.session.commit()

        assert repr(investment_type) == '<InvestmentType Bonds>'

def test_investment_type_to_dict(app):
    """
    GIVEN an InvestmentType model
    WHEN a new InvestmentType is created
    THEN check the to_dict method returns the correct dictionary
    """
    with app.app_context():
        user = User(username='testuser3', email='test3@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        investment_type = InvestmentType(name='Real Estate', user_id=user.id)
        db.session.add(investment_type)
        db.session.commit()

        expected_dict = {
            'id': investment_type.id,
            'name': 'Real Estate',
            'user_id': user.id
        }
        assert investment_type.to_dict() == expected_dict
