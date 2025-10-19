"""
Database Seeding Script for Production
Run this once to populate the database with sample data
"""
from application import create_app
from application.extensions import db
from application.models import Customer, Vehicle, Mechanic, ServiceTicket, Part, TicketMechanic, TicketPart
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import os

def seed_database():
    """Seed the database with sample data"""
    config_name = os.getenv('FLASK_CONFIG', 'production')
    app = create_app(config_name)
    
    with app.app_context():
        print("Starting database seeding...")
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("Clearing existing data...")
        TicketPart.query.delete()
        TicketMechanic.query.delete()
        ServiceTicket.query.delete()
        Part.query.delete()
        Vehicle.query.delete()
        Mechanic.query.delete()
        Customer.query.delete()
        db.session.commit()
        
        # Create Customers
        print("Creating customers...")
        customers = [
            Customer(
                first_name="Alice", last_name="Johnson",
                email="alice.johnson@email.com",
                password_hash=generate_password_hash("password123"),
                phone="555-1001"
            ),
            Customer(
                first_name="Bob", last_name="Smith",
                email="bob.smith@email.com",
                password_hash=generate_password_hash("password123"),
                phone="555-1002"
            ),
            Customer(
                first_name="Carol", last_name="Williams",
                email="carol.williams@email.com",
                password_hash=generate_password_hash("password123"),
                phone="555-1003"
            ),
        ]
        db.session.add_all(customers)
        db.session.commit()
        print(f"✅ Created {len(customers)} customers")
        
        # Create Vehicles
        print("Creating vehicles...")
        vehicles = [
            Vehicle(customer_id=customers[0].customer_id, vin="1HGCM82633A123456", make="Honda", model="Accord", year=2020, color="Silver"),
            Vehicle(customer_id=customers[1].customer_id, vin="2T1BR32E25C123789", make="Toyota", model="Camry", year=2019, color="Blue"),
            Vehicle(customer_id=customers[2].customer_id, vin="3FADP4EJ7EM123456", make="Ford", model="Focus", year=2021, color="Red"),
        ]
        db.session.add_all(vehicles)
        db.session.commit()
        print(f"✅ Created {len(vehicles)} vehicles")
        
        # Create Mechanics
        print("Creating mechanics...")
        mechanics = [
            Mechanic(full_name="John Smith", email="john.smith@shop.com", phone="555-0101", salary=65000, is_active=True),
            Mechanic(full_name="Sarah Johnson", email="sarah.johnson@shop.com", phone="555-0102", salary=68000, is_active=True),
            Mechanic(full_name="Mike Wilson", email="mike.wilson@shop.com", phone="555-0103", salary=62000, is_active=True),
        ]
        db.session.add_all(mechanics)
        db.session.commit()
        print(f"✅ Created {len(mechanics)} mechanics")
        
        # Create Parts
        print("Creating parts...")
        parts = [
            Part(part_number="OIL-001", name="Engine Oil 5W-30", description="Premium synthetic oil", category="Fluids", 
                 manufacturer="Castrol", current_cost_cents=2500, quantity_in_stock=50, reorder_level=10, supplier="AutoParts Inc"),
            Part(part_number="FILTER-001", name="Oil Filter", description="Standard oil filter", category="Filters",
                 manufacturer="Fram", current_cost_cents=800, quantity_in_stock=30, reorder_level=5, supplier="AutoParts Inc"),
            Part(part_number="BRAKE-001", name="Brake Pads", description="Front brake pads", category="Brakes",
                 manufacturer="Brembo", current_cost_cents=4500, quantity_in_stock=20, reorder_level=4, supplier="Brake Supply Co"),
        ]
        db.session.add_all(parts)
        db.session.commit()
        print(f"✅ Created {len(parts)} parts")
        
        # Create Service Tickets
        print("Creating service tickets...")
        tickets = [
            ServiceTicket(
                vehicle_id=vehicles[0].vehicle_id,
                customer_id=customers[0].customer_id,
                status="completed",
                opened_at=datetime.utcnow() - timedelta(days=7),
                closed_at=datetime.utcnow() - timedelta(days=6),
                problem_description="Oil change needed",
                odometer_miles=35000,
                priority=2
            ),
            ServiceTicket(
                vehicle_id=vehicles[1].vehicle_id,
                customer_id=customers[1].customer_id,
                status="in_progress",
                opened_at=datetime.utcnow() - timedelta(days=2),
                problem_description="Brake inspection and replacement",
                odometer_miles=42000,
                priority=1
            ),
        ]
        db.session.add_all(tickets)
        db.session.commit()
        print(f"✅ Created {len(tickets)} service tickets")
        
        # Assign Mechanics to Tickets
        print("Assigning mechanics to tickets...")
        ticket_mechanics = [
            TicketMechanic(ticket_id=tickets[0].ticket_id, mechanic_id=mechanics[0].mechanic_id, role="Technician", minutes_worked=30),
            TicketMechanic(ticket_id=tickets[1].ticket_id, mechanic_id=mechanics[1].mechanic_id, role="Lead Technician", minutes_worked=45),
        ]
        db.session.add_all(ticket_mechanics)
        db.session.commit()
        print(f"✅ Assigned {len(ticket_mechanics)} mechanics to tickets")
        
        # Add Parts to Tickets
        print("Adding parts to tickets...")
        ticket_parts = [
            TicketPart(
                ticket_id=tickets[0].ticket_id,
                part_id=parts[0].part_id,
                quantity_used=1,
                unit_cost_cents=parts[0].current_cost_cents,
                markup_percentage=30.0,
                installed_date=datetime.utcnow() - timedelta(days=6),
                warranty_months=6,
                installed_by_mechanic_id=mechanics[0].mechanic_id
            ),
        ]
        db.session.add_all(ticket_parts)
        db.session.commit()
        print(f"✅ Added {len(ticket_parts)} parts to tickets")
        
        print("\n🎉 Database seeding completed successfully!")
        print(f"\nSample Login Credentials:")
        print(f"Email: alice.johnson@email.com")
        print(f"Password: password123")

if __name__ == "__main__":
    seed_database()
