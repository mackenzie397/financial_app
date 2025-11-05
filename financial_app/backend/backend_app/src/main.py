import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, send_from_directory, jsonify
from werkzeug.security import generate_password_hash
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv
import re
import secrets
import string

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

from src.config import config
from src.extensions import jwt, limiter
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
    CORS(app, origins=app.config['CORS_ORIGINS'])

    setup_logging(app)

    # Importar e registrar blueprints
    from src.routes.user import user_bp
    from src.routes.category import category_bp
    from src.routes.payment_method import payment_method_bp
    from src.routes.investment_type import investment_type_bp
    from src.routes.transaction import transaction_bp
    
    from src.routes.investment import investment_bp
    from src.routes.goal import goal_bp

    app.register_blueprint(user_bp, url_prefix='/api')
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
        target_user = User.query.first()

        if not target_user:
            app.logger.info("No users found. Creating a default user...")

            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for i in range(12))

            hashed_password = generate_password_hash(password)
            default_user = User(username='default_user', password_hash=hashed_password)
            db.session.add(default_user)
            db.session.commit()

            target_user = default_user

            print("===================================================================")
            print("USUÁRIO PADRÃO CRIADO:")
            print(f"Username: {target_user.username}")
            print(f"Password: {password}")
            print("Anote esta senha. Ela não será exibida novamente.")
            print("===================================================================")

        user_id_for_seeding = target_user.id
        app.logger.info(f"Seeding data for user_id: {user_id_for_seeding}")

        # Seed Categories
        if Category.query.filter_by(user_id=user_id_for_seeding).count() == 0:
            app.logger.info("Seeding initial categories...")
            categories = [
                Category(user_id=user_id_for_seeding, name='Alimentação', category_type='expense'),
                Category(user_id=user_id_for_seeding, name='Transporte', category_type='expense'),
                Category(user_id=user_id_for_seeding, name='Salário', category_type='income'),
                Category(user_id=user_id_for_seeding, name='Freelance', category_type='income'),
            ]
            db.session.bulk_save_objects(categories)
            db.session.commit()

        # Seed Payment Methods
        if PaymentMethod.query.filter_by(user_id=user_id_for_seeding).count() == 0:
            app.logger.info("Seeding initial payment methods...")
            payment_methods = [
                PaymentMethod(user_id=user_id_for_seeding, name='Dinheiro'),
                PaymentMethod(user_id=user_id_for_seeding, name='Cartão de Débito'),
                PaymentMethod(user_id=user_id_for_seeding, name='PIX'),
            ]
            db.session.bulk_save_objects(payment_methods)
            db.session.commit()

        # Seed Investment Types
        if InvestmentType.query.filter_by(user_id=user_id_for_seeding).count() == 0:
            app.logger.info("Seeding initial investment types...")
            investment_types = [
                InvestmentType(user_id=user_id_for_seeding, name='Renda Fixa'),
                InvestmentType(user_id=user_id_for_seeding, name='Ações'),
                InvestmentType(user_id=user_id_for_seeding, name='Fundos Imobiliários'),
            ]
            db.session.bulk_save_objects(investment_types)
            db.session.commit()

        print("Database seeding completed successfully.")
