import unittest
import json
from application import create_app
from application.extensions import db
from application.models import Customer, Vehicle


class TestCustomerRoutes(unittest.TestCase):
    """Test cases for Customer routes"""
    
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
        
    def tearDown(self):
        """Clean up test database after each test"""
        db.session.remove()
        db.drop_all()
    
    # ===== GET ALL CUSTOMERS TESTS =====
    
    def test_get_customers_success(self):
        """Test getting all customers with pagination"""
        response = self.client.get('/customers', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertIn('customers', json_data)
        self.assertIn('pagination', json_data)
        self.assertGreaterEqual(len(json_data['customers']), 1)
    
    def test_get_customers_pagination(self):
        """Test customer pagination"""
        response = self.client.get('/customers?page=1&per_page=5', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['pagination']['page'], 1)
        self.assertEqual(json_data['pagination']['per_page'], 5)
    
    def test_get_customers_invalid_page(self):
        """Test getting customers with invalid page (negative test)"""
        response = self.client.get('/customers?page=0', headers=self.headers)
        
        self.assertEqual(response.status_code, 400)
    
    def test_get_customers_no_auth(self):
        """Test getting customers without authentication (negative test)"""
        response = self.client.get('/customers')
        
        self.assertEqual(response.status_code, 401)
    
    # ===== GET ONE CUSTOMER TESTS =====
    
    def test_get_customer_success(self):
        """Test getting a specific customer"""
        response = self.client.get(f'/customers/{self.customer_id}', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['customer_id'], self.customer_id)
        self.assertEqual(json_data['email'], 'test@example.com')
    
    def test_get_customer_not_found(self):
        """Test getting non-existent customer (negative test)"""
        response = self.client.get('/customers/9999', headers=self.headers)
        
        self.assertEqual(response.status_code, 404)
        json_data = json.loads(response.data)
        self.assertIn('error', json_data)
    
    def test_get_customer_no_auth(self):
        """Test getting customer without authentication (negative test)"""
        response = self.client.get(f'/customers/{self.customer_id}')
        
        self.assertEqual(response.status_code, 401)
    
    # ===== UPDATE CUSTOMER TESTS =====
    
    def test_update_customer_success(self):
        """Test updating own customer information"""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "email": "test@example.com",
            "phone": "555-999-9999"
        }
        
        response = self.client.put(
            f'/customers/{self.customer_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['first_name'], 'Updated')
        self.assertEqual(json_data['phone'], '555-999-9999')
    
    def test_update_customer_unauthorized(self):
        """Test updating another customer's information (negative test)"""
        # Create another customer
        other_data = {
            "first_name": "Other",
            "last_name": "User",
            "email": "other@example.com",
            "password": "OtherPass123!",
            "phone": "555-111-1111"
        }
        other_response = self.client.post(
            '/auth/register',
            data=json.dumps(other_data),
            content_type='application/json'
        )
        other_id = json.loads(other_response.data)['customer']['customer_id']
        
        # Try to update other customer with current token
        update_data = {
            "first_name": "Hacker",
            "last_name": "Attempt",
            "email": "other@example.com",
            "phone": "555-111-1111"
        }
        
        response = self.client.put(
            f'/customers/{other_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 403)
    
    def test_update_customer_not_found(self):
        """Test updating non-existent customer (negative test)"""
        update_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "phone": "555-000-0000"
        }
        
        response = self.client.put(
            '/customers/9999',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 403)  # Unauthorized before not found check
    
    def test_update_customer_no_auth(self):
        """Test updating customer without authentication (negative test)"""
        update_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "phone": "555-000-0000"
        }
        
        response = self.client.put(
            f'/customers/{self.customer_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
    
    # ===== DELETE CUSTOMER TESTS =====
    
    def test_delete_customer_success(self):
        """Test deleting own customer account"""
        response = self.client.delete(f'/customers/{self.customer_id}', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertIn('message', json_data)
        
        # Verify deletion
        get_response = self.client.get(f'/customers/{self.customer_id}', headers=self.headers)
        self.assertEqual(get_response.status_code, 404)
    
    def test_delete_customer_unauthorized(self):
        """Test deleting another customer's account (negative test)"""
        # Create another customer
        other_data = {
            "first_name": "Other",
            "last_name": "User",
            "email": "other@example.com",
            "password": "OtherPass123!",
            "phone": "555-111-1111"
        }
        other_response = self.client.post(
            '/auth/register',
            data=json.dumps(other_data),
            content_type='application/json'
        )
        other_id = json.loads(other_response.data)['customer']['customer_id']
        
        # Try to delete other customer with current token
        response = self.client.delete(f'/customers/{other_id}', headers=self.headers)
        
        self.assertEqual(response.status_code, 403)
    
    def test_delete_customer_no_auth(self):
        """Test deleting customer without authentication (negative test)"""
        response = self.client.delete(f'/customers/{self.customer_id}')
        
        self.assertEqual(response.status_code, 401)
    
    # ===== CREATE VEHICLE TESTS =====
    
    def test_create_vehicle_success(self):
        """Test creating a vehicle for customer"""
        vehicle_data = {
            "vin": "1HGCM82633A123456",
            "make": "Honda",
            "model": "Accord",
            "year": 2020,
            "color": "Blue",
            "mileage": 25000
        }
        
        response = self.client.post(
            f'/customers/{self.customer_id}/vehicles',
            data=json.dumps(vehicle_data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 201)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['vin'], '1HGCM82633A123456')
        self.assertEqual(json_data['make'], 'Honda')
    
    def test_create_vehicle_duplicate_vin(self):
        """Test creating vehicle with duplicate VIN (negative test)"""
        vehicle_data = {
            "vin": "1HGCM82633A123456",
            "make": "Honda",
            "model": "Accord",
            "year": 2020,
            "color": "Blue",
            "mileage": 25000
        }
        
        # Create first vehicle
        self.client.post(
            f'/customers/{self.customer_id}/vehicles',
            data=json.dumps(vehicle_data),
            content_type='application/json',
            headers=self.headers
        )
        
        # Try to create duplicate
        response = self.client.post(
            f'/customers/{self.customer_id}/vehicles',
            data=json.dumps(vehicle_data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_create_vehicle_unauthorized(self):
        """Test creating vehicle for another customer (negative test)"""
        # Create another customer
        other_data = {
            "first_name": "Other",
            "last_name": "User",
            "email": "other@example.com",
            "password": "OtherPass123!",
            "phone": "555-111-1111"
        }
        other_response = self.client.post(
            '/auth/register',
            data=json.dumps(other_data),
            content_type='application/json'
        )
        other_id = json.loads(other_response.data)['customer']['customer_id']
        
        vehicle_data = {
            "vin": "1HGCM82633A123456",
            "make": "Honda",
            "model": "Accord",
            "year": 2020,
            "color": "Blue",
            "mileage": 25000
        }
        
        response = self.client.post(
            f'/customers/{other_id}/vehicles',
            data=json.dumps(vehicle_data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 403)
    
    def test_create_vehicle_no_auth(self):
        """Test creating vehicle without authentication (negative test)"""
        vehicle_data = {
            "vin": "1HGCM82633A123456",
            "make": "Honda",
            "model": "Accord",
            "year": 2020,
            "color": "Blue",
            "mileage": 25000
        }
        
        response = self.client.post(
            f'/customers/{self.customer_id}/vehicles',
            data=json.dumps(vehicle_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
    
    # ===== GET CUSTOMER VEHICLES TESTS =====
    
    def test_get_customer_vehicles_success(self):
        """Test getting all vehicles for a customer"""
        # Create a vehicle first
        vehicle_data = {
            "vin": "1HGCM82633A123456",
            "make": "Honda",
            "model": "Accord",
            "year": 2020,
            "color": "Blue",
            "mileage": 25000
        }
        self.client.post(
            f'/customers/{self.customer_id}/vehicles',
            data=json.dumps(vehicle_data),
            content_type='application/json',
            headers=self.headers
        )
        
        response = self.client.get(
            f'/customers/{self.customer_id}/vehicles',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertIsInstance(json_data, list)
        self.assertGreaterEqual(len(json_data), 1)
    
    def test_get_customer_vehicles_not_found(self):
        """Test getting vehicles for non-existent customer (negative test)"""
        response = self.client.get('/customers/9999/vehicles', headers=self.headers)
        
        self.assertEqual(response.status_code, 404)
    
    def test_get_customer_vehicles_no_auth(self):
        """Test getting customer vehicles without auth (negative test)"""
        response = self.client.get(f'/customers/{self.customer_id}/vehicles')
        
        self.assertEqual(response.status_code, 401)
    
    # ===== UPDATE VEHICLE TESTS =====
    
    def test_update_vehicle_success(self):
        """Test updating a vehicle"""
        # Create a vehicle first
        vehicle_data = {
            "vin": "1HGCM82633A123456",
            "make": "Honda",
            "model": "Accord",
            "year": 2020,
            "color": "Blue",
            "mileage": 25000
        }
        create_response = self.client.post(
            f'/customers/{self.customer_id}/vehicles',
            data=json.dumps(vehicle_data),
            content_type='application/json',
            headers=self.headers
        )
        vehicle_id = json.loads(create_response.data)['vehicle_id']
        
        # Update vehicle
        update_data = {
            "vin": "1HGCM82633A123456",
            "make": "Honda",
            "model": "Accord",
            "year": 2020,
            "color": "Red",
            "mileage": 30000
        }
        
        response = self.client.put(
            f'/customers/{self.customer_id}/vehicles/{vehicle_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['color'], 'Red')
        self.assertEqual(json_data['mileage'], 30000)
    
    def test_update_vehicle_unauthorized(self):
        """Test updating vehicle of another customer (negative test)"""
        # Create vehicle
        vehicle_data = {
            "vin": "1HGCM82633A123456",
            "make": "Honda",
            "model": "Accord",
            "year": 2020,
            "color": "Blue",
            "mileage": 25000
        }
        create_response = self.client.post(
            f'/customers/{self.customer_id}/vehicles',
            data=json.dumps(vehicle_data),
            content_type='application/json',
            headers=self.headers
        )
        vehicle_id = json.loads(create_response.data)['vehicle_id']
        
        # Create another customer
        other_data = {
            "first_name": "Other",
            "last_name": "User",
            "email": "other@example.com",
            "password": "OtherPass123!",
            "phone": "555-111-1111"
        }
        other_response = self.client.post(
            '/auth/register',
            data=json.dumps(other_data),
            content_type='application/json'
        )
        other_token = json.loads(other_response.data)['access_token']
        other_headers = {'Authorization': f'Bearer {other_token}'}
        
        # Try to update first customer's vehicle with other customer's token
        update_data = {
            "vin": "1HGCM82633A123456",
            "make": "Honda",
            "model": "Accord",
            "year": 2020,
            "color": "Red",
            "mileage": 30000
        }
        
        response = self.client.put(
            f'/customers/{self.customer_id}/vehicles/{vehicle_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=other_headers
        )
        
        self.assertEqual(response.status_code, 403)
    
    def test_update_vehicle_no_auth(self):
        """Test updating vehicle without authentication (negative test)"""
        # Create vehicle
        vehicle_data = {
            "vin": "1HGCM82633A123456",
            "make": "Honda",
            "model": "Accord",
            "year": 2020,
            "color": "Blue",
            "mileage": 25000
        }
        create_response = self.client.post(
            f'/customers/{self.customer_id}/vehicles',
            data=json.dumps(vehicle_data),
            content_type='application/json',
            headers=self.headers
        )
        vehicle_id = json.loads(create_response.data)['vehicle_id']
        
        update_data = {
            "vin": "1HGCM82633A123456",
            "make": "Honda",
            "model": "Accord",
            "year": 2020,
            "color": "Red",
            "mileage": 30000
        }
        
        response = self.client.put(
            f'/customers/{self.customer_id}/vehicles/{vehicle_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
    
    # ===== DELETE VEHICLE TESTS =====
    
    def test_delete_vehicle_success(self):
        """Test deleting a vehicle"""
        # Create vehicle
        vehicle_data = {
            "vin": "1HGCM82633A123456",
            "make": "Honda",
            "model": "Accord",
            "year": 2020,
            "color": "Blue",
            "mileage": 25000
        }
        create_response = self.client.post(
            f'/customers/{self.customer_id}/vehicles',
            data=json.dumps(vehicle_data),
            content_type='application/json',
            headers=self.headers
        )
        vehicle_id = json.loads(create_response.data)['vehicle_id']
        
        response = self.client.delete(
            f'/customers/{self.customer_id}/vehicles/{vehicle_id}',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertIn('message', json_data)
    
    def test_delete_vehicle_unauthorized(self):
        """Test deleting vehicle of another customer (negative test)"""
        # Create vehicle
        vehicle_data = {
            "vin": "1HGCM82633A123456",
            "make": "Honda",
            "model": "Accord",
            "year": 2020,
            "color": "Blue",
            "mileage": 25000
        }
        create_response = self.client.post(
            f'/customers/{self.customer_id}/vehicles',
            data=json.dumps(vehicle_data),
            content_type='application/json',
            headers=self.headers
        )
        vehicle_id = json.loads(create_response.data)['vehicle_id']
        
        # Create another customer
        other_data = {
            "first_name": "Other",
            "last_name": "User",
            "email": "other@example.com",
            "password": "OtherPass123!",
            "phone": "555-111-1111"
        }
        other_response = self.client.post(
            '/auth/register',
            data=json.dumps(other_data),
            content_type='application/json'
        )
        other_token = json.loads(other_response.data)['access_token']
        other_headers = {'Authorization': f'Bearer {other_token}'}
        
        # Try to delete first customer's vehicle with other customer's token
        response = self.client.delete(
            f'/customers/{self.customer_id}/vehicles/{vehicle_id}',
            headers=other_headers
        )
        
        self.assertEqual(response.status_code, 403)
    
    def test_delete_vehicle_no_auth(self):
        """Test deleting vehicle without authentication (negative test)"""
        # Create vehicle
        vehicle_data = {
            "vin": "1HGCM82633A123456",
            "make": "Honda",
            "model": "Accord",
            "year": 2020,
            "color": "Blue",
            "mileage": 25000
        }
        create_response = self.client.post(
            f'/customers/{self.customer_id}/vehicles',
            data=json.dumps(vehicle_data),
            content_type='application/json',
            headers=self.headers
        )
        vehicle_id = json.loads(create_response.data)['vehicle_id']
        
        response = self.client.delete(
            f'/customers/{self.customer_id}/vehicles/{vehicle_id}'
        )
        
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
