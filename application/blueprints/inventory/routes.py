from typing import Any, Dict
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from flask_jwt_extended import jwt_required
from application.blueprints.inventory import inventory_bp
from application.blueprints.inventory.inventorySchemas import part_schema, parts_schema
from application.models import Part
from application.extensions import db, limiter


# CREATE - POST /inventory
@inventory_bp.route("", methods=['POST'])
@jwt_required()
@limiter.limit("20 per hour")
def create_part():
    """
    Create a new part in inventory
    ---
    tags:
      - Inventory
    summary: Create a new part
    description: Creates a new part in the inventory system
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        description: Part data
        required: true
        schema:
          type: object
          required:
            - part_number
            - name
            - category
            - current_cost_cents
            - quantity_in_stock
            - reorder_threshold
          properties:
            part_number:
              type: string
              example: OIL-Filter-002
            name:
              type: string
              example: Premium Oil Filter
            description:
              type: string
              example: High-performance oil filter for most vehicles
            category:
              type: string
              example: Engine
            current_cost_cents:
              type: integer
              example: 1200
            quantity_in_stock:
              type: integer
              example: 50
            reorder_threshold:
              type: integer
              example: 10
    responses:
      201:
        description: Part created successfully
        schema:
          type: object
          properties:
            part_id:
              type: integer
            part_number:
              type: string
            name:
              type: string
            category:
              type: string
            current_cost_cents:
              type: integer
            quantity_in_stock:
              type: integer
      400:
        description: Bad request - validation error or duplicate part number
      401:
        description: Unauthorized
    """
    if not request.json:
        return jsonify({"error": "No JSON data provided"}), 400
    
    try:
        part_data = part_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Check if part_number already exists
    query = select(Part).where(Part.part_number == part_data.part_number)  # type: ignore
    existing_part = db.session.execute(query).scalars().first()
    if existing_part:
        return jsonify({"error": "Part number already exists"}), 400
    
    new_part = part_data  # type: ignore
    db.session.add(new_part)
    db.session.commit()
    return jsonify(part_schema.dump(new_part)), 201


# READ ALL - GET /inventory
@inventory_bp.route("", methods=['GET'])
@jwt_required()
def get_parts():
    """
    Get all parts in inventory
    ---
    tags:
      - Inventory
    summary: Get all parts
    description: Retrieves all parts with optional category filtering and low stock detection
    security:
      - Bearer: []
    parameters:
      - in: query
        name: category
        type: string
        description: Filter by category
        example: Brakes
      - in: query
        name: low_stock
        type: string
        enum: [true, false]
        default: false
        description: Filter for low stock items
    responses:
      200:
        description: List of parts
        schema:
          type: array
          items:
            type: object
            properties:
              part_id:
                type: integer
              part_number:
                type: string
              name:
                type: string
              category:
                type: string
              quantity_in_stock:
                type: integer
      401:
        description: Unauthorized
    """
    # Query parameters for filtering
    low_stock = request.args.get('low_stock', 'false').lower() == 'true'
    category = request.args.get('category')
    
    query = select(Part)
    
    # Apply filters if provided
    if category:
        query = query.where(Part.category == category)
    
    parts = db.session.execute(query).scalars().all()
    
    # Filter for low stock items if requested
    if low_stock:
        parts = [part for part in parts if part.needs_reorder()]
    
    return jsonify(parts_schema.dump(parts)), 200


# READ ONE - GET /inventory/<id>
@inventory_bp.route("/<int:part_id>", methods=['GET'])
@jwt_required()
def get_part(part_id):
    """
    Get a specific part
    ---
    tags:
      - Inventory
    summary: Get part by ID
    description: Retrieves a specific part's information
    security:
      - Bearer: []
    parameters:
      - in: path
        name: part_id
        type: integer
        required: true
        description: The part's ID
    responses:
      200:
        description: Part retrieved successfully
        schema:
          type: object
          properties:
            part_id:
              type: integer
            part_number:
              type: string
            name:
              type: string
            description:
              type: string
            category:
              type: string
            current_cost_cents:
              type: integer
            quantity_in_stock:
              type: integer
            reorder_threshold:
              type: integer
      404:
        description: Part not found
      401:
        description: Unauthorized
    """
    part = db.session.get(Part, part_id)
    
    if part:
        return jsonify(part_schema.dump(part)), 200
    return jsonify({"error": "Part not found"}), 404


# UPDATE - PUT /inventory/<id>
@inventory_bp.route("/<int:part_id>", methods=['PUT'])
@jwt_required()
def update_part(part_id):
    """
    Update a part
    ---
    tags:
      - Inventory
    summary: Update part information
    description: Updates an existing part's information
    security:
      - Bearer: []
    parameters:
      - in: path
        name: part_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - part_number
            - name
            - category
            - current_cost_cents
            - quantity_in_stock
            - reorder_threshold
          properties:
            part_number:
              type: string
              example: OIL-Filter-002
            name:
              type: string
              example: Premium Oil Filter - Updated
            description:
              type: string
              example: High-performance oil filter for most vehicles - Updated description
            category:
              type: string
              example: Engine
            current_cost_cents:
              type: integer
              example: 1300
            quantity_in_stock:
              type: integer
              example: 45
            reorder_threshold:
              type: integer
              example: 8
    responses:
      200:
        description: Part updated successfully
      404:
        description: Part not found
      400:
        description: Bad request
      401:
        description: Unauthorized
    """
    part = db.session.get(Part, part_id)
    
    if not part:
        return jsonify({"error": "Part not found"}), 404
    
    if not request.json:
        return jsonify({"error": "No JSON data provided"}), 400
    
    try:
        part_data = part_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # If part_number is being changed, check if new part_number already exists
    if hasattr(part_data, 'part_number') and part_data.part_number != part.part_number:  # type: ignore
        query = select(Part).where(Part.part_number == part_data.part_number)  # type: ignore
        existing_part = db.session.execute(query).scalars().first()
        if existing_part:
            return jsonify({"error": "Part number already exists"}), 400
    
    # Update part attributes (exclude computed fields like needs_reorder)
    part_dict: Dict[str, Any] = part_schema.dump(part_data)  # type: ignore
    for key, value in part_dict.items():
        if hasattr(part, key) and key not in ['part_id', 'needs_reorder']:
            setattr(part, key, value)
    
    db.session.commit()
    return jsonify(part_schema.dump(part)), 200


# DELETE - DELETE /inventory/<id>
@inventory_bp.route("/<int:part_id>", methods=['DELETE'])
@jwt_required()
def delete_part(part_id):
    """
    Delete a part
    ---
    tags:
      - Inventory
    summary: Delete a part
    description: Deletes a part from inventory
    security:
      - Bearer: []
    parameters:
      - in: path
        name: part_id
        type: integer
        required: true
    responses:
      200:
        description: Part deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
      404:
        description: Part not found
      401:
        description: Unauthorized
    """
    part = db.session.get(Part, part_id)
    
    if not part:
        return jsonify({"error": "Part not found"}), 404
    
    db.session.delete(part)
    db.session.commit()
    return jsonify({"message": f'Part id: {part_id}, successfully deleted'}), 200


# ADJUST QUANTITY - PATCH /inventory/<id>/adjust-quantity
@inventory_bp.route("/<int:part_id>/adjust-quantity", methods=['PATCH'])
@jwt_required()
def adjust_part_quantity(part_id):
    """
    Adjust part quantity
    ---
    tags:
      - Inventory
    summary: Adjust part quantity
    description: Adjusts the quantity of a part in inventory (positive to add, negative to subtract)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: part_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - adjustment
          properties:
            adjustment:
              type: integer
              example: 10
              description: Positive to add, negative to subtract
    responses:
      200:
        description: Quantity adjusted successfully
        schema:
          type: object
          properties:
            message:
              type: string
            part:
              type: object
            adjustment:
              type: integer
            previous_quantity:
              type: integer
            new_quantity:
              type: integer
      400:
        description: Bad request - would result in negative quantity
      404:
        description: Part not found
      401:
        description: Unauthorized
    """
    part = db.session.get(Part, part_id)
    
    if not part:
        return jsonify({"error": "Part not found"}), 404
    
    if not request.json or 'adjustment' not in request.json:
        return jsonify({"error": "adjustment field is required"}), 400
    
    adjustment = request.json['adjustment']
    
    try:
        adjustment = int(adjustment)
    except (ValueError, TypeError):
        return jsonify({"error": "adjustment must be an integer"}), 400
    
    new_quantity = part.quantity_in_stock + adjustment
    
    if new_quantity < 0:
        return jsonify({"error": "Adjustment would result in negative quantity"}), 400
    
    part.quantity_in_stock = new_quantity
    db.session.commit()
    
    return jsonify({
        "message": "Quantity adjusted successfully",
        "part": part_schema.dump(part),
        "adjustment": adjustment,
        "previous_quantity": part.quantity_in_stock - adjustment,
        "new_quantity": part.quantity_in_stock
    }), 200
