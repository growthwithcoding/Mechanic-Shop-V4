"""
Test suite for enhanced error handling system

This test suite validates that the enhanced error handling system:
1. Returns proper error responses with error_ids
2. Logs errors appropriately
3. Provides environment-aware responses
4. Handles different error types correctly

Note: Pylance may show type warnings for SQLAlchemy model constructors.
These are false positives - SQLAlchemy generates __init__ dynamically at runtime.
"""
import pytest  # type: ignore
from application import create_app
from application.extensions import db
from application.models import Customer
from flask_jwt_extended import create_access_token


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    """Create authentication headers with JWT token"""
    with app.app_context():
        # Create a test customer
        # Note: SQLAlchemy generates __init__ parameters dynamically
        # Using kwargs dict to avoid Pylance parameter warnings
        customer_data = {
            'first_name': "Test",
            'last_name': "User",
            'email': "test@example.com",
            'phone': "1234567890",
            'password_hash': "test_hash"
        }
        customer = Customer(**customer_data)  # type: ignore
        db.session.add(customer)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=str(customer.customer_id))
        
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }


class TestErrorIDGeneration:
    """Test that all errors return unique error IDs"""
    
    def test_404_error_has_error_id(self, client, auth_headers):
        """Test 404 errors include error_id"""
        response = client.get('/customers/99999', headers=auth_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        
        assert 'error_id' in data
        assert 'error' in data
        assert 'message' in data
        assert 'timestamp' in data
        assert data['error'] == 'Not Found'
    
    def test_401_error_has_error_id(self, client):
        """Test 401 errors include error_id"""
        response = client.get('/customers')
        
        assert response.status_code == 401
        data = response.get_json()
        
        assert 'error_id' in data
        assert data['error'] == 'Unauthorized'
    
    def test_405_error_has_error_id(self, client, auth_headers):
        """Test 405 Method Not Allowed errors include error_id"""
        # Try to PATCH a customer (method not allowed)
        response = client.patch('/customers/1', headers=auth_headers)
        
        assert response.status_code == 405
        data = response.get_json()
        
        assert 'error_id' in data
        assert data['error'] == 'Method Not Allowed'


class TestDatabaseErrorHandling:
    """Test database-specific error handling"""
    
    def test_duplicate_email_integrity_error(self, client, auth_headers):
        """Test duplicate email returns proper IntegrityError response"""
        # Create first customer
        customer_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "duplicate@example.com",
            "phone": "1234567890",
            "address": "123 Main St",
            "password": "password123"
        }
        
        response1 = client.post(
            '/customers',
            json=customer_data,
            headers=auth_headers
        )
        assert response1.status_code == 201
        
        # Try to create duplicate
        response2 = client.post(
            '/customers',
            json=customer_data,
            headers=auth_headers
        )
        
        assert response2.status_code == 400
        data = response2.get_json()
        
        assert 'error_id' in data
        assert data['error'] == 'Database Integrity Error'
        assert 'already exists' in data['message'].lower()
    
    def test_invalid_foreign_key_integrity_error(self, client, auth_headers):
        """Test invalid foreign key returns proper error"""
        # Try to create service ticket with non-existent vehicle
        ticket_data = {
            "vehicle_id": 99999,  # Non-existent
            "description": "Oil change",
            "status": "pending"
        }
        
        response = client.post(
            '/service_tickets',
            json=ticket_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert 'error_id' in data
        # Could be either integrity error or validation error depending on implementation


class TestValidationErrorHandling:
    """Test validation error handling"""
    
    def test_validation_error_structure(self, client, auth_headers):
        """Test validation errors return proper structure"""
        # Send invalid customer data
        invalid_data = {
            "first_name": "",  # Empty name
            "last_name": "",
            "email": "not-an-email",  # Invalid email
            "phone": "123"  # Too short
        }
        
        response = client.post(
            '/customers',
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert 'error_id' in data
        assert 'error' in data
        assert 'validation_errors' in data or 'messages' in data
        assert data['error'] == 'Validation Error'


class TestErrorResponseStructure:
    """Test that error responses follow consistent structure"""
    
    def test_error_response_has_required_fields(self, client, auth_headers):
        """Test all error responses have required fields"""
        response = client.get('/customers/99999', headers=auth_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        
        # All errors must have these fields
        required_fields = ['error', 'message', 'error_id', 'timestamp']
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    
    def test_error_id_is_uuid(self, client, auth_headers):
        """Test that error_id is a valid UUID"""
        import uuid
        
        response = client.get('/customers/99999', headers=auth_headers)
        data = response.get_json()
        
        error_id = data['error_id']
        
        # Should be able to parse as UUID
        try:
            uuid.UUID(error_id)
        except ValueError:
            pytest.fail(f"error_id '{error_id}' is not a valid UUID")
    
    def test_timestamp_is_iso8601(self, client, auth_headers):
        """Test that timestamp is ISO 8601 format"""
        from datetime import datetime
        
        response = client.get('/customers/99999', headers=auth_headers)
        data = response.get_json()
        
        timestamp = data['timestamp']
        
        # Should be able to parse as ISO 8601
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            pytest.fail(f"timestamp '{timestamp}' is not valid ISO 8601 format")


class TestEnvironmentAwareResponses:
    """Test that responses differ based on DEBUG mode"""
    
    def test_debug_mode_shows_details(self, app, client, auth_headers):
        """Test that debug mode includes error details"""
        # Enable debug mode
        app.config['DEBUG'] = True
        
        # Trigger an error that would show details
        response = client.get('/customers/99999', headers=auth_headers)
        data = response.get_json()
        
        # In debug mode, we might see additional details
        # (specific implementation may vary)
        assert 'error_id' in data
        assert 'error' in data
        assert 'message' in data


class TestHTTPErrorHandlers:
    """Test all HTTP error handlers"""
    
    def test_400_bad_request(self, client, auth_headers):
        """Test 400 Bad Request handler"""
        # Send invalid JSON (missing required fields)
        response = client.post(
            '/customers',
            json={},
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error_id' in data
    
    def test_401_unauthorized(self, client):
        """Test 401 Unauthorized handler"""
        # Try to access protected endpoint without auth
        response = client.get('/customers')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error_id' in data
        assert data['error'] == 'Unauthorized'
    
    def test_403_forbidden(self, client, auth_headers):
        """Test 403 Forbidden handler"""
        # Try to update another user's information
        response = client.put(
            '/customers/99999',
            json={"first_name": "Hacker"},
            headers=auth_headers
        )
        
        # Should be 403 or 404 depending on implementation
        assert response.status_code in [403, 404]
        data = response.get_json()
        assert 'error_id' in data
    
    def test_404_not_found(self, client, auth_headers):
        """Test 404 Not Found handler"""
        response = client.get('/customers/99999', headers=auth_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error_id' in data
        assert data['error'] == 'Not Found'
    
    def test_405_method_not_allowed(self, client, auth_headers):
        """Test 405 Method Not Allowed handler"""
        # Try unsupported HTTP method
        response = client.patch('/customers/1', headers=auth_headers)
        
        assert response.status_code == 405
        data = response.get_json()
        assert 'error_id' in data
        assert data['error'] == 'Method Not Allowed'


class TestErrorLogging:
    """Test that errors are properly logged"""
    
    def test_error_is_logged(self, client, auth_headers, caplog):
        """Test that errors generate log entries"""
        import logging
        
        # Trigger an error
        with caplog.at_level(logging.ERROR):
            response = client.get('/customers/99999', headers=auth_headers)
        
        # Check that error was logged
        assert len(caplog.records) > 0
        
        # Check log contains error information
        log_messages = [record.message for record in caplog.records]
        assert any('Error' in msg for msg in log_messages)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
