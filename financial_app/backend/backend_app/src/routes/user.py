from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.category import Category
from src.models.payment_method import PaymentMethod
from src.models.investment_type import InvestmentType
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity,
    set_access_cookies, unset_jwt_cookies
)
from src.extensions import jwt, limiter
import re
import bleach

user_bp = Blueprint("user_bp", __name__)


def _seed_user_defaults(user_id):
    """
    Cria categorias, formas de pagamento e tipos de investimento padrão para novo usuário.
    Esta função garante que todo novo usuário comece com dados básicos.
    """
    default_categories = [
        Category(user_id=user_id, name='Alimentação', category_type='expense'),
        Category(user_id=user_id, name='Transporte', category_type='expense'),
        Category(user_id=user_id, name='Diversão', category_type='expense'),
        Category(user_id=user_id, name='Saúde', category_type='expense'),
        Category(user_id=user_id, name='Moradia', category_type='expense'),
        Category(user_id=user_id, name='Salário', category_type='income'),
        Category(user_id=user_id, name='Freelance', category_type='income'),
    ]
    
    default_payment_methods = [
        PaymentMethod(user_id=user_id, name='Dinheiro'),
        PaymentMethod(user_id=user_id, name='Cartão de Débito'),
        PaymentMethod(user_id=user_id, name='Cartão de Crédito'),
        PaymentMethod(user_id=user_id, name='PIX'),
    ]
    
    default_investment_types = [
        InvestmentType(user_id=user_id, name='Renda Fixa'),
        InvestmentType(user_id=user_id, name='Ações'),
        InvestmentType(user_id=user_id, name='Fundos Imobiliários'),
    ]
    
    db.session.bulk_save_objects(default_categories + default_payment_methods + default_investment_types)
    db.session.commit()

@user_bp.route("/register", methods=["POST"])
@limiter.limit("10 per minute")
def register():
    """User Registration
    Registers a new user in the system.
    ---
    tags:
      - User
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              username:
                type: string
                example: newuser
              email:
                type: string
                example: newuser@example.com
              password:
                type: string
                example: StrongPassword123!
    responses:
      201:
        description: User registered successfully.
      400:
        description: Bad request (e.g., missing fields, invalid email, weak password).
      409:
        description: Conflict (username or email already exists).
    """
    data = request.get_json()
    username = bleach.clean(data.get("username"))
    email = bleach.clean(data.get("email"))
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"message": "Missing username, email or password"}), 400

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"message": "Invalid email format"}), 400

    if len(password) < 8 or not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password) or not re.search(r"\d", password) or not re.search(r"[^a-zA-Z0-9]", password):
        return jsonify({"message": "Password does not meet the strength requirements"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 409

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    # Seed default categories, payment methods, and investment types for new user
    _seed_user_defaults(new_user.id)

    return jsonify({"message": "User registered successfully"}), 201

@user_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    """User Login
    Authenticates a user and returns an access token.
    ---
    tags:
      - User
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              username:
                type: string
                example: testuser
              password:
                type: string
                example: Test@1234
    responses:
      200:
        description: Login successful, access token cookie is set.
      401:
        description: Invalid credentials.
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id))
        response = jsonify(
            message="Login successful",
            access_token=access_token
        )
        # Note: Flasgger doesn't directly support documenting cookie setting,
        # but the response description clarifies this.
        set_access_cookies(response, access_token)
        return response, 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@user_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """User Logout
    Logs out the user by unsetting the JWT cookie.
    ---
    tags:
      - User
    security:
      - bearerAuth: []
    responses:
      200:
        description: Logout successful.
    """
    response = jsonify(message="Logout successful")
    unset_jwt_cookies(response)
    return response, 200

@user_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    """Protected Route Example
    An example of a route that requires authentication.
    ---
    tags:
      - User
    security:
      - bearerAuth: []
    responses:
      200:
        description: Access to protected data successful.
      401:
        description: Unauthorized (missing or invalid token).
    """
    return jsonify({"message": "Protected data"}), 200

@user_bp.route("/current_user", methods=["GET"])
@jwt_required()
def current_user():
    """Get Current User
    Retrieves the details of the currently authenticated user.
    ---
    tags:
      - User
    security:
      - bearerAuth: []
    responses:
      200:
        description: User details retrieved successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                username:
                  type: string
                  example: testuser
                email:
                  type: string
                  example: test@example.com
      401:
        description: Unauthorized (missing or invalid token).
      404:
        description: User not found.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user:
        return jsonify(user.to_dict()), 200
    return jsonify({"message": "User not found"}), 404


def _validate_password_strength(password):
    """
    Valida a força da senha de acordo com os requisitos:
    - Mínimo 8 caracteres
    - Contém letra maiúscula
    - Contém letra minúscula
    - Contém número
    - Contém caractere especial
    
    Retorna None se válida, ou mensagem de erro se inválida.
    """
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return "Password must contain at least one digit"
    if not re.search(r"[^a-zA-Z0-9]", password):
        return "Password must contain at least one special character"
    return None


@user_bp.route("/account/change-password", methods=["POST"])
@jwt_required()
@limiter.limit("5 per 15 minutes")
def change_password():
    """Change User Password
    Allows an authenticated user to change their password.
    Requires the old password for validation and a new password that meets strength requirements.
    ---
    tags:
      - Account
    security:
      - bearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - old_password
              - new_password
            properties:
              old_password:
                type: string
                example: "OldPassword123!"
              new_password:
                type: string
                example: "NewPassword123!"
    responses:
      200:
        description: Password changed successfully.
      400:
        description: Bad request (invalid input, weak password, or same password).
      401:
        description: Unauthorized (old password is incorrect).
      429:
        description: Too many requests (rate limited).
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    data = request.get_json()
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    
    if not old_password or not new_password:
        return jsonify({"message": "Old password and new password are required"}), 400
    
    # Validar senha antiga
    if not user.check_password(old_password):
        return jsonify({"message": "Old password is incorrect"}), 401
    
    # Validar que a nova senha é diferente da antiga
    if old_password == new_password:
        return jsonify({"message": "New password must be different from the old password"}), 400
    
    # Validar força da nova senha
    strength_error = _validate_password_strength(new_password)
    if strength_error:
        return jsonify({"message": strength_error}), 400
    
    # Alterar senha
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({"message": "Password changed successfully"}), 200


@user_bp.route("/account/update-profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """Update User Profile
    Allows an authenticated user to update their profile information (email, username).
    ---
    tags:
      - Account
    security:
      - bearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email:
                type: string
                example: newemail@example.com
              username:
                type: string
                example: newusername
    responses:
      200:
        description: Profile updated successfully.
      400:
        description: Bad request (invalid input).
      409:
        description: Conflict (email or username already exists).
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    data = request.get_json()
    
    # Validar e atualizar email se fornecido
    if "email" in data and data["email"] != user.email:
        email = bleach.clean(data["email"])
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"message": "Invalid email format"}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({"message": "Email already in use"}), 409
        user.email = email
    
    # Validar e atualizar username se fornecido
    if "username" in data and data["username"] != user.username:
        username = bleach.clean(data["username"])
        if User.query.filter_by(username=username).first():
            return jsonify({"message": "Username already in use"}), 409
        user.username = username
    
    db.session.commit()
    return jsonify(user.to_dict()), 200
