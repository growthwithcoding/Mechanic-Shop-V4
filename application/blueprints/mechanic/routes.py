from typing import Any, Dict, cast
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from flask_jwt_extended import jwt_required
from application.blueprints.mechanic import mechanic_bp
from application.blueprints.mechanic.mechanicSchemas import mechanic_schema, mechanics_schema
from application.models import Mechanic
from application.extensions import db, limiter, cache


# CREATE - POST /mechanics
@mechanic_bp.route("", methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def create_mechanic():
    """
    Create a new mechanic
    ---
    tags:
      - Mechanics
    summary: Create a new mechanic
    description: Creates a new mechanic in the system
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        description: Mechanic data
        required: true
        schema:
          type: object
          required:
            - first_name
            - last_name
            - email
            - phone
            - salary
          properties:
            first_name:
              type: string
              example: Robert
            last_name:
              type: string
              example: Wilson
            email:
              type: string
              format: email
              example: robert.wilson@mechanicshop.com
            phone:
              type: string
              example: 555-0106
            salary:
              type: number
              format: float
              example: 62000.00
            is_active:
              type: boolean
              example: true
    responses:
      201:
        description: Mechanic created successfully
        schema:
          type: object
          properties:
            mechanic_id:
              type: integer
              example: 6
            first_name:
              type: string
              example: Robert
            last_name:
              type: string
              example: Wilson
            email:
              type: string
              example: robert.wilson@mechanicshop.com
            phone:
              type: string
              example: 555-0106
            salary:
              type: number
              example: 62000.00
            is_active:
              type: boolean
              example: true
      400:
        description: Bad request - validation error or duplicate email
      401:
        description: Unauthorized - missing or invalid JWT token
    """
    if not request.json:
        return jsonify({"error": "No JSON data provided"}), 400
    
    try:
        mechanic_data = cast(Dict[str, Any], mechanic_schema.load(request.json))
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Check if email already exists
    query = select(Mechanic).where(Mechanic.email == mechanic_data['email'])
    existing_mechanic = db.session.execute(query).scalars().first()
    if existing_mechanic:
        return jsonify({"error": "Email already associated with a mechanic."}), 400
    
    new_mechanic = Mechanic(**mechanic_data)
    db.session.add(new_mechanic)
    db.session.commit()
    return jsonify(mechanic_schema.dump(new_mechanic)), 201


# READ ALL - GET /mechanics
# Caching applied: Results are cached for 5 minutes to reduce database load
@mechanic_bp.route("", methods=['GET'])
@jwt_required()
@cache.cached(timeout=300)
def get_mechanics():
    """
    Get all mechanics
    ---
    tags:
      - Mechanics
    summary: Get all mechanics
    description: Retrieves a list of all mechanics in the system (cached for 5 minutes)
    security:
      - Bearer: []
    responses:
      200:
        description: List of mechanics retrieved successfully
        schema:
          type: array
          items:
            type: object
            properties:
              mechanic_id:
                type: integer
                example: 1
              first_name:
                type: string
                example: John
              last_name:
                type: string
                example: Smith
              email:
                type: string
                example: john.smith@mechanicshop.com
              phone:
                type: string
                example: 555-0101
              salary:
                type: number
                example: 65000.00
              is_active:
                type: boolean
                example: true
      401:
        description: Unauthorized - missing or invalid JWT token
    """
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()
    return jsonify(mechanics_schema.dump(mechanics)), 200


# GET MECHANICS BY POPULARITY - GET /mechanics/by-activity
# This endpoint returns mechanics sorted by the number of tickets they've worked on
# Demonstrates using relationship attributes and custom sorting with lambda functions
@mechanic_bp.route("/by-activity", methods=['GET'])
@jwt_required()
def get_mechanics_by_activity():
    """
    Get mechanics sorted by activity
    ---
    tags:
      - Mechanics
    summary: Get mechanics sorted by activity level
    description: |
      Returns mechanics sorted by the number of tickets they've worked on (descending order).
    
      This endpoint demonstrates:
      1. Accessing related data through SQLAlchemy relationships (ticket_mechanics)
      2. Using len() on relationship lists to count related records
      3. Custom sorting with lambda functions based on relationship data
      4. Creating insightful queries that reveal business metrics
    security:
      - Bearer: []
    parameters:
      - in: query
        name: order
        type: string
        enum: [desc, asc]
        default: desc
        description: Sort order (desc for most active first, asc for least active first)
      - in: query
        name: active_only
        type: string
        enum: [true, false]
        default: false
        description: Filter only active mechanics
    responses:
      200:
        description: List of mechanics sorted by activity
        schema:
          type: array
          items:
            type: object
            properties:
              mechanic_id:
                type: integer
                example: 1
              full_name:
                type: string
                example: John Smith
              email:
                type: string
                example: john.smith@mechanicshop.com
              phone:
                type: string
                example: 555-0101
              salary:
                type: number
                example: 65000.00
              is_active:
                type: boolean
                example: true
              ticket_count:
                type: integer
                example: 15
                description: Number of tickets this mechanic has worked on
      401:
        description: Unauthorized - missing or invalid JWT token
    """
    # Original docstring content:
    """
    Returns mechanics sorted by the number of tickets they've worked on (descending order).
    
    This endpoint demonstrates:
    1. Accessing related data through SQLAlchemy relationships (ticket_mechanics)
    2. Using len() on relationship lists to count related records
    3. Custom sorting with lambda functions based on relationship data
    4. Creating insightful queries that reveal business metrics
    
    Query parameters:
    - order: 'desc' (default) for most active first, 'asc' for least active first
    - active_only: 'true' to filter only active mechanics (default: 'false')
    """
    # Get query parameters
    order = request.args.get('order', 'desc').lower()
    active_only = request.args.get('active_only', 'false').lower() == 'true'
    
    # Build query
    query = select(Mechanic)
    if active_only:
        query = query.where(Mechanic.is_active == True)
    
    mechanics = db.session.execute(query).scalars().all()
    
    # Convert to list for sorting (SQLAlchemy result is not directly sortable)
    mechanics_list = list(mechanics)
    
    # Sort mechanics by the number of tickets they've worked on
    # Using lambda function to define custom sorting key
    # The key function accesses the ticket_mechanics relationship and counts the items
    mechanics_list.sort(
        key=lambda mechanic: len(mechanic.ticket_mechanics),
        reverse=(order == 'desc')
    )
    
    # Prepare response with ticket counts included
    result = []
    for mechanic in mechanics_list:
        mechanic_dict = {
            'mechanic_id': mechanic.mechanic_id,
            'full_name': mechanic.full_name,
            'email': mechanic.email,
            'phone': mechanic.phone,
            'salary': mechanic.salary,
            'is_active': mechanic.is_active,
            'ticket_count': len(mechanic.ticket_mechanics)  # Count of tickets worked on
        }
        result.append(mechanic_dict)
    
    return jsonify(result), 200


# READ ONE - GET /mechanics/<id>
@mechanic_bp.route("/<int:mechanic_id>", methods=['GET'])
@jwt_required()
def get_mechanic(mechanic_id):
    """
    Get a specific mechanic
    ---
    tags:
      - Mechanics
    summary: Get mechanic by ID
    description: Retrieves a specific mechanic's information including their ticket count
    security:
      - Bearer: []
    parameters:
      - in: path
        name: mechanic_id
        type: integer
        required: true
        description: The mechanic's ID
        example: 1
    responses:
      200:
        description: Mechanic retrieved successfully
        schema:
          type: object
          properties:
            mechanic_id:
              type: integer
              example: 1
            first_name:
              type: string
              example: John
            last_name:
              type: string
              example: Smith
            email:
              type: string
              example: john.smith@mechanicshop.com
            phone:
              type: string
              example: 555-0101
            salary:
              type: number
              example: 65000.00
            is_active:
              type: boolean
              example: true
            ticket_count:
              type: integer
              example: 15
      404:
        description: Mechanic not found
      401:
        description: Unauthorized - missing or invalid JWT token
    """
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if mechanic:
        # Include ticket count in single mechanic response
        mechanic_dict = cast(Dict[str, Any], mechanic_schema.dump(mechanic))
        return jsonify({**mechanic_dict, 'ticket_count': len(mechanic.ticket_mechanics)}), 200
    return jsonify({"error": "Mechanic not found."}), 404


# UPDATE - PUT /mechanics/<id>
@mechanic_bp.route("/<int:mechanic_id>", methods=['PUT'])
@jwt_required()
def update_mechanic(mechanic_id):
    """
    Update a mechanic
    ---
    tags:
      - Mechanics
    summary: Update mechanic information
    description: Updates an existing mechanic's information
    security:
      - Bearer: []
    parameters:
      - in: path
        name: mechanic_id
        type: integer
        required: true
        description: The mechanic's ID
        example: 1
      - in: body
        name: body
        description: Updated mechanic data
        required: true
        schema:
          type: object
          required:
            - first_name
            - last_name
            - email
            - phone
            - salary
          properties:
            first_name:
              type: string
              example: Robert
            last_name:
              type: string
              example: Wilson
            email:
              type: string
              example: robert.wilson@mechanicshop.com
            phone:
              type: string
              example: 555-0107
            salary:
              type: number
              example: 65000.00
            is_active:
              type: boolean
              example: true
    responses:
      200:
        description: Mechanic updated successfully
        schema:
          type: object
          properties:
            mechanic_id:
              type: integer
              example: 1
            first_name:
              type: string
              example: John
            email:
              type: string
              example: john.smith@mechanicshop.com
            salary:
              type: number
              example: 70000.00
      404:
        description: Mechanic not found
      400:
        description: Bad request - validation error
      401:
        description: Unauthorized - missing or invalid JWT token
    """
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404
    
    if not request.json:
        return jsonify({"error": "No JSON data provided"}), 400
    
    try:
        mechanic_data = cast(Dict[str, Any], mechanic_schema.load(request.json))
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Update mechanic attributes
    for key, value in mechanic_data.items():
        setattr(mechanic, key, value)
    
    db.session.commit()
    return jsonify(mechanic_schema.dump(mechanic)), 200


# DELETE - DELETE /mechanics/<id>
@mechanic_bp.route("/<int:mechanic_id>", methods=['DELETE'])
@jwt_required()
def delete_mechanic(mechanic_id):
    """
    Delete a mechanic
    ---
    tags:
      - Mechanics
    summary: Delete a mechanic
    description: Deletes a mechanic from the system
    security:
      - Bearer: []
    parameters:
      - in: path
        name: mechanic_id
        type: integer
        required: true
        description: The mechanic's ID to delete
        example: 1
    responses:
      200:
        description: Mechanic deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Mechanic id: 1, successfully deleted."
      404:
        description: Mechanic not found
      401:
        description: Unauthorized - missing or invalid JWT token
    """
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404
    
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f'Mechanic id: {mechanic_id}, successfully deleted.'}), 200
