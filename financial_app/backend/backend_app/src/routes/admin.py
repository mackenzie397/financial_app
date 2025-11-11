import os
from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.models.user import db

admin_bp = Blueprint("admin_bp", __name__)

def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if not api_key or api_key != os.getenv('CLEAN_DB_SECRET_KEY'):
            return jsonify({"message": "Unauthorized: Invalid or missing API key"}), 401
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route("/admin/clean-database", methods=["POST"])
@api_key_required
@jwt_required()
def clean_database():
    """Clean Database
    Drops and recreates all database tables. Requires user authentication and a specific API key.
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
