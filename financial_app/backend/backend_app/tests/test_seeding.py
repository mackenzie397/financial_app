import pytest
from src.models.user import User, db
from src.models.category import Category
from src.models.payment_method import PaymentMethod
from src.models.investment_type import InvestmentType
from src.main import seed_initial_data

def test_seeding_creates_initial_data(app):
    """Testa se a função seed_initial_data cria os dados iniciais quando o DB está vazio."""
    with app.app_context():
        # Garante que o DB está vazio antes do seeding
        db.session.query(Category).delete()
        db.session.query(PaymentMethod).delete()
        db.session.query(InvestmentType).delete()
        db.session.commit()

        # Executa o seeding
        seed_initial_data(app)

        # Verifica se os dados foram criados
        assert Category.query.count() > 0
        assert PaymentMethod.query.count() > 0
        assert InvestmentType.query.count() > 0

def test_seeding_is_idempotent(app):
    """Testa se a função seed_initial_data não duplica dados em execuções subsequentes."""
    with app.app_context():
        # Garante que o DB está vazio antes do primeiro seeding
        db.session.query(Category).delete()
        db.session.query(PaymentMethod).delete()
        db.session.query(InvestmentType).delete()
        db.session.commit()

        # Primeira execução do seeding
        seed_initial_data(app)
        initial_category_count = Category.query.count()
        initial_payment_method_count = PaymentMethod.query.count()
        initial_investment_type_count = InvestmentType.query.count()

        # Segunda execução do seeding
        seed_initial_data(app)

        # Verifica se a contagem de dados não mudou
        assert Category.query.count() == initial_category_count
        assert PaymentMethod.query.count() == initial_payment_method_count
        assert InvestmentType.query.count() == initial_investment_type_count
