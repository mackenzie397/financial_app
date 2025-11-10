
import os

class Config:
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_COOKIE_SAMESITE = 'None'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-key')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    CORS_ORIGINS_STRING = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173')
    CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS_STRING.split(',') if origin.strip()]


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    JWT_SECRET_KEY = 'test-jwt-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_TOKEN_LOCATION = ['headers']
    CORS_ORIGINS = []


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    CORS_ORIGINS_STRING = os.environ.get('CORS_ORIGINS', '')
    CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS_STRING.split(',') if origin.strip()]


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
