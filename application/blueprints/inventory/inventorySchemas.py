from application.extensions import ma
from application.models import Part
from marshmallow import fields, pre_load


class PartSchema(ma.SQLAlchemyAutoSchema):
    """Schema for Part (Inventory) serialization and deserialization"""
    class Meta:
        model = Part
        load_instance = True
        include_fk = True
    
    # Custom fields for computed properties (dump_only means it's only for serialization, not deserialization)
    needs_reorder = fields.Method("get_needs_reorder", dump_only=True)
    
    @pre_load
    def convert_field_names(self, data, **kwargs):
        """Convert reorder_threshold to reorder_level for backwards compatibility with API docs"""
        if 'reorder_threshold' in data:
            data['reorder_level'] = data.pop('reorder_threshold')
        return data
    
    def get_needs_reorder(self, obj):
        """Check if part needs to be reordered"""
        return obj.needs_reorder()


# Single part schema
part_schema = PartSchema()

# Multiple parts schema
parts_schema = PartSchema(many=True)
