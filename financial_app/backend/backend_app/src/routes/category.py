from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.category import Category
from flask_jwt_extended import jwt_required, get_jwt_identity

category_bp = Blueprint("category_bp", __name__)

@category_bp.route("/categories", methods=["POST"])
@jwt_required()
def add_category():
    """Add a new category
    Creates a new category for the authenticated user.
    ---
    tags:
      - Category
    security:
      - bearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - name
            properties:
              name:
                type: string
                example: "Groceries"
              category_type:
                type: string
                enum: [income, expense]
                example: "expense"
    responses:
      201:
        description: Category created successfully.
      400:
        description: Bad request (e.g., missing name, invalid category type).
    """
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
    """Get all categories
    Retrieves a list of all categories for the authenticated user, with optional filtering by type.
    ---
    tags:
      - Category
    security:
      - bearerAuth: []
    parameters:
      - in: query
        name: category_type
        schema:
          type: string
          enum: [income, expense]
        description: Filter categories by type (income or expense).
    responses:
      200:
        description: A list of categories.
      400:
        description: Bad request (e.g., invalid category type filter).
    """
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
    """Get a specific category
    Retrieves a single category by its ID.
    ---
    tags:
      - Category
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: The ID of the category to retrieve.
    responses:
      200:
        description: The category details.
      404:
        description: Category not found.
    """
    user_id = get_jwt_identity()
    category = Category.query.filter_by(id=id, user_id=user_id).first_or_404()
    return jsonify(category.to_dict())

@category_bp.route("/categories/<int:id>", methods=["PUT"])
@jwt_required()
def update_category(id):
    """Update a category
    Updates the details of a specific category.
    ---
    tags:
      - Category
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: The ID of the category to update.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - name
            properties:
              name:
                type: string
                example: "Supermarket"
              category_type:
                type: string
                enum: [income, expense]
                example: "expense"
    responses:
      200:
        description: Category updated successfully.
      400:
        description: Bad request (e.g., missing name, invalid category type).
      404:
        description: Category not found.
    """
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
    """Delete a category
    Deletes a specific category by its ID.
    ---
    tags:
      - Category
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: The ID of the category to delete.
    responses:
      200:
        description: Category deleted successfully.
      404:
        description: Category not found.
    """
    user_id = get_jwt_identity()
    category = Category.query.filter_by(id=id, user_id=user_id).first_or_404()
    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Category deleted"})