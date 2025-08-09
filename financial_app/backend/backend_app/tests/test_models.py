from src.models.user import User

def test_new_user(app):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, and password_hash fields are defined correctly
    """
    user = User(email='test@example.com', username='testuser')
    user.set_password('password123')
    
    assert user.email == 'test@example.com'
    assert user.username == 'testuser'
    assert user.password_hash is not None