import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, send_from_directory, jsonify, request
from werkzeug.security import generate_password_hash
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv
import re
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Carrega as variáveis de ambiente do arquivo .env na raiz do projeto
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../.env'))
load_dotenv(dotenv_path)

from src.config import config
from src.extensions import jwt, limiter, migrate
from src.models.user import db, User
from src.middleware import set_csp_header
from src.logging_config import setup_logging
from src.models.category import Category
from src.models.payment_method import PaymentMethod
from src.models.investment_type import InvestmentType

def create_app(config_name='default'):
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    app.config.from_object(config[config_name])

    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)

    setup_logging(app)

    # Importar e registrar blueprints
    from src.routes.user import user_bp
    from src.routes.category import category_bp
    from src.routes.payment_method import payment_method_bp
    from src.routes.investment_type import investment_type_bp
    from src.routes.transaction import transaction_bp
    
    from src.routes.investment import investment_bp
    from src.routes.goal import goal_bp
    from src.routes.admin import admin_bp
    from src.routes.admin_dashboard import admin_dashboard_bp

    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api')
    app.register_blueprint(admin_dashboard_bp)
    app.register_blueprint(category_bp, url_prefix='/api')
    app.register_blueprint(payment_method_bp, url_prefix='/api')
    app.register_blueprint(investment_type_bp, url_prefix='/api')
    app.register_blueprint(transaction_bp, url_prefix='/api')
    
    app.register_blueprint(investment_bp, url_prefix='/api')
    app.register_blueprint(goal_bp, url_prefix='/api')

    @app.after_request
    def after_request_func(response):
        return set_csp_header(response)

    # Manipuladores de erro globais
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        response = e.get_response()
        response.data = jsonify({"message": e.description}).data
        response.content_type = "application/json"
        return response

    @app.errorhandler(Exception)
    def handle_exception(e):
        # log the exception with traceback
        app.logger.error(f"Unhandled exception: {e}", exc_info=True)
        return jsonify({"message": "An unexpected error occurred."}), 500

    @app.route('/api/health')
    def health_check():
        try:
            db.session.execute(text('SELECT 1'))
            return jsonify({'status': 'ok'}), 200
        except Exception as e:
            app.logger.error(f"Health check failed: {e}")
            return jsonify({'status': 'error', 'message': 'Database connection failed'}), 503

    # Rota para servir o frontend
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return "Static folder not configured", 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return "index.html not found", 404

    return app

def seed_initial_data(app):
    with app.app_context():
        # Tenta encontrar o primeiro usuário no banco de dados
        target_user = User.query.first()

        # Se nenhum usuário existir, cria um usuário padrão
        if not target_user:
            print("No users found. Creating a default user.")
            password = 'default_password'  # Idealmente, use uma senha mais segura ou gerada aleatoriamente
            hashed_password = generate_password_hash(password)
            default_user = User(username='default_user', email='default@example.com', password_hash=hashed_password)
            db.session.add(default_user)
            db.session.commit()  # Salva o usuário no banco de dados imediatamente
            target_user = default_user
            print(f"Default user '{target_user.username}' created successfully with ID: {target_user.id}")
            print(f"Login with username: {target_user.username} and password: {password}")
        else:
            print(f"Using existing user '{target_user.username}' with ID: {target_user.id} for seeding.")

        user_id_for_seeding = target_user.id

        # Seed Categories
        if Category.query.filter_by(user_id=user_id_for_seeding).count() == 0:
            print("Seeding initial categories...")
            categories = [
                Category(user_id=user_id_for_seeding, name='Alimentação', category_type='expense'),
                Category(user_id=user_id_for_seeding, name='Transporte', category_type='expense'),
                Category(user_id=user_id_for_seeding, name='Salário', category_type='income'),
                Category(user_id=user_id_for_seeding, name='Freelance', category_type='income'),
            ]
            db.session.bulk_save_objects(categories)
            db.session.commit()
            print("Categories seeded.")

        # Seed Payment Methods
        if PaymentMethod.query.filter_by(user_id=user_id_for_seeding).count() == 0:
            print("Seeding initial payment methods...")
            payment_methods = [
                PaymentMethod(user_id=user_id_for_seeding, name='Dinheiro'),
                PaymentMethod(user_id=user_id_for_seeding, name='Cartão de Débito'),
                PaymentMethod(user_id=user_id_for_seeding, name='PIX'),
            ]
            db.session.bulk_save_objects(payment_methods)
            db.session.commit()
            print("Payment methods seeded.")

        # Seed Investment Types
        if InvestmentType.query.filter_by(user_id=user_id_for_seeding).count() == 0:
            print("Seeding initial investment types...")
            investment_types = [
                InvestmentType(user_id=user_id_for_seeding, name='Renda Fixa'),
                InvestmentType(user_id=user_id_for_seeding, name='Ações'),
                InvestmentType(user_id=user_id_for_seeding, name='Fundos Imobiliários'),
            ]
            db.session.bulk_save_objects(investment_types)
            db.session.commit()
            print("Investment types seeded.")

        print("===================================================================")
        print("Database seeding completed successfully.")
        print("You can now log in with the following credentials:")
        print("Username: default_user")
        print("Password: default_password")
        print("It is highly recommended to change this password after your first login.")
        print("===================================================================")
