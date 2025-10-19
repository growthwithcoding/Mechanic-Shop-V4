from application.extensions import ma
from marshmallow import fields, validate, pre_load

class RegisterSchema(ma.Schema):
    """Schema for user registration"""
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    last_name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    email = fields.Email(required=True)
    phone = fields.String(required=True, validate=validate.Length(min=1, max=50))
    address = fields.String(required=False, allow_none=True, validate=validate.Length(min=1, max=255))
    city = fields.String(required=False, allow_none=True, validate=validate.Length(min=1, max=100))
    state = fields.String(required=False, allow_none=True, validate=validate.Length(min=1, max=50))
    postal_code = fields.String(required=False, allow_none=True, validate=validate.Length(min=1, max=20))
    password = fields.String(required=True, validate=validate.Length(min=6), load_only=True)
    
    @pre_load
    def convert_postal_code(self, data, **kwargs):
        """Convert postal_code to string if it's an integer"""
        if 'postal_code' in data and isinstance(data['postal_code'], int):
            data['postal_code'] = str(data['postal_code'])
        return data

class LoginSchema(ma.Schema):
    """Schema for user login"""
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)

# Create schema instances
register_schema = RegisterSchema()
login_schema = LoginSchema()
