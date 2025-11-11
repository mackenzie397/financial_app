from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.investment_type import InvestmentType
from flask_jwt_extended import jwt_required, get_jwt_identity

investment_type_bp = Blueprint("investment_type_bp", __name__)

@investment_type_bp.route("/investment-types", methods=["POST"])
@jwt_required()
def add_investment_type():
    """Add a new investment type
    Creates a new investment type for the authenticated user.
    ---
    tags:
      - Investment Type
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
                example: "Stocks"
    responses:
      201:
        description: Investment type created successfully.
      400:
        description: Bad request (e.g., missing name).
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"message": "Name is required"}), 400

    new_investment_type = InvestmentType(name=name, user_id=user_id)
    db.session.add(new_investment_type)
    db.session.commit()
    return jsonify(new_investment_type.to_dict()), 201

@investment_type_bp.route("/investment-types", methods=["GET"])
@jwt_required()
def get_investment_types():
    """Get all investment types
    Retrieves a list of all investment types for the authenticated user.
    ---
    tags:
      - Investment Type
    security:
      - bearerAuth: []
    responses:
      200:
        description: A list of investment types.
    """
    user_id = get_jwt_identity()
    investment_types = InvestmentType.query.filter_by(user_id=user_id).all()
    return jsonify([investment_type.to_dict() for investment_type in investment_types])

@investment_type_bp.route("/investment-types/<int:id>", methods=["GET"])
@jwt_required()
def get_investment_type(id):
    """Get a specific investment type
    Retrieves a single investment type by its ID.
    ---
    tags:
      - Investment Type
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: The ID of the investment type to retrieve.
    responses:
      200:
        description: The investment type details.
      404:
        description: Investment type not found.
    """
    user_id = get_jwt_identity()
    investment_type = InvestmentType.query.filter_by(id=id, user_id=user_id).first_or_404()
    return jsonify(investment_type.to_dict())

@investment_type_bp.route("/investment-types/<int:id>", methods=["PUT"])
@jwt_required()
def update_investment_type(id):
    """Update an investment type
    Updates the details of a specific investment type.
    ---
    tags:
      - Investment Type
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: The ID of the investment type to update.
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
                example: "Real Estate"
    responses:
      200:
        description: Investment type updated successfully.
      400:
        description: Bad request (e.g., missing name).
      404:
        description: Investment type not found.
    """
    user_id = get_jwt_identity()
    investment_type = InvestmentType.query.filter_by(id=id, user_id=user_id).first_or_404()
    data = request.get_json()
    name = data.get("name")

    if name is None:
        return jsonify({"message": "Name is required"}), 400

    investment_type.name = name
    db.session.commit()
    return jsonify(investment_type.to_dict())

@investment_type_bp.route("/investment-types/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_investment_type(id):
    """Delete an investment type
    Deletes a specific investment type by its ID.
    ---
    tags:
      - Investment Type
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: The ID of the investment type to delete.
    responses:
      200:
        description: Investment type deleted successfully.
      404:
        description: Investment type not found.
    """
    user_id = get_jwt_identity()
    investment_type = InvestmentType.query.filter_by(id=id, user_id=user_id).first_or_404()
    db.session.delete(investment_type)
    db.session.commit()
    return jsonify({"message": "Investment type deleted"})
