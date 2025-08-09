import pytest
from src.models.user import User, db

def test_user_model(app):
    with app.app_context():
        # Cria um novo usuário
        new_user = User(username='testuser', email='test@example.com')
        new_user.set_password('password123')
        
        # Adiciona ao banco de dados em memória
        db.session.add(new_user)
        db.session.commit()

        # Busca o usuário no banco de dados
        retrieved_user = User.query.filter_by(username='testuser').first()

        # Verifica se o usuário foi criado
        assert retrieved_user is not None
        assert retrieved_user.username == 'testuser'
        assert retrieved_user.email == 'test@example.com'

        # Verifica se a senha está correta
        assert retrieved_user.check_password('password123')
        assert not retrieved_user.check_password('wrongpassword')

        # Verifica se o hash da senha não é a senha em texto plano
        assert retrieved_user.password_hash != 'password123'
