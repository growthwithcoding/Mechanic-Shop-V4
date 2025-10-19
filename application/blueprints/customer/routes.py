from typing import Any, Dict, cast
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from flask_jwt_extended import jwt_required, get_jwt_identity
from application.blueprints.customer import customer_bp
from application.blueprints.customer.customerSchemas import customer_schema, customers_schema, vehicle_schema, vehicles_schema
from application.models import Customer, Vehicle
from application.extensions import db, limiter


# CREATE - POST /customers
# NOTE: This endpoint is deprecated in favor of /auth/register
# Rate limiting applied: Prevents abuse by limiting customer creation to 5 per hour per IP
# This protects against spam account creation and potential DDOS attacks
@customer_bp.route("", methods=['POST'])
@limiter.limit("5 per hour")
@jwt_required()
def create_customer():
    # Check if request has JSON data
    if not request.json:
        return jsonify({"error": "No JSON data provided"}), 400
    
    try:
        customer_data = cast(Dict[str, Any], customer_schema.load(request.json))
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Check if email already exists
    query = select(Customer).where(Customer.email == customer_data['email'])
    existing_customer = db.session.execute(query).scalars().first()
    if existing_customer:
        return jsonify({"error": "Email already associated with an account."}), 400
    
    new_customer = Customer(**customer_data)
    db.session.add(new_customer)
    db.session.commit()
    return jsonify(customer_schema.dump(new_customer)), 201


# READ ALL - GET /customers
# JWT required: Only authenticated users can view customer list
# Pagination applied: Returns results in manageable chunks using limit and offset
# Query parameters:
#   - page: Page number (default: 1)
#   - per_page: Number of results per page (default: 10, max: 100)
@customer_bp.route("", methods=['GET'])
@jwt_required()
def get_customers():
    """
    Get paginated list of customers.
    
    This endpoint demonstrates efficient data retrieval with pagination:
    1. limit: Controls how many results to return (page size)
    2. offset: Skips a certain number of results (for page navigation)
    
    Query parameters:
    - page: Page number (default: 1)
    - per_page: Results per page (default: 10, max: 100)
    
    Example: /customers?page=2&per_page=20
    Returns the second page with 20 customers per page
    """
    # Get pagination parameters from query string
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Validate pagination parameters
    if page < 1:
        return jsonify({"error": "Page must be >= 1"}), 400
    if per_page < 1 or per_page > 100:
        return jsonify({"error": "Per page must be between 1 and 100"}), 400
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Build query with limit and offset for pagination
    query = select(Customer).limit(per_page).offset(offset)
    customers = db.session.execute(query).scalars().all()
    
    # Get total count for pagination metadata
    count_query = select(db.func.count(Customer.customer_id))
    total_customers = db.session.execute(count_query).scalar() or 0
    
    # Calculate pagination metadata
    total_pages = (total_customers + per_page - 1) // per_page  # Ceiling division
    
    # Prepare response with pagination metadata
    response = {
        'customers': customers_schema.dump(customers),
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_customers': total_customers,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }
    
    return jsonify(response), 200


# READ ONE - GET /customers/<id>
# JWT required: Only authenticated users can view customer details
@customer_bp.route("/<int:customer_id>", methods=['GET'])
@jwt_required()
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    
    if customer:
        return jsonify(customer_schema.dump(customer)), 200
    return jsonify({"error": "Customer not found."}), 404


# UPDATE - PUT /customers/<id>
# JWT required: Only authenticated users can update customer information
@customer_bp.route("/<int:customer_id>", methods=['PUT'])
@jwt_required()
def update_customer(customer_id):
    # Get current user from JWT token (convert from string to int)
    current_user_id = int(get_jwt_identity())
    
    # Users can only update their own information
    if current_user_id != customer_id:
        return jsonify({"error": "Unauthorized to update this customer"}), 403
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return jsonify({"error": "Customer not found."}), 404
    
    # Check if request has JSON data
    if not request.json:
        return jsonify({"error": "No JSON data provided"}), 400
    
    try:
        # Validate the input data
        validated_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Update customer attributes from the original request.json (after validation)
    for key, value in request.json.items():
        if hasattr(customer, key):
            setattr(customer, key, value)
    
    db.session.commit()
    return jsonify(customer_schema.dump(customer)), 200


# DELETE - DELETE /customers/<id>
# JWT required: Only authenticated users can delete their account
@customer_bp.route("/<int:customer_id>", methods=['DELETE'])
@jwt_required()
def delete_customer(customer_id):
    # Get current user from JWT token (convert from string to int)
    current_user_id = int(get_jwt_identity())
    
    # Users can only delete their own account
    if current_user_id != customer_id:
        return jsonify({"error": "Unauthorized to delete this customer"}), 403
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return jsonify({"error": "Customer not found."}), 404
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f'Customer id: {customer_id}, successfully deleted.'}), 200


# ===== VEHICLE ENDPOINTS =====

# CREATE VEHICLE - POST /customers/<id>/vehicles
@customer_bp.route("/<int:customer_id>/vehicles", methods=['POST'])
@jwt_required()
def create_vehicle(customer_id):
    """Create a new vehicle for a customer"""
    # Get current user from JWT token
    current_user_id = int(get_jwt_identity())
    
    # Users can only add vehicles to their own account
    if current_user_id != customer_id:
        return jsonify({"error": "Unauthorized to add vehicles for this customer"}), 403
    
    # Verify customer exists
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    
    # Check if request has JSON data
    if not request.json:
        return jsonify({"error": "No JSON data provided"}), 400
    
    # Add customer_id to the request data before validation
    request_data = dict(request.json)
    request_data['customer_id'] = customer_id
    
    try:
        vehicle_data = cast(Dict[str, Any], vehicle_schema.load(request_data))
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Check if VIN already exists
    query = select(Vehicle).where(Vehicle.vin == vehicle_data['vin'])
    existing_vehicle = db.session.execute(query).scalars().first()
    if existing_vehicle:
        return jsonify({"error": "VIN already exists in the system"}), 400
    
    new_vehicle = Vehicle(**vehicle_data)
    db.session.add(new_vehicle)
    db.session.commit()
    return jsonify(vehicle_schema.dump(new_vehicle)), 201


# READ ALL VEHICLES FOR CUSTOMER - GET /customers/<id>/vehicles
@customer_bp.route("/<int:customer_id>/vehicles", methods=['GET'])
@jwt_required()
def get_customer_vehicles(customer_id):
    """Get all vehicles for a specific customer"""
    # Verify customer exists
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    
    # Get all vehicles for this customer
    query = select(Vehicle).where(Vehicle.customer_id == customer_id)
    vehicles = db.session.execute(query).scalars().all()
    
    return jsonify(vehicles_schema.dump(vehicles)), 200


# READ ONE VEHICLE - GET /customers/<id>/vehicles/<vehicle_id>
@customer_bp.route("/<int:customer_id>/vehicles/<int:vehicle_id>", methods=['GET'])
@jwt_required()
def get_vehicle(customer_id, vehicle_id):
    """Get a specific vehicle"""
    vehicle = db.session.get(Vehicle, vehicle_id)
    
    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404
    
    # Verify vehicle belongs to this customer
    if vehicle.customer_id != customer_id:
        return jsonify({"error": "Vehicle does not belong to this customer"}), 400
    
    return jsonify(vehicle_schema.dump(vehicle)), 200


# UPDATE VEHICLE - PUT /customers/<id>/vehicles/<vehicle_id>
@customer_bp.route("/<int:customer_id>/vehicles/<int:vehicle_id>", methods=['PUT'])
@jwt_required()
def update_vehicle(customer_id, vehicle_id):
    """Update a vehicle"""
    # Get current user from JWT token
    current_user_id = int(get_jwt_identity())
    
    # Users can only update vehicles on their own account
    if current_user_id != customer_id:
        return jsonify({"error": "Unauthorized to update vehicles for this customer"}), 403
    
    vehicle = db.session.get(Vehicle, vehicle_id)
    
    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404
    
    # Verify vehicle belongs to this customer
    if vehicle.customer_id != customer_id:
        return jsonify({"error": "Vehicle does not belong to this customer"}), 400
    
    # Check if request has JSON data
    if not request.json:
        return jsonify({"error": "No JSON data provided"}), 400
    
    # Add customer_id to the request data before validation
    request_data = dict(request.json)
    request_data['customer_id'] = customer_id
    
    try:
        vehicle_data = cast(Dict[str, Any], vehicle_schema.load(request_data))
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # If VIN is being changed, check if new VIN already exists
    if 'vin' in vehicle_data and vehicle_data['vin'] != vehicle.vin:
        query = select(Vehicle).where(Vehicle.vin == vehicle_data['vin'])
        existing_vehicle = db.session.execute(query).scalars().first()
        if existing_vehicle:
            return jsonify({"error": "VIN already exists in the system"}), 400
    
    # Update vehicle attributes (but don't allow changing customer_id)
    for key, value in vehicle_data.items():
        if key != 'customer_id':  # Prevent changing vehicle ownership
            setattr(vehicle, key, value)
    
    db.session.commit()
    return jsonify(vehicle_schema.dump(vehicle)), 200


# DELETE VEHICLE - DELETE /customers/<id>/vehicles/<vehicle_id>
@customer_bp.route("/<int:customer_id>/vehicles/<int:vehicle_id>", methods=['DELETE'])
@jwt_required()
def delete_vehicle(customer_id, vehicle_id):
    """Delete a vehicle"""
    # Get current user from JWT token
    current_user_id = int(get_jwt_identity())
    
    # Users can only delete vehicles from their own account
    if current_user_id != customer_id:
        return jsonify({"error": "Unauthorized to delete vehicles for this customer"}), 403
    
    vehicle = db.session.get(Vehicle, vehicle_id)
    
    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404
    
    # Verify vehicle belongs to this customer
    if vehicle.customer_id != customer_id:
        return jsonify({"error": "Vehicle does not belong to this customer"}), 400
    
    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({"message": f'Vehicle id: {vehicle_id}, successfully deleted.'}), 200
