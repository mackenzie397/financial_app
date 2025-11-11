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
    """Add a new transaction
    Creates a new income or expense transaction for the authenticated user.
    ---
    tags:
      - Transaction
    security:
      - bearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - description
              - amount
              - transaction_type
              - category_id
            properties:
              description:
                type: string
                example: Salary
              amount:
                type: number
                format: float
                example: 2500.00
              date:
                type: string
                format: date
                example: "2024-07-28"
              transaction_type:
                type: string
                enum: [income, expense]
                example: income
              category_id:
                type: integer
                example: 1
              payment_method_id:
                type: integer
                example: 1
              notes:
                type: string
                example: Monthly salary deposit.
    responses:
      201:
        description: Transaction created successfully.
      400:
        description: Bad request (e.g., missing fields, invalid data).
      404:
        description: Not found (e.g., category or payment method not found).
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    description = data.get("description")
    if description:
        description = bleach.clean(description)
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

    if transaction_type == 'income':
        payment_method_id = None
    elif payment_method_id is None:
        return jsonify({"message": "Payment method ID is required for expense transactions"}), 400

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
    """Get all transactions
    Retrieves a list of all transactions for the authenticated user, with optional filtering by year and month.
    ---
    tags:
      - Transaction
    security:
      - bearerAuth: []
    parameters:
      - name: year
        in: query
        type: integer
        required: false
        description: Filter transactions by year.
      - name: month
        in: query
        type: integer
        required: false
        description: Filter transactions by month.
    responses:
      200:
        description: A list of transactions.
      400:
        description: Bad request (e.g., invalid year or month).
    """
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
    """Get a specific transaction
    Retrieves a single transaction by its ID.
    ---
    tags:
      - Transaction
    security:
      - bearerAuth: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The ID of the transaction to retrieve.
    responses:
      200:
        description: The transaction details.
      404:
        description: Transaction not found.
    """
    user_id = get_jwt_identity()
    transaction = Transaction.query.filter_by(id=id, user_id=user_id).first_or_404()
    return jsonify(transaction.to_dict())

@transaction_bp.route("/transactions/<int:id>", methods=["PUT"])
@jwt_required()
def update_transaction(id):
    """Update a transaction
    Updates the details of a specific transaction.
    ---
    tags:
      - Transaction
    security:
      - bearerAuth: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The ID of the transaction to update.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              description:
                type: string
              amount:
                type: number
                format: float
              date:
                type: string
                format: date
              transaction_type:
                type: string
                enum: [income, expense]
              category_id:
                type: integer
              payment_method_id:
                type: integer
              notes:
                type: string
    responses:
      200:
        description: Transaction updated successfully.
      400:
        description: Bad request (e.g., invalid data).
      404:
        description: Not found (e.g., transaction, category, or payment method not found).
    """
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
    """Delete a transaction
    Deletes a specific transaction by its ID.
    ---
    tags:
      - Transaction
    security:
      - bearerAuth: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The ID of the transaction to delete.
    responses:
      200:
        description: Transaction deleted successfully.
      404:
        description: Transaction not found.
    """
    user_id = get_jwt_identity()
    transaction = Transaction.query.filter_by(id=id, user_id=user_id).first_or_404()
    db.session.delete(transaction)
    db.session.commit()
    return jsonify({"message": "Transaction deleted"})

@transaction_bp.route("/transactions/summary", methods=["GET"])
@jwt_required()
def get_transactions_summary():
    """Get transactions summary
    Retrieves a summary of income, expenses, and balance for the authenticated user, with optional filtering by year and month.
    ---
    tags:
      - Transaction
    security:
      - bearerAuth: []
    parameters:
      - name: year
        in: query
        type: integer
        required: false
        description: Filter summary by year.
      - name: month
        in: query
        type: integer
        required: false
        description: Filter summary by month.
    responses:
      200:
        description: A summary of transactions.
        content:
          application/json:
            schema:
              type: object
              properties:
                total_income:
                  type: number
                  format: float
                total_expense:
                  type: number
                  format: float
                balance:
                  type: number
                  format: float
                transaction_count:
                  type: integer
      400:
        description: Bad request (e.g., invalid year or month).
    """
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
