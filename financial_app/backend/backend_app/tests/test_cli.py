import os
os.environ['FLASK_CONFIG'] = 'testing'

from flask.testing import FlaskCliRunner
from src.models.user import User, db
from src.models.category import Category
from src.models.payment_method import PaymentMethod
from financial_app.backend.backend_app.manage import backfill_defaults_command

def test_backfill_defaults_command(client):
    """
    Tests that the backfill-defaults command correctly adds default items
    to a user who doesn't have them.
    """
    # 1. Create a user without any default items
    user = User(username='olduser', email='old@example.com')
    user.set_password('Password123!')
    db.session.add(user)
    db.session.commit()

    # Verify the user has no categories or payment methods initially
    assert Category.query.filter_by(user_id=user.id).count() == 0
    assert PaymentMethod.query.filter_by(user_id=user.id).count() == 0

    # 2. Run the backfill-defaults command
    runner = client.application.test_cli_runner()
    result = runner.invoke(backfill_defaults_command)

    assert 'Successfully updated 1 users.' in result.output

    # 3. Verify that default items were created for the user
    expense_categories = Category.query.filter_by(user_id=user.id, category_type='expense').count()
    income_categories = Category.query.filter_by(user_id=user.id, category_type='income').count()
    payment_methods = PaymentMethod.query.filter_by(user_id=user.id).count()

    assert expense_categories > 0
    assert income_categories > 0
    assert payment_methods > 0
