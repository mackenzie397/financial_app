from flask import Blueprint, request, jsonify
from src.models.user import db, User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from src.extensions import jwt
import re

user_bp = Blueprint("user_bp", __name__)

@user_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"message": "Missing username, email or password"}), 400

    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"message": "Invalid email format"}), 400

    # Validate password strength
    if len(password) < 8:
        return jsonify({"message": "Password must be at least 8 characters long"}), 400
    if not re.search(r"[A-Z]", password):
        return jsonify({"message": "Password must contain at least one uppercase letter"}), 400
    if not re.search(r"[a-z]", password):
        return jsonify({"message": "Password must contain at least one lowercase letter"}), 400
    if not re.search(r"\d", password):
        return jsonify({"message": "Password must contain at least one digit"}), 400
    if not re.search(r"[^a-zA-Z0-9]", password):
        return jsonify({"message": "Password must contain at least one special character"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 409

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@user_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token, user_id=user.id), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@user_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    return jsonify({"message": "Protected data"}), 200

@user_bp.route("/current_user", methods=["GET"])
@jwt_required()
def current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user:
        return jsonify(user.to_dict()), 200
    return jsonify({"message": "User not found"}), 404