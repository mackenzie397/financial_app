from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.category import Category
from flask_jwt_extended import jwt_required, get_jwt_identity

category_bp = Blueprint("category_bp", __name__)

@category_bp.route("/categories", methods=["POST"])
@jwt_required()
def add_category():
    user_id = get_jwt_identity()
    data = request.get_json()

    name = data.get("name")
    category_type = data.get("category_type", "expense")

    if not name:
        return jsonify({"message": "Name is required"}), 400
    if category_type not in ['expense', 'income']:
        return jsonify({"message": "Invalid category type. Must be 'expense' or 'income'"}), 400

    new_category = Category(
        name=name,
        user_id=user_id,
        category_type=category_type
    )
    db.session.add(new_category)
    db.session.commit()
    return jsonify(new_category.to_dict()), 201

@category_bp.route("/categories", methods=["GET"])
@jwt_required()
def get_categories():
    user_id = get_jwt_identity()
    category_type = request.args.get("category_type")
    
    query = Category.query.filter_by(user_id=user_id)
    
    if category_type:
        if category_type not in ['income', 'expense']:
            return jsonify({"message": "Invalid category type filter. Must be 'income' or 'expense'"}), 400
        query = query.filter_by(category_type=category_type)
    
    categories = query.all()
    return jsonify([category.to_dict() for category in categories])

@category_bp.route("/categories/<int:id>", methods=["GET"])
@jwt_required()
def get_category(id):
    user_id = get_jwt_identity()
    category = Category.query.filter_by(id=id, user_id=user_id).first_or_404()
    return jsonify(category.to_dict())

@category_bp.route("/categories/<int:id>", methods=["PUT"])
@jwt_required()
def update_category(id):
    user_id = get_jwt_identity()
    category = Category.query.filter_by(id=id, user_id=user_id).first_or_404()
    data = request.get_json()

    name = data.get("name")
    category_type = data.get("category_type")

    if name is None:
        return jsonify({"message": "Name is required"}), 400
    if category_type is not None and category_type not in ['expense', 'income']:
        return jsonify({"message": "Invalid category type. Must be 'expense' or 'income'"}), 400

    category.name = name
    if category_type is not None:
        category.category_type = category_type
    db.session.commit()
    return jsonify(category.to_dict())

@category_bp.route("/categories/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_category(id):
    user_id = get_jwt_identity()
    category = Category.query.filter_by(id=id, user_id=user_id).first_or_404()
    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Category deleted"})