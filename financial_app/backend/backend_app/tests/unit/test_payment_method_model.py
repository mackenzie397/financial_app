from src.models.payment_method import PaymentMethod
from src.models.user import User, db
import pytest

def test_new_payment_method(app):
    """
    GIVEN a PaymentMethod model
    WHEN a new PaymentMethod is created
    THEN check the name and user_id fields are defined correctly
    """
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        payment_method = PaymentMethod(name='Cash', user_id=user.id)
        db.session.add(payment_method)
        db.session.commit()

        assert payment_method.name == 'Cash'
        assert payment_method.user_id == user.id
        assert payment_method.id is not None

def test_payment_method_repr(app):
    """
    GIVEN a PaymentMethod model
    WHEN a new PaymentMethod is created
    THEN check the __repr__ method returns the correct string
    """
    with app.app_context():
        user = User(username='testuser2', email='test2@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        payment_method = PaymentMethod(name='Bank Transfer', user_id=user.id)
        db.session.add(payment_method)
        db.session.commit()

        assert repr(payment_method) == '<PaymentMethod Bank Transfer>'

def test_payment_method_to_dict(app):
    """
    GIVEN a PaymentMethod model
    WHEN a new PaymentMethod is created
    THEN check the to_dict method returns the correct dictionary
    """
    with app.app_context():
        user = User(username='testuser3', email='test3@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        payment_method = PaymentMethod(name='Credit Card', user_id=user.id)
        db.session.add(payment_method)
        db.session.commit()

        expected_dict = {
            'id': payment_method.id,
            'name': 'Credit Card',
            'user_id': user.id
        }
        assert payment_method.to_dict() == expected_dict
