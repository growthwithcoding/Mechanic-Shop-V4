"""Initial schema for Mechanic Shop V4

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-10-19 08:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create customers table
    op.create_table('customers',
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=255), nullable=False),
        sa.Column('last_name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('address', sa.String(length=255), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=50), nullable=False),
        sa.Column('postal_code', sa.String(length=20), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('customer_id'),
        sa.UniqueConstraint('email')
    )

    # Create vehicles table
    op.create_table('vehicles',
        sa.Column('vehicle_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('vin', sa.String(length=100), nullable=False),
        sa.Column('make', sa.String(length=100), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('color', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.customer_id'], ),
        sa.PrimaryKeyConstraint('vehicle_id'),
        sa.UniqueConstraint('vin')
    )

    # Create mechanics table
    op.create_table('mechanics',
        sa.Column('mechanic_id', sa.Integer(), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('salary', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.PrimaryKeyConstraint('mechanic_id'),
        sa.UniqueConstraint('email')
    )

    # Create services table
    op.create_table('services',
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('default_labor_minutes', sa.Integer(), nullable=False),
        sa.Column('base_price_cents', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('service_id')
    )

    # Create service_tickets table
    op.create_table('service_tickets',
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('vehicle_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('opened_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('closed_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('problem_description', sa.Text(), nullable=False),
        sa.Column('odometer_miles', sa.Integer(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.customer_id'], ),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.vehicle_id'], ),
        sa.PrimaryKeyConstraint('ticket_id')
    )

    # Create parts table (inventory)
    op.create_table('parts',
        sa.Column('part_id', sa.Integer(), nullable=False),
        sa.Column('part_number', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('manufacturer', sa.String(length=255), nullable=True),
        sa.Column('current_cost_cents', sa.Integer(), nullable=False),
        sa.Column('quantity_in_stock', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reorder_level', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('supplier', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('part_id'),
        sa.UniqueConstraint('part_number')
    )

    # Create specializations table
    op.create_table('specializations',
        sa.Column('specialization_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('specialization_id')
    )

    # Create service_packages table
    op.create_table('service_packages',
        sa.Column('package_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('package_discount_percentage', sa.Numeric(precision=5, scale=2), nullable=False, server_default='10.0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('recommended_mileage_interval', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('package_id')
    )

    # Create junction table: ticket_mechanics
    op.create_table('ticket_mechanics',
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('mechanic_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=100), nullable=False),
        sa.Column('minutes_worked', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['mechanic_id'], ['mechanics.mechanic_id'], ),
        sa.ForeignKeyConstraint(['ticket_id'], ['service_tickets.ticket_id'], ),
        sa.PrimaryKeyConstraint('ticket_id', 'mechanic_id')
    )

    # Create junction table: ticket_line_items
    op.create_table('ticket_line_items',
        sa.Column('line_item_id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('line_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('unit_price_cents', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['service_id'], ['services.service_id'], ),
        sa.ForeignKeyConstraint(['ticket_id'], ['service_tickets.ticket_id'], ),
        sa.PrimaryKeyConstraint('line_item_id')
    )

    # Create junction table: ticket_parts
    op.create_table('ticket_parts',
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('part_id', sa.Integer(), nullable=False),
        sa.Column('quantity_used', sa.Integer(), nullable=False),
        sa.Column('unit_cost_cents', sa.Integer(), nullable=False),
        sa.Column('markup_percentage', sa.Numeric(precision=5, scale=2), nullable=False, server_default='30.0'),
        sa.Column('installed_date', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('warranty_months', sa.Integer(), nullable=True),
        sa.Column('installed_by_mechanic_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['installed_by_mechanic_id'], ['mechanics.mechanic_id'], ),
        sa.ForeignKeyConstraint(['part_id'], ['parts.part_id'], ),
        sa.ForeignKeyConstraint(['ticket_id'], ['service_tickets.ticket_id'], ),
        sa.PrimaryKeyConstraint('ticket_id', 'part_id')
    )

    # Create junction table: mechanic_specializations
    op.create_table('mechanic_specializations',
        sa.Column('mechanic_id', sa.Integer(), nullable=False),
        sa.Column('specialization_id', sa.Integer(), nullable=False),
        sa.Column('certified_date', sa.TIMESTAMP(), nullable=False),
        sa.Column('expiration_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('certification_number', sa.String(length=100), nullable=True),
        sa.Column('proficiency_level', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['mechanic_id'], ['mechanics.mechanic_id'], ),
        sa.ForeignKeyConstraint(['specialization_id'], ['specializations.specialization_id'], ),
        sa.PrimaryKeyConstraint('mechanic_id', 'specialization_id')
    )

    # Create junction table: service_prerequisites
    op.create_table('service_prerequisites',
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('prerequisite_service_id', sa.Integer(), nullable=False),
        sa.Column('is_required', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('recommended_gap_hours', sa.Integer(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['prerequisite_service_id'], ['services.service_id'], ),
        sa.ForeignKeyConstraint(['service_id'], ['services.service_id'], ),
        sa.PrimaryKeyConstraint('service_id', 'prerequisite_service_id')
    )

    # Create junction table: service_package_items
    op.create_table('service_package_items',
        sa.Column('package_id', sa.Integer(), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_optional', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('discount_percentage', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0.0'),
        sa.Column('sequence_order', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['package_id'], ['service_packages.package_id'], ),
        sa.ForeignKeyConstraint(['service_id'], ['services.service_id'], ),
        sa.PrimaryKeyConstraint('package_id', 'service_id')
    )


def downgrade():
    # Drop tables in reverse order (junction tables first)
    op.drop_table('service_package_items')
    op.drop_table('service_prerequisites')
    op.drop_table('mechanic_specializations')
    op.drop_table('ticket_parts')
    op.drop_table('ticket_line_items')
    op.drop_table('ticket_mechanics')
    op.drop_table('service_packages')
    op.drop_table('specializations')
    op.drop_table('parts')
    op.drop_table('service_tickets')
    op.drop_table('services')
    op.drop_table('mechanics')
    op.drop_table('vehicles')
    op.drop_table('customers')
