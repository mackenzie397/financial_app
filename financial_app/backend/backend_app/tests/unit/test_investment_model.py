from src.models.investment import Investment
from src.models.investment_type import InvestmentType
from src.models.user import User, db
from datetime import datetime, timezone, date
import pytest

def test_new_investment(app):
    """
    GIVEN an Investment model
    WHEN a new Investment is created
    THEN check the name, amount, current_value, investment_type_id, and user_id fields are defined correctly
    """
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        investment_type = InvestmentType(name='Stocks', user_id=user.id)
        db.session.add(investment_type)
        db.session.commit()

        investment = Investment(
            name='Apple Stock',
            amount=150.0,
            current_value=155.0,
            investment_type_id=investment_type.id,
            user_id=user.id
        )
        db.session.add(investment)
        db.session.commit()

        assert investment.name == 'Apple Stock'
        assert investment.amount == 150.0
        assert investment.current_value == 155.0
        assert investment.investment_type_id == investment_type.id
        assert investment.user_id == user.id
        assert investment.date == datetime.now(timezone.utc).date()
        assert investment.id is not None

def test_investment_repr(app):
    """
    GIVEN an Investment model
    WHEN a new Investment is created
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

        investment = Investment(
            name='Government Bonds',
            amount=1000.0,
            current_value=1020.0,
            investment_type_id=investment_type.id,
            user_id=user.id
        )
        db.session.add(investment)
        db.session.commit()

        assert repr(investment) == '<Investment Government Bonds>'

def test_investment_to_dict(app):
    """
    GIVEN an Investment model
    WHEN a new Investment is created
    THEN check the to_dict method returns the correct dictionary and calculated fields
    """
    with app.app_context():
        user = User(username='testuser3', email='test3@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        investment_type = InvestmentType(name='Real Estate', user_id=user.id)
        db.session.add(investment_type)
        db.session.commit()

        investment = Investment(
            name='Apartment Complex',
            amount=500000.0,
            current_value=550000.0,
            investment_type_id=investment_type.id,
            user_id=user.id
        )
        db.session.add(investment)
        db.session.commit()

        expected_dict = {
            'id': investment.id,
            'name': 'Apartment Complex',
            'amount': 500000.0,
            'date': datetime.now(timezone.utc).date().isoformat(),
            'current_value': 550000.0,
            'investment_type_id': investment_type.id,
            'user_id': user.id,
            'investment_type': investment_type.to_dict(),
            'profit_loss': 50000.0,
            'profit_loss_percentage': 10.0
        }
        assert investment.to_dict() == expected_dict

def test_investment_to_dict_zero_amount(app):
    """
    GIVEN an Investment with zero amount
    WHEN to_dict method is called
    THEN check profit_loss_percentage is 0.0
    """
    with app.app_context():
        user = User(username='testuser4', email='test4@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        investment_type = InvestmentType(name='Crypto', user_id=user.id)
        db.session.add(investment_type)
        db.session.commit()

        investment = Investment(
            name='Bitcoin',
            amount=0.0,
            current_value=100.0,
            investment_type_id=investment_type.id,
            user_id=user.id
        )
        db.session.add(investment)
        db.session.commit()

        assert investment.to_dict()['profit_loss_percentage'] == 0.0

def test_investment_type_relationship(app):
    """
    GIVEN an Investment and InvestmentType
    WHEN an investment is associated with an investment type
    THEN check that the relationship is correctly established
    """
    with app.app_context():
        user = User(username='testuser5', email='test5@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        investment_type = InvestmentType(name='Stocks', user_id=user.id)
        db.session.add(investment_type)
        db.session.commit()

        investment = Investment(
            name='Google Stock',
            amount=200.0,
            current_value=210.0,
            investment_type_id=investment_type.id,
            user_id=user.id
        )
        db.session.add(investment)
        db.session.commit()

        retrieved_investment = db.session.get(Investment, investment.id)
        assert retrieved_investment.investment_type.name == 'Stocks'
