from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.investment import Investment
from src.models.investment_type import InvestmentType
from datetime import datetime, timezone
from flask_jwt_extended import jwt_required, get_jwt_identity
import bleach

investment_bp = Blueprint("investment_bp", __name__)

@investment_bp.route("/investments", methods=["POST"])
@jwt_required()
def add_investment():
    """Add a new investment
    Creates a new investment for the authenticated user.
    ---
    tags:
      - Investment
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
              - amount
              - investment_type_id
            properties:
              name:
                type: string
                example: "Tech Stocks Portfolio"
              amount:
                type: number
                format: float
                example: 5000.00
              date:
                type: string
                format: date
                example: "2024-01-15"
              current_value:
                type: number
                format: float
                example: 5250.50
              investment_type_id:
                type: integer
                example: 1
    responses:
      201:
        description: Investment created successfully.
      400:
        description: Bad request (e.g., missing fields, invalid data).
      404:
        description: Not found (e.g., investment type not found).
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    name = bleach.clean(data.get("name"))
    amount = data.get("amount")
    date_str = data.get("date")
    current_value = data.get("current_value")
    investment_type_id = data.get("investment_type_id")

    if not name:
        return jsonify({"message": "Name is required"}), 400
    if amount is None:
        return jsonify({"message": "Amount is required"}), 400
    if investment_type_id is None:
        return jsonify({"message": "Investment type ID is required"}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"message": "Amount must be a positive number"}), 400
    except ValueError:
        return jsonify({"message": "Amount must be a valid number"}), 400

    if current_value is None:
        current_value = amount
    else:
        try:
            current_value = float(current_value)
            if current_value < 0:
                return jsonify({"message": "Current value must be a non-negative number"}), 400
        except ValueError:
            return jsonify({"message": "Current value must be a valid number"}), 400

    date = datetime.now(timezone.utc).date()
    if date_str:
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400

    # Validate investment_type_id exists and belongs to user
    investment_type = InvestmentType.query.filter_by(id=investment_type_id, user_id=user_id).first()
    if not investment_type:
        return jsonify({"message": "Investment type not found or does not belong to user"}), 404

    new_investment = Investment(
        name=name,
        amount=amount,
        date=date,
        current_value=current_value,
        investment_type_id=investment_type_id,
        user_id=user_id
    )
    db.session.add(new_investment)
    db.session.commit()
    return jsonify(new_investment.to_dict()), 201

@investment_bp.route("/investments", methods=["GET"])
@jwt_required()
def get_investments():
    """Get all investments
    Retrieves a list of all investments for the authenticated user, with optional filtering.
    ---
    tags:
      - Investment
    security:
      - bearerAuth: []
    parameters:
      - name: investment_type_id
        in: query
        type: integer
        required: false
        description: Filter investments by type ID.
      - name: year
        in: query
        type: integer
        required: false
        description: Filter investments by year.
      - name: month
        in: query
        type: integer
        required: false
        description: Filter investments by month.
    responses:
      200:
        description: A list of investments.
      400:
        description: Bad request (e.g., invalid filter parameters).
    """
    user_id = get_jwt_identity()
    investment_type_id = request.args.get("investment_type_id")
    year = request.args.get("year")
    month = request.args.get("month")
    
    query = Investment.query
    
    query = query.filter_by(user_id=user_id)
    
    if investment_type_id:
        try:
            investment_type_id = int(investment_type_id)
            query = query.filter_by(investment_type_id=investment_type_id)
        except ValueError:
            return jsonify({"message": "Invalid investment type ID"}), 400
    
    if year:
        try:
            year = int(year)
            query = query.filter(db.extract('year', Investment.date) == year)
        except ValueError:
            return jsonify({"message": "Invalid year"}), 400
    
    if month:
        try:
            month = int(month)
            query = query.filter(db.extract('month', Investment.date) == month)
        except ValueError:
            return jsonify({"message": "Invalid month"}), 400
    
    investments = query.order_by(Investment.date.desc()).all()
    return jsonify([investment.to_dict() for investment in investments])

@investment_bp.route("/investments/<int:id>", methods=["GET"])
@jwt_required()
def get_investment(id):
    """Get a specific investment
    Retrieves a single investment by its ID.
    ---
    tags:
      - Investment
    security:
      - bearerAuth: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The ID of the investment to retrieve.
    responses:
      200:
        description: The investment details.
      404:
        description: Investment not found.
    """
    user_id = get_jwt_identity()
    investment = Investment.query.filter_by(id=id, user_id=user_id).first_or_404()
    return jsonify(investment.to_dict())

@investment_bp.route("/investments/<int:id>", methods=["PUT"])
@jwt_required()
def update_investment(id):
    """Update an investment
    Updates the details of a specific investment.
    ---
    tags:
      - Investment
    security:
      - bearerAuth: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The ID of the investment to update.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              name:
                type: string
              amount:
                type: number
                format: float
              date:
                type: string
                format: date
              current_value:
                type: number
                format: float
              investment_type_id:
                type: integer
    responses:
      200:
        description: Investment updated successfully.
      400:
        description: Bad request (e.g., invalid data).
      404:
        description: Not found (e.g., investment or investment type not found).
    """
    user_id = get_jwt_identity()
    investment = Investment.query.filter_by(id=id, user_id=user_id).first_or_404()
    data = request.get_json()
    
    name = data.get("name")
    amount = data.get("amount")
    date_str = data.get("date")
    current_value = data.get("current_value")
    investment_type_id = data.get("investment_type_id")

    if name is not None:
        investment.name = bleach.clean(name)

    if amount is not None:
        try:
            amount = float(amount)
            if amount <= 0:
                return jsonify({"message": "Amount must be a positive number"}), 400
            investment.amount = amount
        except ValueError:
            return jsonify({"message": "Amount must be a valid number"}), 400

    if current_value is not None:
        try:
            current_value = float(current_value)
            if current_value < 0:
                return jsonify({"message": "Current value must be a non-negative number"}), 400
            investment.current_value = current_value
        except ValueError:
            return jsonify({"message": "Current value must be a valid number"}), 400

    if date_str is not None:
        try:
            investment.date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400

    if investment_type_id is not None:
        try:
            investment_type_id = int(investment_type_id)
            # Validate investment_type_id exists and belongs to user
            investment_type = InvestmentType.query.filter_by(id=investment_type_id, user_id=user_id).first()
            if not investment_type:
                return jsonify({"message": "Investment type not found or does not belong to user"}), 404
            investment.investment_type_id = investment_type_id
        except ValueError:
            return jsonify({"message": "Investment type ID must be a valid integer"}), 400
    
    db.session.commit()
    return jsonify(investment.to_dict())

@investment_bp.route("/investments/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_investment(id):
    """Delete an investment
    Deletes a specific investment by its ID.
    ---
    tags:
      - Investment
    security:
      - bearerAuth: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The ID of the investment to delete.
    responses:
      200:
        description: Investment deleted successfully.
      404:
        description: Investment not found.
    """
    user_id = get_jwt_identity()
    investment = Investment.query.filter_by(id=id, user_id=user_id).first_or_404()
    db.session.delete(investment)
    db.session.commit()
    return jsonify({"message": "Investment deleted"})

@investment_bp.route("/investments/<int:id>/contribute", methods=["POST"])
@jwt_required()
def contribute_to_investment(id):
    """Contribute to an investment
    Adds a contribution to the current value of an investment.
    ---
    tags:
      - Investment
    security:
      - bearerAuth: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The ID of the investment to contribute to.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - amount
            properties:
              amount:
                type: number
                format: float
                example: 500.00
    responses:
      200:
        description: Contribution added successfully.
      400:
        description: Bad request (e.g., missing or invalid amount).
      404:
        description: Investment not found.
    """
    user_id = get_jwt_identity()
    investment = Investment.query.filter_by(id=id, user_id=user_id).first_or_404()
    data = request.get_json()
    contribution = data.get("amount")
    
    if contribution is None:
        return jsonify({"message": "Amount is required"}), 400
    try:
        contribution = float(contribution)
        if contribution <= 0:
            return jsonify({"message": "Contribution amount must be a positive number"}), 400
    except ValueError:
        return jsonify({"message": "Contribution amount must be a valid number"}), 400

    investment.current_value += contribution
    
    db.session.commit()
    return jsonify(investment.to_dict())

@investment_bp.route("/investments/<int:id>/withdraw", methods=["POST"])
@jwt_required()
def withdraw_from_investment(id):
    """Withdraw from an investment
    Makes a withdrawal from the current value of an investment.
    ---
    tags:
      - Investment
    security:
      - bearerAuth: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The ID of the investment to withdraw from.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - amount
            properties:
              amount:
                type: number
                format: float
                example: 250.00
    responses:
      200:
        description: Withdrawal made successfully.
      400:
        description: Bad request (e.g., missing, invalid, or insufficient amount).
      404:
        description: Investment not found.
    """
    user_id = get_jwt_identity()
    investment = Investment.query.filter_by(id=id, user_id=user_id).first_or_404()
    data = request.get_json()
    withdrawal = data.get("amount")
    
    if withdrawal is None:
        return jsonify({"message": "Amount is required"}), 400
    try:
        withdrawal = float(withdrawal)
        if withdrawal <= 0:
            return jsonify({"message": "Withdrawal amount must be a positive number"}), 400
    except ValueError:
        return jsonify({"message": "Withdrawal amount must be a valid number"}), 400

    if investment.current_value < withdrawal:
        return jsonify({"message": "Insufficient funds"}), 400
        
    investment.current_value -= withdrawal
    
    db.session.commit()
    return jsonify(investment.to_dict())

@investment_bp.route("/investments/summary", methods=["GET"])
@jwt_required()
def get_investments_summary():
    """Get investments summary
    Retrieves a summary of all investments for the authenticated user.
    ---
    tags:
      - Investment
    security:
      - bearerAuth: []
    responses:
      200:
        description: A summary of investments.
        content:
          application/json:
            schema:
              type: object
              properties:
                total_invested:
                  type: number
                  format: float
                total_current_value:
                  type: number
                  format: float
                total_profit_loss:
                  type: number
                  format: float
                total_profit_loss_percentage:
                  type: number
                  format: float
                investment_count:
                  type: integer
    """
    user_id = get_jwt_identity()
    
    query = Investment.query
    
    query = query.filter_by(user_id=user_id)
    
    investments = query.all()
    total_initial_amount = sum(i.amount for i in investments)
    total_current_value = sum(i.current_value for i in investments)
    total_profit_loss = total_current_value - total_initial_amount
    total_profit_loss_percentage = (total_profit_loss / total_initial_amount * 100) if total_initial_amount > 0 else 0
    
    return jsonify({
        "total_invested": total_initial_amount,
        "total_current_value": total_current_value,
        "total_profit_loss": total_profit_loss,
        "total_profit_loss_percentage": total_profit_loss_percentage,
        "investment_count": len(investments)
    })

