from marshmallow import Schema, fields, validate


class ServiceTicketSchema(Schema):
    ticket_id = fields.Int(dump_only=True)
    vehicle_id = fields.Int(required=True)
    customer_id = fields.Int(required=True)
    status = fields.Str(required=True, validate=validate.OneOf(['open', 'in_progress', 'completed', 'cancelled']))
    opened_at = fields.DateTime(dump_only=True)
    closed_at = fields.DateTime(allow_none=True)
    problem_description = fields.Str(required=True)
    odometer_miles = fields.Int(required=True)
    priority = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    
    # Nested relationships
    ticket_mechanics = fields.List(fields.Nested('TicketMechanicSchema'), dump_only=True)
    ticket_line_items = fields.List(fields.Nested('TicketLineItemSchema'), dump_only=True)


class TicketMechanicSchema(Schema):
    ticket_id = fields.Int(dump_only=True)
    mechanic_id = fields.Int(required=True)
    role = fields.Str(required=True)
    minutes_worked = fields.Int(required=True)
    
    # Nested mechanic info
    mechanic = fields.Nested('MechanicSchema', dump_only=True)


class TicketLineItemSchema(Schema):
    line_item_id = fields.Int(dump_only=True)
    ticket_id = fields.Int(required=True)
    service_id = fields.Int(required=True)
    line_type = fields.Str(required=True)
    description = fields.Str(required=True)
    quantity = fields.Float(required=True)
    unit_price_cents = fields.Int(required=True)


class EditTicketMechanicsSchema(Schema):
    """Schema for adding/removing mechanics from a ticket"""
    add_ids = fields.List(fields.Int(), load_default=[])
    remove_ids = fields.List(fields.Int(), load_default=[])
    role = fields.Str(load_default="Technician")
    minutes_worked = fields.Int(load_default=0)


# Initialize schema instances
service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
ticket_mechanic_schema = TicketMechanicSchema()
ticket_mechanics_schema = TicketMechanicSchema(many=True)
edit_ticket_mechanics_schema = EditTicketMechanicsSchema()
