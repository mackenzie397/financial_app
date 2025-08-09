from src.models.goal import Goal
from src.models.user import User, db
from datetime import datetime, timezone, date
import pytest

def test_new_goal(app):
    """
    GIVEN a Goal model
    WHEN a new Goal is created
    THEN check the name, target_amount, user_id, and default fields are defined correctly
    """
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        goal = Goal(name='Dream Vacation', target_amount=5000.0, user_id=user.id)
        db.session.add(goal)
        db.session.commit()

        assert goal.name == 'Dream Vacation'
        assert goal.target_amount == 5000.0
        assert goal.user_id == user.id
        assert goal.current_amount == 0.0
        assert goal.status == 'active'
        assert goal.created_date == datetime.now(timezone.utc).date()
        assert goal.id is not None

def test_goal_with_all_fields(app):
    """
    GIVEN a Goal model
    WHEN a new Goal is created with all fields specified
    THEN check all fields are defined correctly
    """
    with app.app_context():
        user = User(username='testuser2', email='test2@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        target_date = date(2025, 12, 31)
        created_date = date(2024, 1, 1)
        goal = Goal(
            name='New Car',
            description='Save for a new car',
            target_amount=20000.0,
            current_amount=5000.0,
            target_date=target_date,
            status='paused',
            created_date=created_date,
            user_id=user.id
        )
        db.session.add(goal)
        db.session.commit()

        assert goal.name == 'New Car'
        assert goal.description == 'Save for a new car'
        assert goal.target_amount == 20000.0
        assert goal.current_amount == 5000.0
        assert goal.target_date == target_date
        assert goal.status == 'paused'
        assert goal.created_date == created_date
        assert goal.user_id == user.id

def test_goal_repr(app):
    """
    GIVEN a Goal model
    WHEN a new Goal is created
    THEN check the __repr__ method returns the correct string
    """
    with app.app_context():
        user = User(username='testuser3', email='test3@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        goal = Goal(name='House Down Payment', target_amount=50000.0, user_id=user.id)
        db.session.add(goal)
        db.session.commit()

        assert repr(goal) == '<Goal House Down Payment>'

def test_goal_to_dict(app):
    """
    GIVEN a Goal model
    WHEN a new Goal is created
    THEN check the to_dict method returns the correct dictionary and calculated fields
    """
    with app.app_context():
        user = User(username='testuser4', email='test4@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        target_date = date(2026, 6, 30)
        created_date = date(2024, 7, 1)
        goal = Goal(
            name='Retirement Fund',
            target_amount=100000.0,
            current_amount=25000.0,
            target_date=target_date,
            status='active',
            created_date=created_date,
            user_id=user.id
        )
        db.session.add(goal)
        db.session.commit()

        expected_dict = {
            'id': goal.id,
            'name': 'Retirement Fund',
            'description': None,
            'target_amount': 100000.0,
            'current_amount': 25000.0,
            'target_date': target_date.isoformat(),
            'created_date': created_date.isoformat(),
            'status': 'active',
            'user_id': user.id,
            'progress_percentage': 25.0,
            'remaining_amount': 75000.0
        }
        assert goal.to_dict() == expected_dict

def test_goal_to_dict_zero_target_amount(app):
    """
    GIVEN a Goal with zero target_amount
    WHEN to_dict method is called
    THEN check progress_percentage is 0.0
    """
    with app.app_context():
        user = User(username='testuser5', email='test5@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        goal = Goal(name='Zero Target', target_amount=0.0, current_amount=100.0, user_id=user.id)
        db.session.add(goal)
        db.session.commit()

        assert goal.to_dict()['progress_percentage'] == 0.0
