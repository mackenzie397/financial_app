from src.models.transaction import Transaction
from src.models.category import Category
from src.models.payment_method import PaymentMethod
from src.models.user import User, db
from datetime import datetime, timezone, date
import pytest

def test_new_transaction(app):
    """
    GIVEN a Transaction model
    WHEN a new Transaction is created
    THEN check the description, amount, date, transaction_type, category_id, payment_method_id, user_id, and notes fields are defined correctly
    """
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        category = Category(name='Food', user_id=user.id, category_type='expense')
        db.session.add(category)
        db.session.commit()

        payment_method = PaymentMethod(name='Cash', user_id=user.id)
        db.session.add(payment_method)
        db.session.commit()

        transaction = Transaction(
            description='Groceries',
            amount=50.0,
            date=datetime.now(timezone.utc).date(),
            transaction_type='expense',
            category_id=category.id,
            payment_method_id=payment_method.id,
            user_id=user.id,
            notes='Weekly shopping'
        )
        db.session.add(transaction)
        db.session.commit()

        assert transaction.description == 'Groceries'
        assert transaction.amount == 50.0
        assert transaction.date == datetime.now(timezone.utc).date()
        assert transaction.transaction_type == 'expense'
        assert transaction.category_id == category.id
        assert transaction.payment_method_id == payment_method.id
        assert transaction.user_id == user.id
        assert transaction.notes == 'Weekly shopping'
        assert transaction.id is not None

def test_transaction_default_notes(app):
    """
    GIVEN a Transaction model
    WHEN a new Transaction is created without specifying notes
    THEN check that notes defaults to an empty string
    """
    with app.app_context():
        user = User(username='testuser2', email='test2@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        category = Category(name='Transport', user_id=user.id, category_type='expense')
        db.session.add(category)
        db.session.commit()

        payment_method = PaymentMethod(name='Credit Card', user_id=user.id)
        db.session.add(payment_method)
        db.session.commit()

        transaction = Transaction(
            description='Bus Fare',
            amount=5.0,
            transaction_type='expense',
            category_id=category.id,
            payment_method_id=payment_method.id,
            user_id=user.id
        )
        db.session.add(transaction)
        db.session.commit()

        assert transaction.notes == ''

def test_transaction_repr(app):
    """
    GIVEN a Transaction model
    WHEN a new Transaction is created
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

        payment_method = PaymentMethod(name='Debit Card', user_id=user.id)
        db.session.add(payment_method)
        db.session.commit()

        transaction = Transaction(
            description='Electricity Bill',
            amount=100.0,
            transaction_type='expense',
            category_id=category.id,
            payment_method_id=payment_method.id,
            user_id=user.id
        )
        db.session.add(transaction)
        db.session.commit()

        assert repr(transaction) == '<Transaction Electricity Bill>'

def test_transaction_to_dict(app):
    """
    GIVEN a Transaction model
    WHEN a new Transaction is created
    THEN check the to_dict method returns the correct dictionary and related names
    """
    with app.app_context():
        user = User(username='testuser4', email='test4@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        category = Category(name='Shopping', user_id=user.id, category_type='expense')
        db.session.add(category)
        db.session.commit()

        payment_method = PaymentMethod(name='Credit Card', user_id=user.id)
        db.session.add(payment_method)
        db.session.commit()

        transaction = Transaction(
            description='New Clothes',
            amount=75.0,
            date=datetime.now(timezone.utc).date(),
            transaction_type='expense',
            category_id=category.id,
            payment_method_id=payment_method.id,
            user_id=user.id,
            notes='Summer collection'
        )
        db.session.add(transaction)
        db.session.commit()

        expected_dict = {
            'id': transaction.id,
            'description': 'New Clothes',
            'amount': 75.0,
            'date': datetime.now(timezone.utc).date().isoformat(),
            'transaction_type': 'expense',
            'category_id': category.id,
            'payment_method_id': payment_method.id,
            'user_id': user.id,
            'notes': 'Summer collection',
            'category_name': 'Shopping',
            'payment_method_name': 'Credit Card'
        }
        assert transaction.to_dict() == expected_dict

def test_transaction_category_relationship(app):
    """
    GIVEN a Transaction and Category
    WHEN a transaction is associated with a category
    THEN check that the relationship is correctly established
    """
    with app.app_context():
        user = User(username='testuser5', email='test5@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        category = Category(name='Books', user_id=user.id, category_type='expense')
        db.session.add(category)
        db.session.commit()

        payment_method = PaymentMethod(name='Debit', user_id=user.id)
        db.session.add(payment_method)
        db.session.commit()

        transaction = Transaction(
            description='New Book',
            amount=25.0,
            transaction_type='expense',
            category_id=category.id,
            payment_method_id=payment_method.id,
            user_id=user.id
        )
        db.session.add(transaction)
        db.session.commit()

        retrieved_transaction = db.session.get(Transaction, transaction.id)
        assert retrieved_transaction.category.name == 'Books'

def test_transaction_payment_method_relationship(app):
    """
    GIVEN a Transaction and PaymentMethod
    WHEN a transaction is associated with a payment method
    THEN check that the relationship is correctly established
    """
    with app.app_context():
        user = User(username='testuser6', email='test6@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        category = Category(name='Electronics', user_id=user.id, category_type='expense')
        db.session.add(category)
        db.session.commit()

        payment_method = PaymentMethod(name='Online Transfer', user_id=user.id)
        db.session.add(payment_method)
        db.session.commit()

        transaction = Transaction(
            description='New Gadget',
            amount=1200.0,
            transaction_type='expense',
            category_id=category.id,
            payment_method_id=payment_method.id,
            user_id=user.id
        )
        db.session.add(transaction)
        db.session.commit()

        retrieved_transaction = db.session.get(Transaction, transaction.id)
        assert retrieved_transaction.payment_method.name == 'Online Transfer'
