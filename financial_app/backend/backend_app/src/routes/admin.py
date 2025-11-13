import os
from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, set_access_cookies
from src.models.user import db, User
from src.extensions import limiter

admin_bp = Blueprint("admin_bp", __name__)

def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if not api_key or api_key != os.getenv('CLEAN_DB_SECRET_KEY'):
            return jsonify({"message": "Unauthorized: Invalid or missing API key"}), 401
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route("/admin/login", methods=["POST"])
@limiter.limit("10 per minute")
def admin_login():
    """Admin Login
    Authenticates an administrator and returns a session cookie.
    Uses separate admin credentials, not the regular user system.
    ---
    tags:
      - Admin
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              username:
                type: string
                example: admin
              password:
                type: string
                example: admin_password
    responses:
      200:
        description: Admin login successful, session cookie is set.
      401:
        description: Invalid admin credentials.
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Get admin credentials from environment
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_password = os.getenv('ADMIN_PASSWORD')

    # Basic authentication
    if not admin_password:
        return jsonify({"message": "Admin authentication not configured"}), 500

    if username == admin_username and password == admin_password:
        # Create a dummy token for the admin session
        # Using a special identifier to distinguish from regular users
        access_token = create_access_token(identity="admin:system")
        response = jsonify(
            message="Admin login successful",
            access_token=access_token
        )
        set_access_cookies(response, access_token)
        return response, 200
    else:
        return jsonify({"message": "Invalid admin credentials"}), 401

@admin_bp.route("/admin/clean-database", methods=["POST"])
@api_key_required
@jwt_required()
def clean_database():
    """Clean Database
    Drops and recreates all database tables. Requires admin authentication and a specific API key.
    ---
    tags:
      - Admin
    security:
      - bearerAuth: []
      - apiKey: []
    responses:
      200:
        description: Database cleaned successfully.
        schema:
          type: object
          properties:
            message:
              type: string
              example: All tables dropped and recreated successfully.
      401:
        description: Unauthorized, invalid or missing API key.
      500:
        description: An error occurred while cleaning the database.
    """
    try:
        db.drop_all()
        db.create_all()
        return jsonify({"message": "All tables dropped and recreated successfully."}), 200
    except Exception as e:
        # Log the exception for debugging
        # current_app.logger.error(f"Error cleaning database: {e}", exc_info=True)
        return jsonify({"message": "An error occurred while cleaning the database."}), 500
