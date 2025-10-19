from marshmallow import Schema, fields, validate, pre_load


class MechanicSchema(Schema):
    mechanic_id = fields.Int(dump_only=True)
    full_name = fields.Str(required=True)
    email = fields.Str(required=True, validate=validate.Email())
    phone = fields.Str(required=True)
    salary = fields.Int(required=True)
    is_active = fields.Bool(load_default=True)
    
    # Optional: Include ticket count when sorting by popularity
    ticket_count = fields.Int(dump_only=True)
    
    @pre_load
    def combine_names(self, data, **kwargs):
        """Combine first_name and last_name into full_name for backwards compatibility with API docs"""
        if 'first_name' in data and 'last_name' in data:
            data['full_name'] = f"{data['first_name']} {data['last_name']}"
            # Remove first_name and last_name to avoid validation errors
            data.pop('first_name', None)
            data.pop('last_name', None)
        return data


# Initialize schema instances
mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
