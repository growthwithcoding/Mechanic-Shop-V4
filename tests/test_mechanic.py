import unittest
import json
from application import create_app
from application.extensions import db
from application.models import Customer, Mechanic


class TestMechanicRoutes(unittest.TestCase):
    """Test cases for Mechanic routes"""
    
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
        self.token = json.loads(response.data)['access_token']
        self.headers = {'Authorization': f'Bearer {self.token}'}
        
    def tearDown(self):
        """Clean up test database after each test"""
        db.session.remove()
        db.drop_all()
    
    # ===== CREATE MECHANIC TESTS =====
    
    def test_create_mechanic_success(self):
        """Test successful mechanic creation"""
        data = {
            "first_name": "Mike",
            "last_name": "Mechanic",
            "email": "mike@mechanicshop.com",
            "phone": "555-111-2222",
            "salary": 50000.00,
            "is_active": True
        }
        
        response = self.client.post(
            '/mechanics',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 201)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['email'], 'mike@mechanicshop.com')
        self.assertEqual(json_data['first_name'], 'Mike')
        self.assertEqual(json_data['salary'], 50000.00)
    
    def test_create_mechanic_duplicate_email(self):
        """Test creating mechanic with duplicate email (negative test)"""
        data = {
            "first_name": "Mike",
            "last_name": "Mechanic",
            "email": "mike@mechanicshop.com",
            "phone": "555-111-2222",
            "salary": 50000.00,
            "is_active": True
        }
        
        # Create first mechanic
        self.client.post(
            '/mechanics',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.headers
        )
        
        # Try to create duplicate
        response = self.client.post(
            '/mechanics',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 400)
        json_data = json.loads(response.data)
        self.assertIn('error', json_data)
    
    def test_create_mechanic_no_auth(self):
        """Test creating mechanic without authentication (negative test)"""
        data = {
            "first_name": "Mike",
            "last_name": "Mechanic",
            "email": "mike@mechanicshop.com",
            "phone": "555-111-2222",
            "salary": 50000.00,
            "is_active": True
        }
        
        response = self.client.post(
            '/mechanics',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_create_mechanic_missing_required_field(self):
        """Test creating mechanic with missing required field (negative test)"""
        data = {
            "first_name": "Mike",
            "last_name": "Mechanic",
            "email": "mike@mechanicshop.com"
            # Missing phone and salary
        }
        
        response = self.client.post(
            '/mechanics',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 400)
    
    # ===== GET ALL MECHANICS TESTS =====
    
    def test_get_all_mechanics_success(self):
        """Test getting all mechanics"""
        # Create test mechanics
        mechanics_data = [
            {
                "first_name": "Mike",
                "last_name": "Mechanic",
                "email": "mike@mechanicshop.com",
                "phone": "555-111-2222",
                "salary": 50000.00,
                "is_active": True
            },
            {
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane@mechanicshop.com",
                "phone": "555-333-4444",
                "salary": 55000.00,
                "is_active": True
            }
        ]
        
        for data in mechanics_data:
            self.client.post(
                '/mechanics',
                data=json.dumps(data),
                content_type='application/json',
                headers=self.headers
            )
        
        response = self.client.get('/mechanics', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(len(json_data), 2)
    
    def test_get_all_mechanics_no_auth(self):
        """Test getting mechanics without authentication (negative test)"""
        response = self.client.get('/mechanics')
        
        self.assertEqual(response.status_code, 401)
    
    # ===== GET MECHANICS BY ACTIVITY TESTS =====
    
    def test_get_mechanics_by_activity_success(self):
        """Test getting mechanics sorted by activity"""
        # Create test mechanics
        mechanic_data = {
            "first_name": "Mike",
            "last_name": "Mechanic",
            "email": "mike@mechanicshop.com",
            "phone": "555-111-2222",
            "salary": 50000.00,
            "is_active": True
        }
        
        self.client.post(
            '/mechanics',
            data=json.dumps(mechanic_data),
            content_type='application/json',
            headers=self.headers
        )
        
        response = self.client.get('/mechanics/by-activity', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertIsInstance(json_data, list)
        if len(json_data) > 0:
            self.assertIn('ticket_count', json_data[0])
    
    def test_get_mechanics_by_activity_no_auth(self):
        """Test getting mechanics by activity without auth (negative test)"""
        response = self.client.get('/mechanics/by-activity')
        
        self.assertEqual(response.status_code, 401)
    
    # ===== GET ONE MECHANIC TESTS =====
    
    def test_get_mechanic_success(self):
        """Test getting a specific mechanic"""
        data = {
            "first_name": "Mike",
            "last_name": "Mechanic",
            "email": "mike@mechanicshop.com",
            "phone": "555-111-2222",
            "salary": 50000.00,
            "is_active": True
        }
        
        create_response = self.client.post(
            '/mechanics',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.headers
        )
        
        mechanic_id = json.loads(create_response.data)['mechanic_id']
        
        response = self.client.get(f'/mechanics/{mechanic_id}', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['mechanic_id'], mechanic_id)
        self.assertIn('ticket_count', json_data)
    
    def test_get_mechanic_not_found(self):
        """Test getting non-existent mechanic (negative test)"""
        response = self.client.get('/mechanics/9999', headers=self.headers)
        
        self.assertEqual(response.status_code, 404)
        json_data = json.loads(response.data)
        self.assertIn('error', json_data)
    
    def test_get_mechanic_no_auth(self):
        """Test getting mechanic without authentication (negative test)"""
        response = self.client.get('/mechanics/1')
        
        self.assertEqual(response.status_code, 401)
    
    # ===== UPDATE MECHANIC TESTS =====
    
    def test_update_mechanic_success(self):
        """Test updating a mechanic"""
        # Create mechanic
        create_data = {
            "first_name": "Mike",
            "last_name": "Mechanic",
            "email": "mike@mechanicshop.com",
            "phone": "555-111-2222",
            "salary": 50000.00,
            "is_active": True
        }
        
        create_response = self.client.post(
            '/mechanics',
            data=json.dumps(create_data),
            content_type='application/json',
            headers=self.headers
        )
        
        mechanic_id = json.loads(create_response.data)['mechanic_id']
        
        # Update mechanic
        update_data = {
            "first_name": "Michael",
            "last_name": "Mechanic",
            "email": "mike@mechanicshop.com",
            "phone": "555-111-2222",
            "salary": 60000.00,
            "is_active": True
        }
        
        response = self.client.put(
            f'/mechanics/{mechanic_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['first_name'], 'Michael')
        self.assertEqual(json_data['salary'], 60000.00)
    
    def test_update_mechanic_not_found(self):
        """Test updating non-existent mechanic (negative test)"""
        update_data = {
            "first_name": "Michael",
            "last_name": "Mechanic",
            "email": "mike@mechanicshop.com",
            "phone": "555-111-2222",
            "salary": 60000.00,
            "is_active": True
        }
        
        response = self.client.put(
            '/mechanics/9999',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_update_mechanic_no_auth(self):
        """Test updating mechanic without authentication (negative test)"""
        update_data = {
            "first_name": "Michael",
            "last_name": "Mechanic",
            "email": "mike@mechanicshop.com",
            "phone": "555-111-2222",
            "salary": 60000.00,
            "is_active": True
        }
        
        response = self.client.put(
            '/mechanics/1',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
    
    # ===== DELETE MECHANIC TESTS =====
    
    def test_delete_mechanic_success(self):
        """Test deleting a mechanic"""
        # Create mechanic
        data = {
            "first_name": "Mike",
            "last_name": "Mechanic",
            "email": "mike@mechanicshop.com",
            "phone": "555-111-2222",
            "salary": 50000.00,
            "is_active": True
        }
        
        create_response = self.client.post(
            '/mechanics',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.headers
        )
        
        mechanic_id = json.loads(create_response.data)['mechanic_id']
        
        response = self.client.delete(f'/mechanics/{mechanic_id}', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertIn('message', json_data)
        
        # Verify deletion
        get_response = self.client.get(f'/mechanics/{mechanic_id}', headers=self.headers)
        self.assertEqual(get_response.status_code, 404)
    
    def test_delete_mechanic_not_found(self):
        """Test deleting non-existent mechanic (negative test)"""
        response = self.client.delete('/mechanics/9999', headers=self.headers)
        
        self.assertEqual(response.status_code, 404)
    
    def test_delete_mechanic_no_auth(self):
        """Test deleting mechanic without authentication (negative test)"""
        response = self.client.delete('/mechanics/1')
        
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
