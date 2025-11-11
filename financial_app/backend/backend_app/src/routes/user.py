from flask import Blueprint, request, jsonify
from src.models.user import db, User
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity,
    set_access_cookies, unset_jwt_cookies
)
from src.extensions import jwt, limiter
import re
import bleach

user_bp = Blueprint("user_bp", __name__)

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
        response = jsonify(message="Login successful")
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
