from flask import Flask
from config import config
from application.extensions import db, ma, limiter, cache, jwt, migrate
from flasgger import Swagger


def create_app(config_name='default'):
    """
    Application Factory Pattern
    Creates and configures the Flask application instance
    
    Args:
        config_name (str): The configuration to use ('development', 'testing', 'production', 'default')
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions with app
    db.init_app(app)
    ma.init_app(app)
    
    # Configure rate limiter based on configuration
    app.config.setdefault('RATELIMIT_ENABLED', True)
    limiter.init_app(app)
    
    cache.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize Swagger
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs"
    }
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Mechanic Shop API V4",
            "description": "A comprehensive RESTful API for managing a mechanic shop, including customers, vehicles, mechanics, inventory, and service tickets",
            "version": "3.0.0",
            "contact": {
                "name": "API Support",
                "email": "support@mechanicshop.com"
            }
        },
        "host": "mechanic-shop-v4.onrender.com",
        "basePath": "/",
        "schemes": ["https"],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer {token}'"
            }
        }
    }
    
    Swagger(app, config=swagger_config, template=swagger_template)
    
    # Register blueprints
    from application.blueprints.customer import customer_bp
    from application.blueprints.auth import auth_bp
    from application.blueprints.service_ticket import service_ticket_bp
    from application.blueprints.mechanic import mechanic_bp
    from application.blueprints.inventory import inventory_bp
    
    app.register_blueprint(customer_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(service_ticket_bp)
    app.register_blueprint(mechanic_bp)
    app.register_blueprint(inventory_bp)
    
    # Register error handlers for JSON responses
    register_error_handlers(app)
    
    return app


def register_error_handlers(app):
    """
    Register error handlers to ensure all errors return JSON responses
    This is critical for API consistency - all responses must be JSON
    
    Enhanced error handling includes:
    - Comprehensive logging with request context
    - Unique error IDs for tracking
    - Environment-aware responses (detailed in dev, safe in production)
    - Categorized error types for better debugging
    """
    from flask import jsonify, request, g
    from werkzeug.exceptions import HTTPException
    from marshmallow import ValidationError
    from sqlalchemy.exc import (
        SQLAlchemyError, IntegrityError, OperationalError, 
        DataError, DatabaseError
    )
    from flask_jwt_extended import get_jwt_identity
    import logging
    import traceback
    import uuid
    from datetime import datetime
    
    # Configure logging
    logger = logging.getLogger(__name__)
    
    def get_request_context():
        """Capture request context for logging"""
        try:
            user_id = get_jwt_identity()
        except:
            user_id = None
        
        context = {
            'timestamp': datetime.utcnow().isoformat(),
            'method': request.method,
            'path': request.path,
            'endpoint': request.endpoint,
            'remote_addr': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'user_id': user_id,
        }
        
        # Add query parameters (if any)
        if request.args:
            context['query_params'] = dict(request.args)
        
        # Add request data (sanitized - avoid logging sensitive data)
        if request.is_json and request.json:
            # Create a copy to avoid modifying original
            sanitized_data = dict(request.json)
            # Remove sensitive fields
            sensitive_fields = ['password', 'token', 'secret', 'api_key']
            for field in sensitive_fields:
                if field in sanitized_data:
                    sanitized_data[field] = '***REDACTED***'
            context['request_data'] = sanitized_data
        
        return context
    
    def log_error(error_id, error_type, error, status_code, additional_info=None):
        """Log error with full context"""
        context = get_request_context()
        
        log_data = {
            'error_id': error_id,
            'error_type': error_type,
            'status_code': status_code,
            'error_message': str(error),
            'context': context
        }
        
        if additional_info:
            log_data['additional_info'] = additional_info
        
        # Log stack trace for 500 errors
        if status_code >= 500:
            log_data['traceback'] = traceback.format_exc()
        
        logger.error(f"Error {error_id}: {error_type} - {str(error)}", extra=log_data)
    
    def create_error_response(error_type, message, error_id, status_code, details=None):
        """Create standardized error response"""
        response = {
            "error": error_type,
            "message": message,
            "error_id": error_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Include details in development mode
        if app.debug and details:
            response["details"] = details
        
        return jsonify(response), status_code
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors"""
        error_id = str(uuid.uuid4())
        log_error(error_id, "Bad Request", error, 400)
        
        return create_error_response(
            "Bad Request",
            str(error.description) if hasattr(error, 'description') else "Invalid request",
            error_id,
            400
        )
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized errors"""
        error_id = str(uuid.uuid4())
        log_error(error_id, "Unauthorized", error, 401)
        
        return create_error_response(
            "Unauthorized",
            str(error.description) if hasattr(error, 'description') else "Authentication required",
            error_id,
            401
        )
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors"""
        error_id = str(uuid.uuid4())
        log_error(error_id, "Forbidden", error, 403)
        
        return create_error_response(
            "Forbidden",
            str(error.description) if hasattr(error, 'description') else "Access denied",
            error_id,
            403
        )
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors"""
        error_id = str(uuid.uuid4())
        log_error(error_id, "Not Found", error, 404)
        
        return create_error_response(
            "Not Found",
            str(error.description) if hasattr(error, 'description') else "Resource not found",
            error_id,
            404
        )
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors"""
        error_id = str(uuid.uuid4())
        log_error(error_id, "Method Not Allowed", error, 405)
        
        return create_error_response(
            "Method Not Allowed",
            str(error.description) if hasattr(error, 'description') else "HTTP method not allowed",
            error_id,
            405
        )
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error"""
        error_id = str(uuid.uuid4())
        log_error(error_id, "Internal Server Error", error, 500)
        
        # In development, provide more details
        details = None
        if app.debug:
            details = {
                "type": type(error).__name__,
                "traceback": traceback.format_exc()
            }
        
        return create_error_response(
            "Internal Server Error",
            "An internal error occurred. Please contact support with error ID: " + error_id,
            error_id,
            500,
            details
        )
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle all other HTTP exceptions"""
        error_id = str(uuid.uuid4())
        log_error(error_id, error.name, error, error.code)
        
        return create_error_response(
            error.name,
            error.description,
            error_id,
            error.code
        )
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle Marshmallow validation errors"""
        error_id = str(uuid.uuid4())
        log_error(error_id, "Validation Error", error, 400)
        
        response = {
            "error": "Validation Error",
            "message": "Request validation failed",
            "validation_errors": error.messages,
            "error_id": error_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return jsonify(response), 400
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        """Handle database integrity constraint violations"""
        error_id = str(uuid.uuid4())
        db.session.rollback()
        
        # Parse common integrity errors
        error_msg = str(error.orig) if hasattr(error, 'orig') else str(error)
        
        user_message = "Database constraint violation occurred"
        details = None
        
        if 'Duplicate entry' in error_msg:
            user_message = "A record with this information already exists"
            if app.debug:
                details = {"constraint": "unique", "message": error_msg}
        elif 'foreign key constraint' in error_msg.lower():
            user_message = "Referenced record does not exist"
            if app.debug:
                details = {"constraint": "foreign_key", "message": error_msg}
        elif app.debug:
            details = {"message": error_msg}
        
        log_error(error_id, "Database Integrity Error", error, 400, {
            "constraint_type": "integrity",
            "original_error": error_msg
        })
        
        return create_error_response(
            "Database Integrity Error",
            user_message,
            error_id,
            400,
            details
        )
    
    @app.errorhandler(OperationalError)
    def handle_operational_error(error):
        """Handle database operational errors (connection, timeouts, etc.)"""
        error_id = str(uuid.uuid4())
        db.session.rollback()
        
        error_msg = str(error.orig) if hasattr(error, 'orig') else str(error)
        
        user_message = "Database connection error"
        details = None
        
        if 'Lost connection' in error_msg or 'Can\'t connect' in error_msg:
            user_message = "Database connection lost. Please try again"
        elif 'Lock wait timeout' in error_msg or 'Deadlock' in error_msg:
            user_message = "Database is busy. Please try again"
        
        if app.debug:
            details = {"operational_error": error_msg}
        
        log_error(error_id, "Database Operational Error", error, 503, {
            "error_type": "operational",
            "original_error": error_msg
        })
        
        return create_error_response(
            "Database Operational Error",
            user_message,
            error_id,
            503,
            details
        )
    
    @app.errorhandler(DataError)
    def handle_data_error(error):
        """Handle database data errors (type mismatches, invalid values)"""
        error_id = str(uuid.uuid4())
        db.session.rollback()
        
        error_msg = str(error.orig) if hasattr(error, 'orig') else str(error)
        
        log_error(error_id, "Database Data Error", error, 400, {
            "error_type": "data",
            "original_error": error_msg
        })
        
        details = None
        if app.debug:
            details = {"data_error": error_msg}
        
        return create_error_response(
            "Database Data Error",
            "Invalid data format or type",
            error_id,
            400,
            details
        )
    
    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(error):
        """Handle all other database errors"""
        error_id = str(uuid.uuid4())
        db.session.rollback()
        
        error_msg = str(error.orig) if hasattr(error, 'orig') else str(error)
        
        log_error(error_id, "Database Error", error, 500, {
            "error_type": type(error).__name__,
            "original_error": error_msg
        })
        
        details = None
        if app.debug:
            details = {
                "type": type(error).__name__,
                "message": error_msg,
                "traceback": traceback.format_exc()
            }
        
        return create_error_response(
            "Database Error",
            "A database error occurred. Please contact support with error ID: " + error_id,
            error_id,
            500,
            details
        )
    
    @app.errorhandler(Exception)
    def handle_generic_error(error):
        """Handle all other unhandled exceptions"""
        error_id = str(uuid.uuid4())
        
        log_error(error_id, "Unhandled Exception", error, 500, {
            "exception_type": type(error).__name__
        })
        
        details = None
        if app.debug:
            details = {
                "type": type(error).__name__,
                "message": str(error),
                "traceback": traceback.format_exc()
            }
        
        return create_error_response(
            "Internal Server Error",
            "An unexpected error occurred. Please contact support with error ID: " + error_id,
            error_id,
            500,
            details
        )
