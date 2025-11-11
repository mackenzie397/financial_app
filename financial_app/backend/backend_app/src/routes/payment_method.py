from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.payment_method import PaymentMethod
from flask_jwt_extended import jwt_required, get_jwt_identity

payment_method_bp = Blueprint("payment_method_bp", __name__, url_prefix="/api")

@payment_method_bp.route("/payment-methods", methods=["POST"])
@jwt_required()
def add_payment_method():
    """Add a new payment method
    Creates a new payment method for the authenticated user.
    ---
    tags:
      - Payment Method
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
                example: "Credit Card"
    responses:
      201:
        description: Payment method created successfully.
      400:
        description: Bad request (e.g., missing name).
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"message": "Name is required"}), 400

    new_payment_method = PaymentMethod(name=name, user_id=user_id)
    db.session.add(new_payment_method)
    db.session.commit()
    return jsonify(new_payment_method.to_dict()), 201

@payment_method_bp.route("/payment-methods", methods=["GET"])
@jwt_required()
def get_payment_methods():
    """Get all payment methods
    Retrieves a list of all payment methods for the authenticated user.
    ---
    tags:
      - Payment Method
    security:
      - bearerAuth: []
    responses:
      200:
        description: A list of payment methods.
    """
    user_id = get_jwt_identity()
    payment_methods = PaymentMethod.query.filter_by(user_id=user_id).all()
    return jsonify([payment_method.to_dict() for payment_method in payment_methods])

@payment_method_bp.route("/payment-methods/<int:id>", methods=["GET"])
@jwt_required()
def get_payment_method(id):
    """Get a specific payment method
    Retrieves a single payment method by its ID.
    ---
    tags:
      - Payment Method
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: The ID of the payment method to retrieve.
    responses:
      200:
        description: The payment method details.
      404:
        description: Payment method not found.
    """
    user_id = get_jwt_identity()
    payment_method = PaymentMethod.query.filter_by(id=id, user_id=user_id).first_or_404()
    return jsonify(payment_method.to_dict())

@payment_method_bp.route("/payment-methods/<int:id>", methods=["PUT"])
@jwt_required()
def update_payment_method(id):
    """Update a payment method
    Updates the details of a specific payment method.
    ---
    tags:
      - Payment Method
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: The ID of the payment method to update.
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
                example: "Debit Card"
    responses:
      200:
        description: Payment method updated successfully.
      400:
        description: Bad request (e.g., missing name).
      404:
        description: Payment method not found.
    """
    user_id = get_jwt_identity()
    payment_method = PaymentMethod.query.filter_by(id=id, user_id=user_id).first_or_404()
    data = request.get_json()
    name = data.get("name")

    if name is None:
        return jsonify({"message": "Name is required"}), 400

    payment_method.name = name
    db.session.commit()
    return jsonify(payment_method.to_dict())

@payment_method_bp.route("/payment-methods/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_payment_method(id):
    """Delete a payment method
    Deletes a specific payment method by its ID.
    ---
    tags:
      - Payment Method
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: The ID of the payment method to delete.
    responses:
      200:
        description: Payment method deleted successfully.
      404:
        description: Payment method not found.
    """
    user_id = get_jwt_identity()
    payment_method = PaymentMethod.query.filter_by(id=id, user_id=user_id).first_or_404()
    db.session.delete(payment_method)
    db.session.commit()
    return jsonify({"message": "Payment method deleted"})