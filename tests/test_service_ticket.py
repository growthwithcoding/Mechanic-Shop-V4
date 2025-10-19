import unittest
import json
from application import create_app
from application.extensions import db
from application.models import Customer, Mechanic, Vehicle, ServiceTicket, Part


class TestServiceTicketRoutes(unittest.TestCase):
    """Test cases for Service Ticket routes"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test client and application context once for all tests"""
        cls.app = create_app('testing')
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
    @classmethod
    def tearDownClass(cls):
        """Clean up application context"""
        cls.app_context.pop()
    
    def setUp(self):
        """Set up test database and auth token before each test"""
        db.create_all()
        
        # Create a test customer and get auth token
        register_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "password": "TestPass123!",
            "phone": "555-000-0000"
        }
        response = self.client.post(
            '/auth/register',
            data=json.dumps(register_data),
            content_type='application/json'
        )
        response_data = json.loads(response.data)
        self.token = response_data['access_token']
        self.customer_id = response_data['customer']['customer_id']
        self.headers = {'Authorization': f'Bearer {self.token}'}
        
        # Create a test vehicle
        vehicle_data = {
            "vin": "1HGCM82633A123456",
            "make": "Honda",
            "model": "Accord",
            "year": 2020,
            "color": "Blue",
            "mileage": 25000
        }
        vehicle_response = self.client.post(
            f'/customers/{self.customer_id}/vehicles',
            data=json.dumps(vehicle_data),
            content_type='application/json',
            headers=self.headers
        )
        self.vehicle_id = json.loads(vehicle_response.data)['vehicle_id']
        
        # Create a test mechanic
        mechanic_data = {
            "first_name": "Mike",
            "last_name": "Mechanic",
            "email": "mike@mechanicshop.com",
            "phone": "555-111-2222",
            "salary": 50000.00,
            "is_active": True
        }
        mechanic_response = self.client.post(
            '/mechanics',
            data=json.dumps(mechanic_data),
            content_type='application/json',
            headers=self.headers
        )
        self.mechanic_id = json.loads(mechanic_response.data)['mechanic_id']
        
        # Create a test part
        part_data = {
            "part_number": "BRK-001",
            "name": "Brake Pad Set",
            "description": "Front brake pads",
            "category": "Brakes",
            "current_cost_cents": 4500,
            "quantity_in_stock": 25,
            "reorder_threshold": 5
        }
        part_response = self.client.post(
            '/inventory',
            data=json.dumps(part_data),
            content_type='application/json',
            headers=self.headers
        )
        self.part_id = json.loads(part_response.data)['part_id']
        
    def tearDown(self):
        """Clean up test database after each test"""
        db.session.remove()
        db.drop_all()
    
    # ===== CREATE SERVICE TICKET TESTS =====
    
    def test_create_service_ticket_success(self):
        """Test creating a service ticket"""
        ticket_data = {
            "vehicle_id": self.vehicle_id,
            "customer_id": self.customer_id,
            "description": "Oil change and brake inspection",
            "status": "Open"
        }
        
        response = self.client.post(
            '/service_tickets',
            data=json.dumps(ticket_data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 201)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['description'], 'Oil change and brake inspection')
        self.assertEqual(json_data['status'], 'Open')
    
    def test_create_service_ticket_missing_fields(self):
        """Test creating ticket with missing required fields (negative test)"""
        ticket_data = {
            "description": "Oil change"
            # Missing vehicle_id and customer_id
        }
        
        response = self.client.post(
            '/service_tickets',
            data=json.dumps(ticket_data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_create_service_ticket_no_auth(self):
        """Test creating ticket without authentication (negative test)"""
        ticket_data = {
            "vehicle_id": self.vehicle_id,
            "customer_id": self.customer_id,
            "description": "Oil change",
            "status": "Open"
        }
        
        response = self.client.post(
            '/service_tickets',
            data=json.dumps(ticket_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
    
    # ===== GET ALL SERVICE TICKETS TESTS =====
    
    def test_get_all_service_tickets_success(self):
        """Test getting all service tickets"""
        # Create a test ticket
        ticket_data = {
            "vehicle_id": self.vehicle_id,
            "customer_id": self.customer_id,
            "description": "Oil change",
            "status": "Open"
        }
        self.client.post(
            '/service_tickets',
            data=json.dumps(ticket_data),
            content_type='application/json',
            headers=self.headers
        )
        
        response = self.client.get('/service_tickets', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertIsInstance(json_data, list)
        self.assertGreaterEqual(len(json_data), 1)
    
    def test_get_all_service_tickets_no_auth(self):
        """Test getting tickets without authentication (negative test)"""
        response = self.client.get('/service_tickets')
        
        self.assertEqual(response.status_code, 401)
    
    # ===== GET ONE SERVICE TICKET TESTS =====
    
    def test_get_service_ticket_success(self):
        """Test getting a specific service ticket"""
        # Create a ticket
        ticket_data = {
            "vehicle_id": self.vehicle_id,
            "customer_id": self.customer_id,
            "description": "Oil change",
            "status": "Open"
        }
        create_response = self.client.post(
            '/service_tickets',
            data=json.dumps(ticket_data),
            content_type='application/json',
            headers=self.headers
        )
        ticket_id = json.loads(create_response.data)['ticket_id']
        
        response = self.client.get(f'/service_tickets/{ticket_id}', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['ticket_id'], ticket_id)
    
    def test_get_service_ticket_not_found(self):
        """Test getting non-existent ticket (negative test)"""
        response = self.client.get('/service_tickets/9999', headers=self.headers)
        
        self.assertEqual(response.status_code, 404)
    
    def test_get_service_ticket_no_auth(self):
        """Test getting ticket without authentication (negative test)"""
        response = self.client.get('/service_tickets/1')
        
        self.assertEqual(response.status_code, 401)
    
    # ===== UPDATE SERVICE TICKET TESTS =====
    
    def test_update_service_ticket_success(self):
        """Test updating a service ticket"""
        # Create a ticket
        ticket_data = {
            "vehicle_id": self.vehicle_id,
            "customer_id": self.customer_id,
            "description": "Oil change",
            "status": "Open"
        }
        create_response = self.client.post(
            '/service_tickets',
            data=json.dumps(ticket_data),
            content_type='application/json',
            headers=self.headers
        )
        ticket_id = json.loads(create_response.data)['ticket_id']
        
        # Update ticket
        update_data = {
            "vehicle_id": self.vehicle_id,
            "customer_id": self.customer_id,
            "description": "Oil change and brake inspection",
            "status": "In Progress"
        }
        
        response = self.client.put(
            f'/service_tickets/{ticket_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['status'], 'In Progress')
    
    def test_update_service_ticket_not_found(self):
        """Test updating non-existent ticket (negative test)"""
        update_data = {
            "vehicle_id": self.vehicle_id,
            "customer_id": self.customer_id,
            "description": "Oil change",
            "status": "Open"
        }
        
        response = self.client.put(
            '/service_tickets/9999',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_update_service_ticket_no_auth(self):
        """Test updating ticket without authentication (negative test)"""
        update_data = {
            "vehicle_id": self.vehicle_id,
            "customer_id": self.customer_id,
            "description": "Oil change",
            "status": "Open"
        }
        
        response = self.client.put(
            '/service_tickets/1',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
    
    # ===== DELETE SERVICE TICKET TESTS =====
    
    def test_delete_service_ticket_success(self):
        """Test deleting a service ticket"""
        # Create a ticket
        ticket_data = {
            "vehicle_id": self.vehicle_id,
            "customer_id": self.customer_id,
            "description": "Oil change",
            "status": "Open"
        }
        create_response = self.client.post(
            '/service_tickets',
            data=json.dumps(ticket_data),
            content_type='application/json',
            headers=self.headers
        )
        ticket_id = json.loads(create_response.data)['ticket_id']
        
        response = self.client.delete(f'/service_tickets/{ticket_id}', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertIn('message', json_data)
    
    def test_delete_service_ticket_not_found(self):
        """Test deleting non-existent ticket (negative test)"""
        response = self.client.delete('/service_tickets/9999', headers=self.headers)
        
        self.assertEqual(response.status_code, 404)
    
    def test_delete_service_ticket_no_auth(self):
        """Test deleting ticket without authentication (negative test)"""
        response = self.client.delete('/service_tickets/1')
        
        self.assertEqual(response.status_code, 401)
    
    # ===== ASSIGN MECHANIC TESTS =====
    
    def test_assign_mechanic_success(self):
        """Test assigning a mechanic to a ticket"""
        # Create a ticket
        ticket_data = {
            "vehicle_id": self.vehicle_id,
            "customer_id": self.customer_id,
            "description": "Oil change",
            "status": "Open"
        }
        create_response = self.client.post(
            '/service_tickets',
            data=json.dumps(ticket_data),
            content_type='application/json',
            headers=self.headers
        )
        ticket_id = json.loads(create_response.data)['ticket_id']
        
        # Assign mechanic
        response = self.client.put(
            f'/service_tickets/{ticket_id}/assign-mechanic/{self.mechanic_id}',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertIn('message', json_data)
    
    def test_assign_mechanic_duplicate(self):
        """Test assigning same mechanic twice (negative test)"""
        # Create a ticket
        ticket_data = {
            "vehicle_id": self.vehicle_id,
            "customer_id": self.customer_id,
            "description": "Oil change",
            "status": "Open"
        }
        create_response = self.client.post(
            '/service_tickets',
            data=json.dumps(ticket_data),
            content_type='application/json',
            headers=self.headers
        )
        ticket_id = json.loads(create_response.data)['ticket_id']
        
        # Assign mechanic first time
        self.client.put(
            f'/service_tickets/{ticket_id}/assign-mechanic/{self.mechanic_id}',
            headers=self.headers
        )
        
        # Try to assign same mechanic again
        response = self.client.put(
            f'/service_tickets/{ticket_id}/assign-mechanic/{self.mechanic_id}',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_assign_mechanic_not_found(self):
        """Test assigning non-existent mechanic (negative test)"""
        # Create a ticket
        ticket_data = {
            "vehicle_id": self.vehicle_id,
            "customer_id": self.customer_id,
            "description": "Oil change",
            "status": "Open"
        }
        create_response = self.client.post(
            '/service_tickets',
            data=json.dumps(ticket_data),
            content_type='application/json',
            headers=self.headers
        )
        ticket_id = json.loads(create_response.data)['ticket_id']
        
        response = self.client.put(
            f'/service_tickets/{ticket_id}/assign-mechanic/9999',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_assign_mechanic_no_auth(self):
        """Test assigning mechanic without authentication (negative test)"""
        response = self.client.put(
            f'/service_tickets/1/assign-mechanic/{self.mechanic_id}'
        )
        
        self.assertEqual(response.status_code, 401)
    
    # ===== REMOVE MECHANIC TESTS =====
    
    def test_remove_mechanic_success(self):
        """Test removing a mechanic from a ticket"""
        # Create a ticket and assign mechanic
        ticket_data = {
            "vehicle_id": self.vehicle_id,
            "customer_id": self.customer_id,
            "description": "Oil change",
            "status": "Open"
        }
        create_response = self.client.post(
            '/service_tickets',
            data=json.dumps(ticket_data),
            content_type='application/json',
            headers=self.headers
        )
        ticket_id = json.loads(create_response.data)['ticket_id']
        
        self.client.put(
            f'/service_tickets/{ticket_id}/assign-mechanic/{self.mechanic_id}',
            headers=self.headers
        )
        
        # Remove mechanic
        response = self.client.put(
            f'/service_tickets/{ticket_id}/remove-mechanic/{self.mechanic_id}',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertIn('message', json_data)
    
    def test_remove_mechanic_not_assigned(self):
        """Test removing mechanic that's not assigned (negative test)"""
        # Create a ticket
        ticket_data = {
            "vehicle_id": self.vehicle_id,
            "customer_id": self.customer_id,
            "description": "Oil change",
            "status": "Open"
        }
        create_response = self.client.post(
            '/service_tickets',
            data=json.dumps(ticket_data),
            content_type='application/json',
            headers=self.headers
        )
        ticket_id = json.loads(create_response.data)['ticket_id']
        
        # Try to remove mechanic that wasn't assigned
        response = self.client.put(
            f'/service_tickets/{ticket_id}/remove-mechanic/{self.mechanic_id}',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_remove_mechanic_no_auth(self):
        """Test removing mechanic without authentication (negative test)"""
        response = self.client.put(
            f'/service_tickets/1/remove-mechanic/{self.mechanic_id}'
        )
        
        self.assertEqual(response.status_code, 401)
    
    # ===== ADD PART TO TICKET TESTS =====
    
    def test_add_part_to_ticket_success(self):
        """Test adding a part to a ticket"""
        # Create a ticket
        ticket_data = {
            "vehicle_id": self.vehicle_id,
            "customer_id": self.customer_id,
            "description": "Brake replacement",
            "status": "Open"
        }
        create_response = self.client.post(
            '/service_tickets',
            data=json.dumps(ticket_data),
            content_type='application/json',
            headers=self.headers
        )
        ticket_id = json.loads(create_response.data)['ticket_id']
        
        # Add part
        part_data = {
            "quantity_used": 2,
            "markup_percentage": 30.0
        }
        
        response = self.client.post(
            f'/service_tickets/{ticket_id}/parts/{self.part_id}',
            data=json.dumps(part_data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertIn('message', json_data)
        self.assertEqual(json_data['quantity_used'], 2)
    
    def test_add_part_insufficient_stock(self):
        """Test adding part with insufficient stock (negative test)"""
        # Create a ticket
        ticket_data = {
            "vehicle_id": self.vehicle_id,
            "customer_id": self.customer_id,
            "description": "Brake replacement",
            "status": "Open"
        }
        create_response = self.client.post(
            '/service_tickets',
            data=json.dumps(ticket_data),
            content_type='application/json',
            headers=self.headers
        )
        ticket_id = json.loads(create_response.data)['ticket_id']
        
        # Try to add more parts than available
        part_data = {
            "quantity_used": 100,  # More than the 25 in stock
            "markup_percentage": 30.0
        }
        
        response = self.client.post(
            f'/service_tickets/{ticket_id}/parts/{self.part_id}',
            data=json.dumps(part_data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_add_part_missing_quantity(self):
        """Test adding part without quantity (negative test)"""
        # Create a ticket
        ticket_data = {
            "vehicle_id": self.vehicle_id,
            "customer_id": self.customer_id,
            "description": "Brake replacement",
            "status": "Open"
        }
        create_response = self.client.post(
            '/service_tickets',
            data=json.dumps(ticket_data),
            content_type='application/json',
            headers=self.headers
        )
        ticket_id = json.loads(create_response.data)['ticket_id']
        
        # Try to add part without quantity
        part_data = {
            "markup_percentage": 30.0
        }
        
        response = self.client.post(
            f'/service_tickets/{ticket_id}/parts/{self.part_id}',
            data=json.dumps(part_data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_add_part_no_auth(self):
        """Test adding part without authentication (negative test)"""
        part_data = {
            "quantity_used": 2,
            "markup_percentage": 30.0
        }
        
        response = self.client.post(
            f'/service_tickets/1/parts/{self.part_id}',
            data=json.dumps(part_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
    
    # ===== EDIT TICKET MECHANICS TESTS =====
    
    def test_edit_ticket_mechanics_add(self):
        """Test adding mechanics using edit endpoint"""
        # Create a ticket
        ticket_data = {
            "vehicle_id": self.vehicle_id,
            "customer_id": self.customer_id,
            "description": "Oil change",
            "status": "Open"
        }
        create_response = self.client.post(
            '/service_tickets',
            data=json.dumps(ticket_data),
            content_type='application/json',
            headers=self.headers
        )
        ticket_id = json.loads(create_response.data)['ticket_id']
        
        # Add mechanics
        edit_data = {
            "add_ids": [self.mechanic_id],
            "remove_ids": [],
            "role": "Lead Technician"
        }
        
        response = self.client.put(
            f'/service_tickets/{ticket_id}/edit',
            data=json.dumps(edit_data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertIn('added_mechanics', json_data)
        self.assertIn(self.mechanic_id, json_data['added_mechanics'])
    
    def test_edit_ticket_mechanics_remove(self):
        """Test removing mechanics using edit endpoint"""
        # Create a ticket and assign mechanic
        ticket_data = {
            "vehicle_id": self.vehicle_id,
            "customer_id": self.customer_id,
            "description": "Oil change",
            "status": "Open"
        }
        create_response = self.client.post(
            '/service_tickets',
            data=json.dumps(ticket_data),
            content_type='application/json',
            headers=self.headers
        )
        ticket_id = json.loads(create_response.data)['ticket_id']
        
        self.client.put(
            f'/service_tickets/{ticket_id}/assign-mechanic/{self.mechanic_id}',
            headers=self.headers
        )
        
        # Remove mechanics
        edit_data = {
            "add_ids": [],
            "remove_ids": [self.mechanic_id]
        }
        
        response = self.client.put(
            f'/service_tickets/{ticket_id}/edit',
            data=json.dumps(edit_data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertIn('removed_mechanics', json_data)
        self.assertIn(self.mechanic_id, json_data['removed_mechanics'])
    
    def test_edit_ticket_mechanics_no_auth(self):
        """Test editing ticket mechanics without auth (negative test)"""
        edit_data = {
            "add_ids": [self.mechanic_id],
            "remove_ids": []
        }
        
        response = self.client.put(
            '/service_tickets/1/edit',
            data=json.dumps(edit_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
