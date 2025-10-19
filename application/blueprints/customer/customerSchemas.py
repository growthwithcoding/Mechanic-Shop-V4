from application.extensions import ma
from application.models import Customer, Vehicle


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        exclude = ('password_hash',)  # Exclude password hash from serialization


class VehicleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Vehicle
        include_fk = True  # Include foreign keys


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
vehicle_schema = VehicleSchema()
vehicles_schema = VehicleSchema(many=True)
