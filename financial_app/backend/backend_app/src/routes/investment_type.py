from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.investment_type import InvestmentType
from flask_jwt_extended import jwt_required, get_jwt_identity

investment_type_bp = Blueprint("investment_type_bp", __name__)

@investment_type_bp.route("/investment-types", methods=["POST"])
@jwt_required()
def add_investment_type():
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
    user_id = get_jwt_identity()
    investment_types = InvestmentType.query.filter_by(user_id=user_id).all()
    return jsonify([investment_type.to_dict() for investment_type in investment_types])

@investment_type_bp.route("/investment-types/<int:id>", methods=["GET"])
@jwt_required()
def get_investment_type(id):
    user_id = get_jwt_identity()
    investment_type = InvestmentType.query.filter_by(id=id, user_id=user_id).first_or_404()
    return jsonify(investment_type.to_dict())

@investment_type_bp.route("/investment-types/<int:id>", methods=["PUT"])
@jwt_required()
def update_investment_type(id):
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
    user_id = get_jwt_identity()
    investment_type = InvestmentType.query.filter_by(id=id, user_id=user_id).first_or_404()
    db.session.delete(investment_type)
    db.session.commit()
    return jsonify({"message": "Investment type deleted"})

