"""Quick debug script to see what's happening with the auth test"""
import json
from application import create_app
from application.extensions import db

# Create app in testing mode
app = create_app('testing')
client = app.test_client()

with app.app_context():
    # Create tables
    db.create_all()
    
    # Try to register
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "alice.johnson@email.com",
        "password": "password123",
        "phone": "555-123-4567"
    }
    
    response = client.post(
        '/auth/register',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Data: {response.data.decode('utf-8')}")
    
    # Clean up
    db.drop_all()
