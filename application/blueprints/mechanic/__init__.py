from flask import Blueprint

mechanic_bp = Blueprint('mechanic', __name__, url_prefix='/mechanics')

from application.blueprints.mechanic import routes
