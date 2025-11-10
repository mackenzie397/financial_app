from http import HTTPStatus
from src.models.user import User
from src.models.category import Category
from src.models.payment_method import PaymentMethod

def test_register_successfully_and_creates_defaults(client):
    """
    Tests that user registration is successful and that default categories
    and payment methods are created.
    """
    response = client.post('/api/register', json={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'Password123!'
    })
    assert response.status_code == HTTPStatus.CREATED
    assert response.json['message'] == 'User registered successfully'

    # Verify that the user was created
    user = User.query.filter_by(username='newuser').first()
    assert user is not None

    # Verify default expense categories were created
    expense_categories = Category.query.filter_by(user_id=user.id, category_type='expense').all()
    assert len(expense_categories) > 0
    default_expense_categories = [
        "Alimentação", "Transporte", "Moradia", "Lazer", "Saúde",
        "Educação", "Investimentos", "Outros"
    ]
    expense_category_names = [c.name for c in expense_categories]
    for default_cat in default_expense_categories:
        assert default_cat in expense_category_names

    # Verify default income categories were created
    income_categories = Category.query.filter_by(user_id=user.id, category_type='income').all()
    assert len(income_categories) > 0
    default_income_categories = [
        "Salário", "Renda Extra", "Investimentos", "Outros"
    ]
    income_category_names = [c.name for c in income_categories]
    for default_cat in default_income_categories:
        assert default_cat in income_category_names

    # Verify default payment methods were created
    payment_methods = PaymentMethod.query.filter_by(user_id=user.id).all()
    assert len(payment_methods) > 0
    default_payment_methods = [
        "Dinheiro", "Cartão de Crédito", "Cartão de Débito", "PIX",
        "Transferência Bancária"
    ]
    method_names = [pm.name for pm in payment_methods]
    for default_pm in default_payment_methods:
        assert default_pm in method_names

def test_login_successfully(client):
    client.post('/api/register', json={
        'username': 'loginuser',
        'email': 'login@example.com',
        'password': 'Password123!'
    })
    response = client.post('/api/login', json={
        'username': 'loginuser',
        'password': 'Password123!'
    })
    assert response.status_code == HTTPStatus.OK
    assert response.json['message'] == 'Login successful'
    assert 'access_token_cookie' in response.headers['Set-Cookie']

def test_get_current_user_data(auth_client):
    client, user = auth_client
    response = client.get('/api/current_user')
    assert response.status_code == HTTPStatus.OK
    assert response.json['id'] == user.id
