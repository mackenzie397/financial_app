from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.payment_method import PaymentMethod
from flask_jwt_extended import jwt_required, get_jwt_identity

payment_method_bp = Blueprint("payment_method_bp", __name__, url_prefix="/api")

@payment_method_bp.route("/payment-methods", methods=["POST"])
@jwt_required()
def add_payment_method():
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
    user_id = get_jwt_identity()
    payment_methods = PaymentMethod.query.filter_by(user_id=user_id).all()
    return jsonify([payment_method.to_dict() for payment_method in payment_methods])

@payment_method_bp.route("/payment-methods/<int:id>", methods=["GET"])
@jwt_required()
def get_payment_method(id):
    user_id = get_jwt_identity()
    payment_method = PaymentMethod.query.filter_by(id=id, user_id=user_id).first_or_404()
    return jsonify(payment_method.to_dict())

@payment_method_bp.route("/payment-methods/<int:id>", methods=["PUT"])
@jwt_required()
def update_payment_method(id):
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
    user_id = get_jwt_identity()
    payment_method = PaymentMethod.query.filter_by(id=id, user_id=user_id).first_or_404()
    db.session.delete(payment_method)
    db.session.commit()
    return jsonify({"message": "Payment method deleted"})