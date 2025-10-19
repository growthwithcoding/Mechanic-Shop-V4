from flask import Blueprint

service_ticket_bp = Blueprint('service_ticket', __name__, url_prefix='/service_tickets')

from application.blueprints.service_ticket import routes
