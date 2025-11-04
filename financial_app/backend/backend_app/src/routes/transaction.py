from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.transaction import Transaction
from src.models.category import Category
from src.models.payment_method import PaymentMethod
from datetime import datetime, timezone
from flask_jwt_extended import jwt_required, get_jwt_identity
import bleach

transaction_bp = Blueprint("transaction_bp", __name__)

@transaction_bp.route("/transactions", methods=["POST"])
@jwt_required()
def add_transaction():
    user_id = get_jwt_identity()
    data = request.get_json()

    description = bleach.clean(data.get("description"))
    amount = data.get("amount")
    date_str = data.get("date")
    transaction_type = data.get("transaction_type")
    category_id = data.get("category_id")
    payment_method_id = data.get("payment_method_id")
    notes = bleach.clean(data.get("notes", ""))

    if not description:
        return jsonify({"message": "Description is required"}), 400
    if amount is None:
        return jsonify({"message": "Amount is required"}), 400
    if not transaction_type:
        return jsonify({"message": "Transaction type is required"}), 400
    if category_id is None:
        return jsonify({"message": "Category ID is required"}), 400
    if transaction_type == 'income':
        payment_method_id = None
    elif payment_method_id is None:
        return jsonify({"message": "Payment method ID is required for expense transactions"}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"message": "Amount must be a positive number"}), 400
    except ValueError:
        return jsonify({"message": "Amount must be a valid number"}), 400

    if transaction_type not in ['income', 'expense']:
        return jsonify({"message": "Invalid transaction type. Must be 'income' or 'expense'"}), 400

    date = datetime.now(timezone.utc).date()
    if date_str:
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400

    # Validate category_id exists and belongs to user
    category = Category.query.filter_by(id=category_id, user_id=user_id).first()
    if not category:
        return jsonify({"message": "Category not found or does not belong to user"}), 404

    # Validate payment_method_id exists and belongs to user, only if provided
    if payment_method_id is not None:
        payment_method = PaymentMethod.query.filter_by(id=payment_method_id, user_id=user_id).first()
        if not payment_method:
            return jsonify({"message": "Payment method not found or does not belong to user"}), 404

    new_transaction = Transaction(
        description=description,
        amount=amount,
        date=date,
        transaction_type=transaction_type,
        category_id=category_id,
        payment_method_id=payment_method_id,
        user_id=user_id,
        notes=notes
    )
    db.session.add(new_transaction)
    db.session.commit()
    return jsonify(new_transaction.to_dict()), 201

@transaction_bp.route("/transactions", methods=["GET"])
@jwt_required()
def get_transactions():
    user_id = get_jwt_identity()
    year = request.args.get("year")
    month = request.args.get("month")
    
    query = Transaction.query
    
    query = query.filter_by(user_id=user_id)
    
    if year:
        try:
            year = int(year)
            query = query.filter(db.extract('year', Transaction.date) == year)
        except ValueError:
            return jsonify({"message": "Invalid year"}), 400
    
    if month:
        try:
            month = int(month)
            query = query.filter(db.extract('month', Transaction.date) == month)
        except ValueError:
            return jsonify({"message": "Invalid month"}), 400
    
    transactions = query.order_by(Transaction.date.desc()).all()
    return jsonify([transaction.to_dict() for transaction in transactions])

@transaction_bp.route("/transactions/<int:id>", methods=["GET"])
@jwt_required()
def get_transaction(id):
    user_id = get_jwt_identity()
    transaction = Transaction.query.filter_by(id=id, user_id=user_id).first_or_404()
    return jsonify(transaction.to_dict())

@transaction_bp.route("/transactions/<int:id>", methods=["PUT"])
@jwt_required()
def update_transaction(id):
    user_id = get_jwt_identity()
    transaction = Transaction.query.filter_by(id=id, user_id=user_id).first_or_404()
    data = request.get_json()
    
    description = data.get("description")
    amount = data.get("amount")
    date_str = data.get("date")
    transaction_type = data.get("transaction_type")
    category_id = data.get("category_id")
    payment_method_id = data.get("payment_method_id")
    notes = data.get("notes")

    if description is not None:
        transaction.description = bleach.clean(description)

    if amount is not None:
        try:
            amount = float(amount)
            if amount <= 0:
                return jsonify({"message": "Amount must be a positive number"}), 400
            transaction.amount = amount
        except ValueError:
            return jsonify({"message": "Amount must be a valid number"}), 400

    if date_str is not None:
        try:
            transaction.date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400

    if transaction_type is not None:
        if transaction_type not in ['income', 'expense']:
            return jsonify({"message": "Invalid transaction type. Must be 'income' or 'expense'"}), 400
        transaction.transaction_type = transaction_type

    if category_id is not None:
        try:
            category_id = int(category_id)
            category = Category.query.filter_by(id=category_id, user_id=user_id).first()
            if not category:
                return jsonify({"message": "Category not found or does not belong to user"}), 404
            transaction.category_id = category_id
        except ValueError:
            return jsonify({"message": "Category ID must be a valid integer"}), 400

    if payment_method_id is not None:
        try:
            payment_method_id = int(payment_method_id)
            payment_method = PaymentMethod.query.filter_by(id=payment_method_id, user_id=user_id).first()
            if not payment_method:
                return jsonify({"message": "Payment method not found or does not belong to user"}), 404
            transaction.payment_method_id = payment_method_id
        except ValueError:
            return jsonify({"message": "Payment method ID must be a valid integer"}), 400

    if notes is not None:
        transaction.notes = bleach.clean(notes)
    
    db.session.commit()
    return jsonify(transaction.to_dict())

@transaction_bp.route("/transactions/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_transaction(id):
    user_id = get_jwt_identity()
    transaction = Transaction.query.filter_by(id=id, user_id=user_id).first_or_404()
    db.session.delete(transaction)
    db.session.commit()
    return jsonify({"message": "Transaction deleted"})

@transaction_bp.route("/transactions/summary", methods=["GET"])
@jwt_required()
def get_transactions_summary():
    user_id = get_jwt_identity()
    year = request.args.get("year")
    month = request.args.get("month")
    
    query = Transaction.query
    
    query = query.filter_by(user_id=user_id)
    
    if year:
        try:
            year = int(year)
            query = query.filter(db.extract('year', Transaction.date) == year)
        except ValueError:
            return jsonify({"message": "Invalid year"}), 400
    
    if month:
        try:
            month = int(month)
            query = query.filter(db.extract('month', Transaction.date) == month)
        except ValueError:
            return jsonify({"message": "Invalid month"}), 400
    
    transactions = query.all()
    
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expense = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    balance = total_income - total_expense
    
    return jsonify({
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "transaction_count": len(transactions)
    })