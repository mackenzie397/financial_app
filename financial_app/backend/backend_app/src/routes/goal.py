from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.goal import Goal
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
import bleach

goal_bp = Blueprint("goal_bp", __name__)

@goal_bp.route("/goals", methods=["POST"])
@jwt_required()
def add_goal():
    """Add a new goal
    Creates a new financial goal for the authenticated user.
    ---
    tags:
      - Goal
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
              - target_amount
            properties:
              name:
                type: string
                example: "New Car"
              description:
                type: string
                example: "Saving for a down payment"
              target_amount:
                type: number
                format: float
                example: 10000.00
              current_amount:
                type: number
                format: float
                example: 1500.00
              target_date:
                type: string
                format: date
                example: "2025-12-31"
              status:
                type: string
                enum: [active, completed, paused]
                example: "active"
    responses:
      201:
        description: Goal created successfully.
      400:
        description: Bad request (e.g., missing fields, invalid data).
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    name = bleach.clean(data.get("name"))
    target_amount = data.get("target_amount")
    description = data.get("description")
    if description:
        description = bleach.clean(description)
    current_amount = data.get("current_amount", 0)
    target_date_str = data.get("target_date")
    status = data.get("status", "active")

    if not name:
        return jsonify({"message": "Name is required"}), 400
    if target_amount is None:
        return jsonify({"message": "Target amount is required"}), 400
    try:
        target_amount = float(target_amount)
        if target_amount < 0:
            return jsonify({"message": "Target amount must be a positive number"}), 400
    except ValueError:
        return jsonify({"message": "Target amount must be a valid number"}), 400
    
    try:
        current_amount = float(current_amount)
        if current_amount < 0:
            return jsonify({"message": "Current amount must be a positive number"}), 400
    except ValueError:
        return jsonify({"message": "Current amount must be a valid number"}), 400

    target_date = None
    if target_date_str:
        try:
            target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"message": "Invalid target date format. Use YYYY-MM-DD"}), 400
    
    if status not in ['active', 'completed', 'paused']:
        return jsonify({"message": "Invalid status. Must be 'active', 'completed', or 'paused'"}), 400

    new_goal = Goal(
        name=name,
        description=description,
        target_amount=target_amount,
        current_amount=current_amount,
        target_date=target_date,
        status=status,
        user_id=user_id
    )
    db.session.add(new_goal)
    db.session.commit()
    return jsonify(new_goal.to_dict()), 201

@goal_bp.route("/goals", methods=["GET"])
@jwt_required()
def get_goals():
    """Get all goals
    Retrieves a list of all goals for the authenticated user, with optional filtering by status.
    ---
    tags:
      - Goal
    security:
      - bearerAuth: []
    parameters:
      - in: query
        name: status
        schema:
          type: string
          enum: [active, completed, paused]
        description: Filter goals by status.
    responses:
      200:
        description: A list of goals.
    """
    user_id = get_jwt_identity()
    status = request.args.get("status")
    
    query = Goal.query
    
    query = query.filter_by(user_id=user_id)
    
    if status:
        query = query.filter_by(status=status)
    
    goals = query.order_by(Goal.created_date.desc()).all()
    return jsonify([goal.to_dict() for goal in goals])

@goal_bp.route("/goals/<int:id>", methods=["GET"])
@jwt_required()
def get_goal(id):
    """Get a specific goal
    Retrieves a single goal by its ID.
    ---
    tags:
      - Goal
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: The ID of the goal to retrieve.
    responses:
      200:
        description: The goal details.
      404:
        description: Goal not found.
    """
    user_id = get_jwt_identity()
    goal = Goal.query.filter_by(id=id, user_id=user_id).first_or_404()
    return jsonify(goal.to_dict())

@goal_bp.route("/goals/<int:id>", methods=["PUT"])
@jwt_required()
def update_goal(id):
    """Update a goal
    Updates the details of a specific goal.
    ---
    tags:
      - Goal
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: The ID of the goal to update.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              name:
                type: string
              description:
                type: string
              target_amount:
                type: number
                format: float
              current_amount:
                type: number
                format: float
              target_date:
                type: string
                format: date
              status:
                type: string
                enum: [active, completed, paused]
    responses:
      200:
        description: Goal updated successfully.
      400:
        description: Bad request (e.g., invalid data).
      404:
        description: Goal not found.
    """
    user_id = get_jwt_identity()
    goal = Goal.query.filter_by(id=id, user_id=user_id).first_or_404()
    data = request.get_json()
    
    name = data.get("name")
    target_amount = data.get("target_amount")
    current_amount = data.get("current_amount")
    target_date_str = data.get("target_date")
    status = data.get("status")

    if name is not None:
        goal.name = bleach.clean(name)
    if data.get("description") is not None:
        goal.description = bleach.clean(data.get("description"))

    if target_amount is not None:
        try:
            target_amount = float(target_amount)
            if target_amount < 0:
                return jsonify({"message": "Target amount must be a positive number"}), 400
            goal.target_amount = target_amount
        except ValueError:
            return jsonify({"message": "Target amount must be a valid number"}), 400
    
    if current_amount is not None:
        try:
            current_amount = float(current_amount)
            if current_amount < 0:
                return jsonify({"message": "Current amount must be a positive number"}), 400
            goal.current_amount = current_amount
        except ValueError:
            return jsonify({"message": "Current amount must be a valid number"}), 400

    if target_date_str is not None:
        try:
            goal.target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"message": "Invalid target date format. Use YYYY-MM-DD"}), 400
    
    if status is not None:
        if status not in ['active', 'completed', 'paused']:
            return jsonify({"message": "Invalid status. Must be 'active', 'completed', or 'paused'"}), 400
        goal.status = status
    
    db.session.commit()
    return jsonify(goal.to_dict())

@goal_bp.route("/goals/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_goal(id):
    """Delete a goal
    Deletes a specific goal by its ID.
    ---
    tags:
      - Goal
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: The ID of the goal to delete.
    responses:
      200:
        description: Goal deleted successfully.
      404:
        description: Goal not found.
    """
    user_id = get_jwt_identity()
    goal = Goal.query.filter_by(id=id, user_id=user_id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    return jsonify({"message": "Goal deleted"})

@goal_bp.route("/goals/<int:id>/contribute", methods=["POST"])
@jwt_required()
def contribute_to_goal(id):
    """Contribute to a goal
    Adds a contribution to the current amount of a goal.
    ---
    tags:
      - Goal
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: The ID of the goal to contribute to.
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
                example: 100.00
    responses:
      200:
        description: Contribution added successfully.
      400:
        description: Bad request (e.g., missing or invalid amount).
      404:
        description: Goal not found.
    """
    user_id = get_jwt_identity()
    goal = Goal.query.filter_by(id=id, user_id=user_id).first_or_404()
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

    goal.current_amount += contribution
    
    # Verificar se a meta foi atingida
    if goal.current_amount >= goal.target_amount and goal.status == "active":
        goal.status = "completed"
    
    db.session.commit()
    return jsonify(goal.to_dict())

@goal_bp.route("/goals/summary", methods=["GET"])
@jwt_required()
def get_goals_summary():
    """Get goals summary
    Retrieves a summary of all goals for the authenticated user.
    ---
    tags:
      - Goal
    security:
      - bearerAuth: []
    responses:
      200:
        description: A summary of goals.
        content:
          application/json:
            schema:
              type: object
              properties:
                total_goals:
                  type: integer
                active_goals:
                  type: integer
                completed_goals:
                  type: integer
                total_target_amount:
                  type: number
                  format: float
                total_current_amount:
                  type: number
                  format: float
                total_progress_percentage:
                  type: number
                  format: float
    """
    user_id = get_jwt_identity()
    
    query = Goal.query
    
    query = query.filter_by(user_id=user_id)
    
    goals = query.all()
    
    active_goals = [g for g in goals if g.status == "active"]
    completed_goals = [g for g in goals if g.status == "completed"]
    
    total_target_amount = sum(g.target_amount for g in active_goals)
    total_current_amount = sum(g.current_amount for g in active_goals)
    total_progress_percentage = (total_current_amount / total_target_amount * 100) if total_target_amount > 0 else 0
    
    return jsonify({
        "total_goals": len(goals),
        "active_goals": len(active_goals),
        "completed_goals": len(completed_goals),
        "total_target_amount": total_target_amount,
        "total_current_amount": total_current_amount,
        "total_progress_percentage": total_progress_percentage
    })

