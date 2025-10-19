from flask import Blueprint

# Create the auth blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Import routes to register them with the blueprint
from application.blueprints.auth import routes
