from src.models.category import Category
from src.models.user import User, db
import pytest

def test_new_category(app):
    """
    GIVEN a Category model
    WHEN a new Category is created
    THEN check the name, user_id, and category_type fields are defined correctly
    """
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        category = Category(name='Food', user_id=user.id, category_type='expense')
        db.session.add(category)
        db.session.commit()

        assert category.name == 'Food'
        assert category.user_id == user.id
        assert category.category_type == 'expense'
        assert category.id is not None

def test_category_default_type(app):
    """
    GIVEN a Category model
    WHEN a new Category is created without specifying category_type
    THEN check that category_type defaults to 'expense'
    """
    with app.app_context():
        user = User(username='testuser2', email='test2@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        category = Category(name='Rent', user_id=user.id)
        db.session.add(category)
        db.session.commit()

        assert category.name == 'Rent'
        assert category.user_id == user.id
        assert category.category_type == 'expense'

def test_category_repr(app):
    """
    GIVEN a Category model
    WHEN a new Category is created
    THEN check the __repr__ method returns the correct string
    """
    with app.app_context():
        user = User(username='testuser3', email='test3@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        category = Category(name='Utilities', user_id=user.id, category_type='expense')
        db.session.add(category)
        db.session.commit()

        assert repr(category) == '<Category Utilities>'

def test_category_to_dict(app):
    """
    GIVEN a Category model
    WHEN a new Category is created
    THEN check the to_dict method returns the correct dictionary
    """
    with app.app_context():
        user = User(username='testuser4', email='test4@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        category = Category(name='Transport', user_id=user.id, category_type='expense')
        db.session.add(category)
        db.session.commit()

        expected_dict = {
            'id': category.id,
            'name': 'Transport',
            'user_id': user.id,
            'category_type': 'expense'
        }
        assert category.to_dict() == expected_dict
