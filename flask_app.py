from application import create_app
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the configuration name from environment variable or use 'default'
config_name = os.getenv('FLASK_CONFIG', 'default')

# Create the Flask app instance using the Application Factory Pattern
app = create_app(config_name)

# Run database migrations automatically on startup (production only)
if config_name == 'production':
    with app.app_context():
        from flask_migrate import upgrade
        try:
            upgrade()
            print("✅ Database migrations applied successfully")
        except Exception as e:
            print(f"⚠️ Migration error (might be already up to date): {e}")

# Add a simple health check / status route at root
@app.route('/')
def health_check():
    """
    Health check endpoint - confirms the API is running
    Returns basic status information
    """
    return {
        "status": "online",
        "message": "Mechanic Shop API V4 is running",
        "api_documentation": "/apidocs",
        "endpoints": {
            "auth": "/auth",
            "customers": "/customers",
            "mechanics": "/mechanics",
            "service_tickets": "/service-tickets",
            "inventory": "/inventory"
        }
    }, 200

@app.route('/admin/seed-database', methods=['POST'])
def seed_database_endpoint():
    """
    ONE-TIME USE: Seeds the database with sample data from JSON file
    Call this once after deployment to populate the database
    """
    import json
    from application.extensions import db
    from application.models import Customer, Vehicle, Mechanic, ServiceTicket, Part, TicketMechanic, TicketPart
    from werkzeug.security import generate_password_hash
    from datetime import datetime, timedelta
    
    try:
        # Check if data already exists
        if Customer.query.first():
            return {"message": "Database already has data. Skipping seed."}, 200
        
        # Load seed data from JSON file
        with open('seed_data.json', 'r') as f:
            seed_data = json.load(f)
        
        # Create Customers
        customers = []
        for cust_data in seed_data['customers']:
            customer = Customer()
            customer.first_name = cust_data['first_name']
            customer.last_name = cust_data['last_name']
            customer.email = cust_data['email']
            customer.phone = cust_data['phone']
            customer.address = cust_data['address']
            customer.city = cust_data['city']
            customer.state = cust_data['state']
            customer.postal_code = cust_data['postal_code']
            customer.password_hash = generate_password_hash(cust_data['password'])
            customers.append(customer)
        db.session.add_all(customers)
        db.session.commit()
        
        # Create Vehicles
        vehicles = []
        for veh_data in seed_data['vehicles']:
            vehicle = Vehicle()
            vehicle.customer_id = customers[veh_data['customer_index']].customer_id
            vehicle.vin = veh_data['vin']
            vehicle.make = veh_data['make']
            vehicle.model = veh_data['model']
            vehicle.year = veh_data['year']
            vehicle.color = veh_data['color']
            vehicles.append(vehicle)
        db.session.add_all(vehicles)
        db.session.commit()
        
        # Create Mechanics
        mechanics = []
        for mech_data in seed_data['mechanics']:
            mechanic = Mechanic()
            mechanic.full_name = mech_data['full_name']
            mechanic.email = mech_data['email']
            mechanic.phone = mech_data['phone']
            mechanic.salary = mech_data['salary']
            mechanic.is_active = mech_data['is_active']
            mechanics.append(mechanic)
        db.session.add_all(mechanics)
        db.session.commit()
        
        # Create Parts
        parts = []
        for part_data in seed_data['parts']:
            part = Part()
            part.part_number = part_data['part_number']
            part.name = part_data['name']
            part.description = part_data['description']
            part.category = part_data['category']
            part.manufacturer = part_data['manufacturer']
            part.current_cost_cents = part_data['current_cost_cents']
            part.quantity_in_stock = part_data['quantity_in_stock']
            part.reorder_level = part_data['reorder_level']
            part.supplier = part_data['supplier']
            parts.append(part)
        db.session.add_all(parts)
        db.session.commit()
        
        # Create Service Tickets
        tickets = []
        for ticket_data in seed_data['service_tickets']:
            ticket = ServiceTicket()
            ticket.vehicle_id = vehicles[ticket_data['vehicle_index']].vehicle_id
            ticket.customer_id = customers[ticket_data['customer_index']].customer_id
            ticket.status = ticket_data['status']
            ticket.opened_at = datetime.utcnow() - timedelta(days=ticket_data['days_ago_opened'])
            if 'days_ago_closed' in ticket_data:
                ticket.closed_at = datetime.utcnow() - timedelta(days=ticket_data['days_ago_closed'])
            ticket.problem_description = ticket_data['problem_description']
            ticket.odometer_miles = ticket_data['odometer_miles']
            ticket.priority = ticket_data['priority']
            tickets.append(ticket)
        db.session.add_all(tickets)
        db.session.commit()
        
        # Assign Mechanics to Tickets
        ticket_mechanics = []
        for tm_data in seed_data['ticket_mechanics']:
            tm = TicketMechanic()
            tm.ticket_id = tickets[tm_data['ticket_index']].ticket_id
            tm.mechanic_id = mechanics[tm_data['mechanic_index']].mechanic_id
            tm.role = tm_data['role']
            tm.minutes_worked = tm_data['minutes_worked']
            ticket_mechanics.append(tm)
        db.session.add_all(ticket_mechanics)
        db.session.commit()
        
        # Add Parts to Tickets
        ticket_parts = []
        for tp_data in seed_data['ticket_parts']:
            tp = TicketPart()
            tp.ticket_id = tickets[tp_data['ticket_index']].ticket_id
            tp.part_id = parts[tp_data['part_index']].part_id
            tp.quantity_used = tp_data['quantity_used']
            tp.unit_cost_cents = parts[tp_data['part_index']].current_cost_cents
            tp.markup_percentage = tp_data['markup_percentage']
            tp.installed_date = datetime.utcnow() - timedelta(days=tp_data['days_ago_installed'])
            tp.warranty_months = tp_data['warranty_months']
            tp.installed_by_mechanic_id = mechanics[tp_data['installed_by_mechanic_index']].mechanic_id
            ticket_parts.append(tp)
        db.session.add_all(ticket_parts)
        db.session.commit()
        
        return {
            "message": "Database seeded successfully!",
            "sample_credentials": {
                "email": "alice.johnson@email.com",
                "password": "password123"
            },
            "data_created": {
                "customers": len(customers),
                "vehicles": len(vehicles),
                "mechanics": len(mechanics),
                "parts": len(parts),
                "tickets": len(tickets)
            }
        }, 201
    
    except Exception as e:
        db.session.rollback()
        return {"error": f"Seeding failed: {str(e)}"}, 500

# Note: app.run() is removed for production deployment
# For local development, use: flask run
# For production, gunicorn will handle running the app
