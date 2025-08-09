import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp, jwt
from src.routes.category import category_bp
from src.routes.payment_method import payment_method_bp
from src.routes.investment_type import investment_type_bp
from src.routes.transaction import transaction_bp
from src.routes.credit_card import credit_card_bp
from src.routes.investment import investment_bp
from src.routes.goal import goal_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'src', 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'

# Configurar CORS
CORS(app, origins="*")

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(category_bp, url_prefix='/api')
app.register_blueprint(payment_method_bp, url_prefix='/api')
app.register_blueprint(investment_type_bp, url_prefix='/api')
app.register_blueprint(transaction_bp, url_prefix='/api')
app.register_blueprint(credit_card_bp, url_prefix='/api')
app.register_blueprint(investment_bp, url_prefix='/api')
app.register_blueprint(goal_bp, url_prefix='/api')

# Configurar banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
jwt.init_app(app)

with app.app_context():
    db.create_all()
    
    # Criar dados de teste se não existirem
    from src.models.category import Category
    from src.models.payment_method import PaymentMethod
    from src.models.investment_type import InvestmentType
    
    # Verificar se já existem dados
    if Category.query.count() == 0:
        # Criar categorias padrão
        categories = [
            Category(user_id=1, name='Alimentação', category_type='expense'),
            Category(user_id=1, name='Transporte', category_type='expense'),
            Category(user_id=1, name='Saúde', category_type='expense'),
            Category(user_id=1, name='Lazer', category_type='expense'),
            Category(user_id=1, name='Salário', category_type='income'),
            Category(user_id=1, name='Freelance', category_type='income'),
        ]
        for category in categories:
            db.session.add(category)
    
    if PaymentMethod.query.count() == 0:
        # Criar formas de pagamento padrão
        payment_methods = [
            PaymentMethod(user_id=1, name='Dinheiro'),
            PaymentMethod(user_id=1, name='Débito'),
            PaymentMethod(user_id=1, name='Crédito'),
            PaymentMethod(user_id=1, name='PIX'),
            PaymentMethod(user_id=1, name='Transferência'),
        ]
        for method in payment_methods:
            db.session.add(method)
    
    if InvestmentType.query.count() == 0:
        # Criar tipos de investimento padrão
        investment_types = [
            InvestmentType(user_id=1, name='Tesouro Direto'),
            InvestmentType(user_id=1, name='CDB'),
            InvestmentType(user_id=1, name='Ações'),
            InvestmentType(user_id=1, name='Fundos'),
            InvestmentType(user_id=1, name='Criptomoedas'),
        ]
        for inv_type in investment_types:
            db.session.add(inv_type)
    
    db.session.commit()

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

