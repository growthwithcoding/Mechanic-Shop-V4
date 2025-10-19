from application.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta
from werkzeug.security import generate_password_hash, check_password_hash


class Customer(db.Model):
    __tablename__ = 'customers'
    
    customer_id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(50), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(db.String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(db.String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(db.String(50), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(db.String(20), nullable=True)
    password_hash: Mapped[str] = mapped_column(db.String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    vehicles: Mapped[List['Vehicle']] = relationship(back_populates='customer')
    service_tickets: Mapped[List['ServiceTicket']] = relationship(back_populates='customer')
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)


class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    vehicle_id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.customer_id'), nullable=False)
    vin: Mapped[str] = mapped_column(db.String(100), nullable=False, unique=True)
    make: Mapped[str] = mapped_column(db.String(100), nullable=False)
    model: Mapped[str] = mapped_column(db.String(100), nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)
    color: Mapped[str] = mapped_column(db.String(50), nullable=False)
    
    # Relationships
    customer: Mapped['Customer'] = relationship(back_populates='vehicles')
    service_tickets: Mapped[List['ServiceTicket']] = relationship(back_populates='vehicle')


class Mechanic(db.Model):
    __tablename__ = 'mechanics'
    
    mechanic_id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(50), nullable=False)
    salary: Mapped[int] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(db.Boolean, default=True)
    
    # Relationships
    ticket_mechanics: Mapped[List['TicketMechanic']] = relationship(back_populates='mechanic')
    specializations: Mapped[List['MechanicSpecialization']] = relationship(back_populates='mechanic')
    parts_installed: Mapped[List['TicketPart']] = relationship(foreign_keys='TicketPart.installed_by_mechanic_id')


class Service(db.Model):
    __tablename__ = 'services'
    
    service_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    default_labor_minutes: Mapped[int] = mapped_column(nullable=False)
    base_price_cents: Mapped[int] = mapped_column(nullable=False)
    
    # Relationships
    ticket_line_items: Mapped[List['TicketLineItem']] = relationship(back_populates='service')
    prerequisites: Mapped[List['ServicePrerequisite']] = relationship(
        foreign_keys='ServicePrerequisite.service_id',
        back_populates='service'
    )
    dependent_services: Mapped[List['ServicePrerequisite']] = relationship(
        foreign_keys='ServicePrerequisite.prerequisite_service_id',
        back_populates='prerequisite'
    )
    package_memberships: Mapped[List['ServicePackageItem']] = relationship(back_populates='service')


class ServiceTicket(db.Model):
    __tablename__ = 'service_tickets'
    
    ticket_id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(db.ForeignKey('vehicles.vehicle_id'), nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.customer_id'), nullable=False)
    status: Mapped[str] = mapped_column(db.String(50), nullable=False)
    opened_at: Mapped[datetime] = mapped_column(db.TIMESTAMP, default=datetime.utcnow)
    closed_at: Mapped[datetime] = mapped_column(db.TIMESTAMP, nullable=True)
    problem_description: Mapped[str] = mapped_column(db.Text, nullable=False)
    odometer_miles: Mapped[int] = mapped_column(nullable=False)
    priority: Mapped[int] = mapped_column(nullable=False)
    
    # Relationships
    vehicle: Mapped['Vehicle'] = relationship(back_populates='service_tickets')
    customer: Mapped['Customer'] = relationship(back_populates='service_tickets')
    ticket_line_items: Mapped[List['TicketLineItem']] = relationship(back_populates='service_ticket')
    ticket_mechanics: Mapped[List['TicketMechanic']] = relationship(back_populates='service_ticket')
    parts_used: Mapped[List['TicketPart']] = relationship(back_populates='service_ticket')


class TicketLineItem(db.Model):
    __tablename__ = 'ticket_line_items'
    
    line_item_id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(db.ForeignKey('service_tickets.ticket_id'), nullable=False)
    service_id: Mapped[int] = mapped_column(db.ForeignKey('services.service_id'), nullable=False)
    line_type: Mapped[str] = mapped_column(db.String(50), nullable=False)
    description: Mapped[str] = mapped_column(db.Text, nullable=False)
    quantity: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=False)
    unit_price_cents: Mapped[int] = mapped_column(nullable=False)
    
    # Relationships
    service_ticket: Mapped['ServiceTicket'] = relationship(back_populates='ticket_line_items')
    service: Mapped['Service'] = relationship(back_populates='ticket_line_items')


class TicketMechanic(db.Model):
    __tablename__ = 'ticket_mechanics'
    
    ticket_id: Mapped[int] = mapped_column(db.ForeignKey('service_tickets.ticket_id'), primary_key=True)
    mechanic_id: Mapped[int] = mapped_column(db.ForeignKey('mechanics.mechanic_id'), primary_key=True)
    role: Mapped[str] = mapped_column(db.String(100), nullable=False)
    minutes_worked: Mapped[int] = mapped_column(nullable=False)
    
    # Relationships
    service_ticket: Mapped['ServiceTicket'] = relationship(back_populates='ticket_mechanics')
    mechanic: Mapped['Mechanic'] = relationship(back_populates='ticket_mechanics')


class Part(db.Model):
    """Parts inventory management"""
    __tablename__ = 'parts'
    
    part_id: Mapped[int] = mapped_column(primary_key=True)
    part_number: Mapped[str] = mapped_column(db.String(100), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(db.Text, nullable=True)
    category: Mapped[str] = mapped_column(db.String(100), nullable=False)
    manufacturer: Mapped[Optional[str]] = mapped_column(db.String(255), nullable=True)
    current_cost_cents: Mapped[int] = mapped_column(nullable=False)
    quantity_in_stock: Mapped[int] = mapped_column(nullable=False, default=0)
    reorder_level: Mapped[int] = mapped_column(nullable=False, default=5)
    supplier: Mapped[Optional[str]] = mapped_column(db.String(255), nullable=True)
    
    # Relationships
    usage_history: Mapped[List['TicketPart']] = relationship(back_populates='part')
    
    def needs_reorder(self):
        """Check if part needs to be reordered"""
        return self.quantity_in_stock <= self.reorder_level


class TicketPart(db.Model):
    """Junction table tracking parts used in service tickets"""
    __tablename__ = 'ticket_parts'
    
    ticket_id: Mapped[int] = mapped_column(db.ForeignKey('service_tickets.ticket_id'), primary_key=True)
    part_id: Mapped[int] = mapped_column(db.ForeignKey('parts.part_id'), primary_key=True)
    quantity_used: Mapped[int] = mapped_column(nullable=False)
    unit_cost_cents: Mapped[int] = mapped_column(nullable=False)
    markup_percentage: Mapped[float] = mapped_column(db.Numeric(5, 2), nullable=False, default=30.0)
    installed_date: Mapped[datetime] = mapped_column(db.TIMESTAMP, default=datetime.utcnow)
    warranty_months: Mapped[Optional[int]] = mapped_column(nullable=True)
    installed_by_mechanic_id: Mapped[Optional[int]] = mapped_column(
        db.ForeignKey('mechanics.mechanic_id'), 
        nullable=True
    )
    
    # Relationships
    service_ticket: Mapped['ServiceTicket'] = relationship(back_populates='parts_used')
    part: Mapped['Part'] = relationship(back_populates='usage_history')
    installed_by: Mapped[Optional['Mechanic']] = relationship(
        foreign_keys=[installed_by_mechanic_id],
        overlaps="parts_installed"
    )
    
    def get_total_cost(self):
        """Calculate total cost with markup"""
        base_cost = (self.quantity_used * self.unit_cost_cents) / 100
        markup = base_cost * (self.markup_percentage / 100)
        return round(base_cost + markup, 2)
    
    def is_under_warranty(self):
        """Check if part is still under warranty"""
        if self.warranty_months:
            warranty_end = self.installed_date + relativedelta(months=self.warranty_months)
            return datetime.utcnow() < warranty_end
        return False


class Specialization(db.Model):
    """Types of certifications/specializations for mechanics"""
    __tablename__ = 'specializations'
    
    specialization_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(db.Text, nullable=True)
    category: Mapped[str] = mapped_column(db.String(100), nullable=False)
    
    # Relationships
    certified_mechanics: Mapped[List['MechanicSpecialization']] = relationship(back_populates='specialization')


class MechanicSpecialization(db.Model):
    """Junction table tracking mechanic certifications"""
    __tablename__ = 'mechanic_specializations'
    
    mechanic_id: Mapped[int] = mapped_column(db.ForeignKey('mechanics.mechanic_id'), primary_key=True)
    specialization_id: Mapped[int] = mapped_column(db.ForeignKey('specializations.specialization_id'), primary_key=True)
    certified_date: Mapped[datetime] = mapped_column(db.TIMESTAMP, nullable=False)
    expiration_date: Mapped[Optional[datetime]] = mapped_column(db.TIMESTAMP, nullable=True)
    certification_number: Mapped[Optional[str]] = mapped_column(db.String(100), nullable=True)
    proficiency_level: Mapped[str] = mapped_column(db.String(50), nullable=False)
    
    # Relationships
    mechanic: Mapped['Mechanic'] = relationship(back_populates='specializations')
    specialization: Mapped['Specialization'] = relationship(back_populates='certified_mechanics')
    
    def is_expired(self):
        """Check if certification is expired"""
        if self.expiration_date:
            return datetime.utcnow() > self.expiration_date
        return False


class ServicePrerequisite(db.Model):
    """Junction table for service dependencies"""
    __tablename__ = 'service_prerequisites'
    
    service_id: Mapped[int] = mapped_column(db.ForeignKey('services.service_id'), primary_key=True)
    prerequisite_service_id: Mapped[int] = mapped_column(db.ForeignKey('services.service_id'), primary_key=True)
    is_required: Mapped[bool] = mapped_column(db.Boolean, default=True)
    recommended_gap_hours: Mapped[Optional[int]] = mapped_column(nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(db.Text, nullable=True)
    
    # Relationships
    service: Mapped['Service'] = relationship(
        foreign_keys=[service_id],
        back_populates='prerequisites'
    )
    prerequisite: Mapped['Service'] = relationship(
        foreign_keys=[prerequisite_service_id],
        back_populates='dependent_services'
    )


class ServicePackage(db.Model):
    """Bundled service offerings"""
    __tablename__ = 'service_packages'
    
    package_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(db.Text, nullable=True)
    package_discount_percentage: Mapped[float] = mapped_column(db.Numeric(5, 2), default=10.0)
    is_active: Mapped[bool] = mapped_column(db.Boolean, default=True)
    recommended_mileage_interval: Mapped[Optional[int]] = mapped_column(nullable=True)
    
    # Relationships
    included_services: Mapped[List['ServicePackageItem']] = relationship(back_populates='package')


class ServicePackageItem(db.Model):
    """Junction table for service packages"""
    __tablename__ = 'service_package_items'
    
    package_id: Mapped[int] = mapped_column(db.ForeignKey('service_packages.package_id'), primary_key=True)
    service_id: Mapped[int] = mapped_column(db.ForeignKey('services.service_id'), primary_key=True)
    quantity: Mapped[int] = mapped_column(nullable=False, default=1)
    is_optional: Mapped[bool] = mapped_column(db.Boolean, default=False)
    discount_percentage: Mapped[float] = mapped_column(db.Numeric(5, 2), default=0.0)
    sequence_order: Mapped[int] = mapped_column(nullable=False)
    
    # Relationships
    package: Mapped['ServicePackage'] = relationship(back_populates='included_services')
    service: Mapped['Service'] = relationship(back_populates='package_memberships')
