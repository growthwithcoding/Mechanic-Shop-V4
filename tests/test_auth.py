import unittest
import json
from application import create_app
from application.extensions import db
from application.models import Customer


class TestAuthRoutes(unittest.TestCase):
    """Test cases for Authentication routes"""
    
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
        """Set up test database before each test"""
        db.create_all()
        
    def tearDown(self):
        """Clean up test database after each test"""
        db.session.remove()
        db.drop_all()
    
    # ===== REGISTER TESTS =====
    
    def test_register_success(self):
        """Test successful customer registration"""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "SecurePass123!",
            "phone": "555-123-4567"
        }
        
        response = self.client.post(
            '/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        json_data = json.loads(response.data)
        self.assertIn('access_token', json_data)
        self.assertIn('customer', json_data)
        self.assertEqual(json_data['customer']['email'], 'john.doe@example.com')
        self.assertEqual(json_data['message'], 'Customer registered successfully')
    
    def test_register_duplicate_email(self):
        """Test registration with duplicate email (negative test)"""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "SecurePass123!",
            "phone": "555-123-4567"
        }
        
        # Register first customer
        self.client.post(
            '/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Try to register again with same email
        response = self.client.post(
            '/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        json_data = json.loads(response.data)
        self.assertIn('error', json_data)
        self.assertEqual(json_data['error'], 'Email already registered')
    
    def test_register_missing_required_field(self):
        """Test registration with missing required field (negative test)"""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com"
            # Missing password and phone
        }
        
        response = self.client.post(
            '/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_register_no_json_data(self):
        """Test registration with no JSON data (negative test)"""
        response = self.client.post('/auth/register')
        
        self.assertEqual(response.status_code, 400)
        json_data = json.loads(response.data)
        self.assertIn('error', json_data)
    
    def test_register_invalid_email(self):
        """Test registration with invalid email format (negative test)"""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "invalid-email",
            "password": "SecurePass123!",
            "phone": "555-123-4567"
        }
        
        response = self.client.post(
            '/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    # ===== LOGIN TESTS =====
    
    def test_login_success(self):
        """Test successful login"""
        # First register a customer
        register_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "SecurePass123!",
            "phone": "555-123-4567"
        }
        self.client.post(
            '/auth/register',
            data=json.dumps(register_data),
            content_type='application/json'
        )
        
        # Now try to login
        login_data = {
            "email": "john.doe@example.com",
            "password": "SecurePass123!"
        }
        
        response = self.client.post(
            '/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertIn('access_token', json_data)
        self.assertIn('customer', json_data)
        self.assertEqual(json_data['message'], 'Login successful')
    
    def test_login_invalid_password(self):
        """Test login with invalid password (negative test)"""
        # First register a customer
        register_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "SecurePass123!",
            "phone": "555-123-4567"
        }
        self.client.post(
            '/auth/register',
            data=json.dumps(register_data),
            content_type='application/json'
        )
        
        # Try to login with wrong password
        login_data = {
            "email": "john.doe@example.com",
            "password": "WrongPassword123!"
        }
        
        response = self.client.post(
            '/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        json_data = json.loads(response.data)
        self.assertIn('error', json_data)
        self.assertEqual(json_data['error'], 'Invalid email or password')
    
    def test_login_nonexistent_email(self):
        """Test login with non-existent email (negative test)"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123!"
        }
        
        response = self.client.post(
            '/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        json_data = json.loads(response.data)
        self.assertIn('error', json_data)
    
    def test_login_missing_credentials(self):
        """Test login with missing credentials (negative test)"""
        login_data = {
            "email": "john.doe@example.com"
            # Missing password
        }
        
        response = self.client.post(
            '/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_login_no_json_data(self):
        """Test login with no JSON data (negative test)"""
        response = self.client.post('/auth/login')
        
        self.assertEqual(response.status_code, 400)
        json_data = json.loads(response.data)
        self.assertIn('error', json_data)
    
    # ===== GET CURRENT USER TESTS =====
    
    def test_get_current_user_success(self):
        """Test getting current user information with valid token"""
        # First register a customer
        register_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "SecurePass123!",
            "phone": "555-123-4567"
        }
        register_response = self.client.post(
            '/auth/register',
            data=json.dumps(register_data),
            content_type='application/json'
        )
        
        token = json.loads(register_response.data)['access_token']
        
        # Get current user info
        response = self.client.get(
            '/auth/me',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['email'], 'john.doe@example.com')
        self.assertEqual(json_data['first_name'], 'John')
    
    def test_get_current_user_no_token(self):
        """Test getting current user without token (negative test)"""
        response = self.client.get('/auth/me')
        
        self.assertEqual(response.status_code, 401)
    
    def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token (negative test)"""
        response = self.client.get(
            '/auth/me',
            headers={'Authorization': 'Bearer invalid_token_here'}
        )
        
        self.assertEqual(response.status_code, 422)


if __name__ == '__main__':
    unittest.main()
