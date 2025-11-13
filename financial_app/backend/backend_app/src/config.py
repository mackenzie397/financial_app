
import os

class Config:
    # Support both cookies and headers for JWT
    # Cookies: For regular frontend (secure, HttpOnly)
    # Headers: For admin dashboard (Bearer token)
    JWT_TOKEN_LOCATION = ['cookies', 'headers']
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_HTTPONLY = True  # Prevent JavaScript access to cookie
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_COOKIE_SAMESITE = 'Strict'  # Default to strict, override in dev
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    JWT_COOKIE_SECURE = False  # Allow HTTP in development
    JWT_COOKIE_SAMESITE = 'None'  # Allow in development for all origins
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
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_SAMESITE = 'Strict'  # Maximum security in production
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
