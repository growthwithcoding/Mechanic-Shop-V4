import unittest
import json
from application import create_app
from application.extensions import db
from application.models import Customer, Part


class TestInventoryRoutes(unittest.TestCase):
    """Test cases for Inventory routes"""
    
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
    
    # ===== CREATE PART TESTS =====
    
    def test_create_part_success(self):
        """Test successful part creation"""
        data = {
            "part_number": "BRK-001",
            "name": "Brake Pad Set",
            "description": "Front brake pads for most vehicles",
            "category": "Brakes",
            "current_cost_cents": 4500,
            "quantity_in_stock": 25,
            "reorder_threshold": 5
        }
        
        response = self.client.post(
            '/inventory',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 201)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['part_number'], 'BRK-001')
        self.assertEqual(json_data['name'], 'Brake Pad Set')
    
    def test_create_part_duplicate_number(self):
        """Test creating part with duplicate part number (negative test)"""
        data = {
            "part_number": "BRK-001",
            "name": "Brake Pad Set",
            "description": "Front brake pads",
            "category": "Brakes",
            "current_cost_cents": 4500,
            "quantity_in_stock": 25,
            "reorder_threshold": 5
        }
        
        # Create first part
        self.client.post(
            '/inventory',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.headers
        )
        
        # Try to create duplicate
        response = self.client.post(
            '/inventory',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 400)
        json_data = json.loads(response.data)
        self.assertIn('error', json_data)
    
    def test_create_part_no_auth(self):
        """Test creating part without authentication (negative test)"""
        data = {
            "part_number": "BRK-001",
            "name": "Brake Pad Set",
            "description": "Front brake pads",
            "category": "Brakes",
            "current_cost_cents": 4500,
            "quantity_in_stock": 25,
            "reorder_threshold": 5
        }
        
        response = self.client.post(
            '/inventory',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_create_part_missing_required_field(self):
        """Test creating part with missing required field (negative test)"""
        data = {
            "part_number": "BRK-001",
            "name": "Brake Pad Set"
            # Missing other required fields
        }
        
        response = self.client.post(
            '/inventory',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 400)
    
    # ===== GET ALL PARTS TESTS =====
    
    def test_get_all_parts_success(self):
        """Test getting all parts"""
        # Create test parts
        parts_data = [
            {
                "part_number": "BRK-001",
                "name": "Brake Pad Set",
                "description": "Front brake pads",
                "category": "Brakes",
                "current_cost_cents": 4500,
                "quantity_in_stock": 25,
                "reorder_threshold": 5
            },
            {
                "part_number": "OIL-001",
                "name": "Engine Oil 5W-30",
                "description": "Premium synthetic oil",
                "category": "Fluids",
                "current_cost_cents": 2500,
                "quantity_in_stock": 50,
                "reorder_threshold": 10
            }
        ]
        
        for data in parts_data:
            self.client.post(
                '/inventory',
                data=json.dumps(data),
                content_type='application/json',
                headers=self.headers
            )
        
        response = self.client.get('/inventory', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(len(json_data), 2)
    
    def test_get_all_parts_no_auth(self):
        """Test getting parts without authentication (negative test)"""
        response = self.client.get('/inventory')
        
        self.assertEqual(response.status_code, 401)
    
    def test_get_parts_with_category_filter(self):
        """Test getting parts with category filter"""
        # Create test parts
        parts_data = [
            {
                "part_number": "BRK-001",
                "name": "Brake Pad Set",
                "description": "Front brake pads",
                "category": "Brakes",
                "current_cost_cents": 4500,
                "quantity_in_stock": 25,
                "reorder_threshold": 5
            },
            {
                "part_number": "OIL-001",
                "name": "Engine Oil 5W-30",
                "description": "Premium synthetic oil",
                "category": "Fluids",
                "current_cost_cents": 2500,
                "quantity_in_stock": 50,
                "reorder_threshold": 10
            }
        ]
        
        for data in parts_data:
            self.client.post(
                '/inventory',
                data=json.dumps(data),
                content_type='application/json',
                headers=self.headers
            )
        
        response = self.client.get('/inventory?category=Brakes', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(len(json_data), 1)
        self.assertEqual(json_data[0]['category'], 'Brakes')
    
    # ===== GET ONE PART TESTS =====
    
    def test_get_part_success(self):
        """Test getting a specific part"""
        data = {
            "part_number": "BRK-001",
            "name": "Brake Pad Set",
            "description": "Front brake pads",
            "category": "Brakes",
            "current_cost_cents": 4500,
            "quantity_in_stock": 25,
            "reorder_threshold": 5
        }
        
        create_response = self.client.post(
            '/inventory',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.headers
        )
        
        part_id = json.loads(create_response.data)['part_id']
        
        response = self.client.get(f'/inventory/{part_id}', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['part_id'], part_id)
    
    def test_get_part_not_found(self):
        """Test getting non-existent part (negative test)"""
        response = self.client.get('/inventory/9999', headers=self.headers)
        
        self.assertEqual(response.status_code, 404)
        json_data = json.loads(response.data)
        self.assertIn('error', json_data)
    
    def test_get_part_no_auth(self):
        """Test getting part without authentication (negative test)"""
        response = self.client.get('/inventory/1')
        
        self.assertEqual(response.status_code, 401)
    
    # ===== UPDATE PART TESTS =====
    
    def test_update_part_success(self):
        """Test updating a part"""
        # Create part
        create_data = {
            "part_number": "BRK-001",
            "name": "Brake Pad Set",
            "description": "Front brake pads",
            "category": "Brakes",
            "current_cost_cents": 4500,
            "quantity_in_stock": 25,
            "reorder_threshold": 5
        }
        
        create_response = self.client.post(
            '/inventory',
            data=json.dumps(create_data),
            content_type='application/json',
            headers=self.headers
        )
        
        part_id = json.loads(create_response.data)['part_id']
        
        # Update part
        update_data = {
            "part_number": "BRK-001",
            "name": "Brake Pad Set Premium",
            "description": "Premium front brake pads",
            "category": "Brakes",
            "current_cost_cents": 5500,
            "quantity_in_stock": 30,
            "reorder_threshold": 5
        }
        
        response = self.client.put(
            f'/inventory/{part_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['name'], 'Brake Pad Set Premium')
        self.assertEqual(json_data['current_cost_cents'], 5500)
    
    def test_update_part_not_found(self):
        """Test updating non-existent part (negative test)"""
        update_data = {
            "part_number": "BRK-001",
            "name": "Brake Pad Set",
            "description": "Front brake pads",
            "category": "Brakes",
            "current_cost_cents": 4500,
            "quantity_in_stock": 25,
            "reorder_threshold": 5
        }
        
        response = self.client.put(
            '/inventory/9999',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_update_part_no_auth(self):
        """Test updating part without authentication (negative test)"""
        update_data = {
            "part_number": "BRK-001",
            "name": "Brake Pad Set",
            "description": "Front brake pads",
            "category": "Brakes",
            "current_cost_cents": 4500,
            "quantity_in_stock": 25,
            "reorder_threshold": 5
        }
        
        response = self.client.put(
            '/inventory/1',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
    
    # ===== DELETE PART TESTS =====
    
    def test_delete_part_success(self):
        """Test deleting a part"""
        # Create part
        data = {
            "part_number": "BRK-001",
            "name": "Brake Pad Set",
            "description": "Front brake pads",
            "category": "Brakes",
            "current_cost_cents": 4500,
            "quantity_in_stock": 25,
            "reorder_threshold": 5
        }
        
        create_response = self.client.post(
            '/inventory',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.headers
        )
        
        part_id = json.loads(create_response.data)['part_id']
        
        response = self.client.delete(f'/inventory/{part_id}', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertIn('message', json_data)
        
        # Verify deletion
        get_response = self.client.get(f'/inventory/{part_id}', headers=self.headers)
        self.assertEqual(get_response.status_code, 404)
    
    def test_delete_part_not_found(self):
        """Test deleting non-existent part (negative test)"""
        response = self.client.delete('/inventory/9999', headers=self.headers)
        
        self.assertEqual(response.status_code, 404)
    
    def test_delete_part_no_auth(self):
        """Test deleting part without authentication (negative test)"""
        response = self.client.delete('/inventory/1')
        
        self.assertEqual(response.status_code, 401)
    
    # ===== ADJUST QUANTITY TESTS =====
    
    def test_adjust_quantity_add_success(self):
        """Test adding to part quantity"""
        # Create part
        data = {
            "part_number": "BRK-001",
            "name": "Brake Pad Set",
            "description": "Front brake pads",
            "category": "Brakes",
            "current_cost_cents": 4500,
            "quantity_in_stock": 25,
            "reorder_threshold": 5
        }
        
        create_response = self.client.post(
            '/inventory',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.headers
        )
        
        part_id = json.loads(create_response.data)['part_id']
        
        # Add quantity
        adjustment_data = {"adjustment": 10}
        
        response = self.client.patch(
            f'/inventory/{part_id}/adjust-quantity',
            data=json.dumps(adjustment_data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['new_quantity'], 35)
        self.assertEqual(json_data['adjustment'], 10)
    
    def test_adjust_quantity_subtract_success(self):
        """Test subtracting from part quantity"""
        # Create part
        data = {
            "part_number": "BRK-001",
            "name": "Brake Pad Set",
            "description": "Front brake pads",
            "category": "Brakes",
            "current_cost_cents": 4500,
            "quantity_in_stock": 25,
            "reorder_threshold": 5
        }
        
        create_response = self.client.post(
            '/inventory',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.headers
        )
        
        part_id = json.loads(create_response.data)['part_id']
        
        # Subtract quantity
        adjustment_data = {"adjustment": -10}
        
        response = self.client.patch(
            f'/inventory/{part_id}/adjust-quantity',
            data=json.dumps(adjustment_data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['new_quantity'], 15)
    
    def test_adjust_quantity_negative_result(self):
        """Test adjustment that would result in negative quantity (negative test)"""
        # Create part
        data = {
            "part_number": "BRK-001",
            "name": "Brake Pad Set",
            "description": "Front brake pads",
            "category": "Brakes",
            "current_cost_cents": 4500,
            "quantity_in_stock": 10,
            "reorder_threshold": 5
        }
        
        create_response = self.client.post(
            '/inventory',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.headers
        )
        
        part_id = json.loads(create_response.data)['part_id']
        
        # Try to subtract more than available
        adjustment_data = {"adjustment": -20}
        
        response = self.client.patch(
            f'/inventory/{part_id}/adjust-quantity',
            data=json.dumps(adjustment_data),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 400)
        json_data = json.loads(response.data)
        self.assertIn('error', json_data)
    
    def test_adjust_quantity_missing_adjustment(self):
        """Test adjustment without adjustment field (negative test)"""
        # Create part
        data = {
            "part_number": "BRK-001",
            "name": "Brake Pad Set",
            "description": "Front brake pads",
            "category": "Brakes",
            "current_cost_cents": 4500,
            "quantity_in_stock": 25,
            "reorder_threshold": 5
        }
        
        create_response = self.client.post(
            '/inventory',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.headers
        )
        
        part_id = json.loads(create_response.data)['part_id']
        
        response = self.client.patch(
            f'/inventory/{part_id}/adjust-quantity',
            data=json.dumps({}),
            content_type='application/json',
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_adjust_quantity_no_auth(self):
        """Test adjusting quantity without authentication (negative test)"""
        adjustment_data = {"adjustment": 10}
        
        response = self.client.patch(
            '/inventory/1/adjust-quantity',
            data=json.dumps(adjustment_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
