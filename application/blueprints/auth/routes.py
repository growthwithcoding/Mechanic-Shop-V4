from typing import Any, Dict, cast
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flasgger import swag_from
from application.blueprints.auth import auth_bp
from application.blueprints.auth.authSchemas import register_schema, login_schema
from application.blueprints.customer.customerSchemas import customer_schema
from application.models import Customer
from application.extensions import db, limiter


# REGISTER - POST /auth/register
# Rate limiting applied: Prevents spam account creation
@auth_bp.route("/register", methods=['POST'])
@limiter.limit("3 per hour")
def register():
    """
    Register a new customer account
    ---
    tags:
      - Authentication
    summary: Register a new customer
    description: Creates a new customer account with hashed password and returns JWT access token
    parameters:
      - in: body
        name: body
        description: Customer registration data
        required: true
        schema:
          type: object
          required:
            - first_name
            - last_name
            - email
            - password
            - phone
          properties:
            first_name:
              type: string
              example: Demo
            last_name:
              type: string
              example: User
            email:
              type: string
              format: email
              example: demo.user@email.com
            password:
              type: string
              format: password
              example: password123
            phone:
              type: string
              example: 555-9999
            address:
              type: string
              example: 123 Test St
            city:
              type: string
              example: Denver
            state:
              type: string
              example: CO
            postal_code:
              type: string
              example: 80201
    responses:
      201:
        description: Customer registered successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Customer registered successfully
            access_token:
              type: string
              example: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
            customer:
              type: object
              properties:
                customer_id:
                  type: integer
                  example: 6
                first_name:
                  type: string
                  example: Demo
                last_name:
                  type: string
                  example: User
                email:
                  type: string
                  example: demo.user@email.com
                phone:
                  type: string
                  example: 555-9999
                address:
                  type: string
                  example: 123 Test St
                city:
                  type: string
                  example: Denver
                state:
                  type: string
                  example: CO
                postal_code:
                  type: string
                  example: 80201
      400:
        description: Bad request - validation error or email already exists
        schema:
          type: object
          properties:
            error:
              type: string
              example: Email already registered
    """
    # Check if request has JSON data
    if not request.json:
        return jsonify({"error": "No JSON data provided"}), 400
    
    try:
        # Validate and deserialize input
        customer_data = cast(Dict[str, Any], register_schema.load(request.json))
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Check if email already exists
    query = select(Customer).where(Customer.email == customer_data['email'])
    existing_customer = db.session.execute(query).scalars().first()
    if existing_customer:
        return jsonify({"error": "Email already registered"}), 400
    
    # Extract password and remove from customer_data
    password = customer_data.pop('password')
    
    # Create new customer
    new_customer = Customer(**customer_data)
    new_customer.set_password(password)
    
    db.session.add(new_customer)
    db.session.commit()
    
    # Create JWT access token (identity must be a string)
    access_token = create_access_token(identity=str(new_customer.customer_id))
    
    return jsonify({
        "message": "Customer registered successfully",
        "access_token": access_token,
        "customer": customer_schema.dump(new_customer)
    }), 201


# LOGIN - POST /auth/login
# Rate limiting applied: Prevents brute force attacks
@auth_bp.route("/login", methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """
    Login with email and password
    ---
    tags:
      - Authentication
    summary: Login to get access token
    description: Authenticate with email and password to receive a JWT access token
    parameters:
      - in: body
        name: body
        description: Login credentials
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              format: email
              example: alice.johnson@email.com
            password:
              type: string
              format: password
              example: password123
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: Login successful
            access_token:
              type: string
              example: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
            customer:
              type: object
              properties:
                customer_id:
                  type: integer
                  example: 1
                first_name:
                  type: string
                  example: Alice
                last_name:
                  type: string
                  example: Johnson
                email:
                  type: string
                  example: alice.johnson@email.com
                phone:
                  type: string
                  example: 555-1001
      401:
        description: Unauthorized - invalid credentials
        schema:
          type: object
          properties:
            error:
              type: string
              example: Invalid email or password
      400:
        description: Bad request - validation error
    """
    # Check if request has JSON data
    if not request.json:
        return jsonify({"error": "No JSON data provided"}), 400
    
    try:
        # Validate and deserialize input
        login_data = cast(Dict[str, Any], login_schema.load(request.json))
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Find customer by email
    query = select(Customer).where(Customer.email == login_data['email'])
    customer = db.session.execute(query).scalars().first()
    
    # Check if customer exists and password is correct
    if not customer or not customer.check_password(login_data['password']):
        return jsonify({"error": "Invalid email or password"}), 401
    
    # Create JWT access token (identity must be a string)
    access_token = create_access_token(identity=str(customer.customer_id))
    
    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "customer": customer_schema.dump(customer)
    }), 200


# GET CURRENT USER - GET /auth/me
# JWT required: Returns the currently authenticated user's information
@auth_bp.route("/me", methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current authenticated user information
    ---
    tags:
      - Authentication
    summary: Get current user
    description: Retrieves the currently authenticated user's information using JWT token
    security:
      - Bearer: []
    responses:
      200:
        description: Current user information retrieved successfully
        schema:
          type: object
          properties:
            customer_id:
              type: integer
              example: 1
            first_name:
              type: string
              example: Alice
            last_name:
              type: string
              example: Johnson
            email:
              type: string
              example: alice.johnson@email.com
            phone:
              type: string
              example: 555-1001
      404:
        description: Customer not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: Customer not found
      401:
        description: Unauthorized - missing or invalid JWT token
    """
    # Get customer ID from JWT token (convert from string back to int)
    current_customer_id = int(get_jwt_identity())
    
    # Fetch customer from database
    customer = db.session.get(Customer, current_customer_id)
    
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    
    return customer_schema.jsonify(customer), 200
