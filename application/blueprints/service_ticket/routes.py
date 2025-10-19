from typing import Any, Dict, cast
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from flask_jwt_extended import jwt_required
from application.blueprints.service_ticket import service_ticket_bp
from application.blueprints.service_ticket.serviceTicketSchemas import (
    service_ticket_schema, 
    service_tickets_schema,
    edit_ticket_mechanics_schema
)
from application.models import ServiceTicket, Mechanic, TicketMechanic, Part, TicketPart
from application.extensions import db, limiter


# CREATE - POST /service_tickets
@service_ticket_bp.route("", methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def create_service_ticket():
    if not request.json:
        return jsonify({"error": "No JSON data provided"}), 400
    
    try:
        ticket_data = cast(Dict[str, Any], service_ticket_schema.load(request.json))
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_ticket = ServiceTicket(**ticket_data)
    db.session.add(new_ticket)
    db.session.commit()
    return jsonify(service_ticket_schema.dump(new_ticket)), 201


# READ ALL - GET /service_tickets
@service_ticket_bp.route("", methods=['GET'])
@jwt_required()
def get_service_tickets():
    query = select(ServiceTicket)
    tickets = db.session.execute(query).scalars().all()
    return jsonify(service_tickets_schema.dump(tickets)), 200


# READ ONE - GET /service_tickets/<id>
@service_ticket_bp.route("/<int:ticket_id>", methods=['GET'])
@jwt_required()
def get_service_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    
    if ticket:
        return jsonify(service_ticket_schema.dump(ticket)), 200
    return jsonify({"error": "Service ticket not found."}), 404


# ASSIGN MECHANIC - PUT /service_tickets/<ticket_id>/assign-mechanic/<mechanic_id>
@service_ticket_bp.route("/<int:ticket_id>/assign-mechanic/<int:mechanic_id>", methods=['PUT'])
@jwt_required()
def assign_mechanic(ticket_id, mechanic_id):
    """
    Assigns a mechanic to a service ticket by creating a TicketMechanic relationship.
    
    Request body (optional):
    {
        "role": "Technician",       # Role for the mechanic (default: "Technician")
        "minutes_worked": 0          # Minutes worked (default: 0)
    }
    """
    # Verify service ticket exists
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found."}), 404
    
    # Verify mechanic exists
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404
    
    # Check if mechanic is already assigned to this ticket
    existing = db.session.execute(
        select(TicketMechanic).where(
            TicketMechanic.ticket_id == ticket_id,
            TicketMechanic.mechanic_id == mechanic_id
        )
    ).scalar_one_or_none()
    
    if existing:
        return jsonify({"error": "Mechanic is already assigned to this ticket."}), 400
    
    # Get role and minutes_worked from request body (optional)
    role = "Technician"
    minutes_worked = 0
    
    if request.json:
        role = request.json.get('role', 'Technician')
        minutes_worked = request.json.get('minutes_worked', 0)
    
    # Create the TicketMechanic relationship
    new_assignment = TicketMechanic(
        ticket_id=ticket_id,  # type: ignore
        mechanic_id=mechanic_id,  # type: ignore
        role=role,  # type: ignore
        minutes_worked=minutes_worked  # type: ignore
    )
    
    db.session.add(new_assignment)
    db.session.commit()
    
    return jsonify({
        "message": f"Mechanic {mechanic_id} successfully assigned to ticket {ticket_id}",
        "ticket_id": ticket_id,
        "mechanic_id": mechanic_id,
        "role": role,
        "minutes_worked": minutes_worked
    }), 200


# REMOVE MECHANIC - PUT /service_tickets/<ticket_id>/remove-mechanic/<mechanic_id>
@service_ticket_bp.route("/<int:ticket_id>/remove-mechanic/<int:mechanic_id>", methods=['PUT'])
@jwt_required()
def remove_mechanic(ticket_id, mechanic_id):
    """
    Removes a mechanic from a service ticket by deleting the TicketMechanic relationship.
    """
    # Verify service ticket exists
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found."}), 404
    
    # Verify mechanic exists
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404
    
    # Find the TicketMechanic relationship
    ticket_mechanic = db.session.execute(
        select(TicketMechanic).where(
            TicketMechanic.ticket_id == ticket_id,
            TicketMechanic.mechanic_id == mechanic_id
        )
    ).scalar_one_or_none()
    
    if not ticket_mechanic:
        return jsonify({"error": "Mechanic is not assigned to this ticket."}), 404
    
    # Remove the relationship
    db.session.delete(ticket_mechanic)
    db.session.commit()
    
    return jsonify({
        "message": f"Mechanic {mechanic_id} successfully removed from ticket {ticket_id}",
        "ticket_id": ticket_id,
        "mechanic_id": mechanic_id
    }), 200


# UPDATE MECHANICS - PUT /service_tickets/<id>/edit
# This endpoint allows adding and removing mechanics from a service ticket
# It demonstrates working with many-to-many relationships by manipulating the relationship list
@service_ticket_bp.route("/<int:ticket_id>/edit", methods=['PUT'])
@jwt_required()
def edit_ticket_mechanics(ticket_id):
    """
    Add or remove mechanics from a service ticket.
    
    Request body:
    {
        "add_ids": [1, 2, 3],      # List of mechanic IDs to add
        "remove_ids": [4, 5],       # List of mechanic IDs to remove
        "role": "Technician",       # Role for newly added mechanics (default: "Technician")
        "minutes_worked": 0         # Minutes worked for newly added mechanics (default: 0)
    }
    """
    ticket = db.session.get(ServiceTicket, ticket_id)
    
    if not ticket:
        return jsonify({"error": "Service ticket not found."}), 404
    
    if not request.json:
        return jsonify({"error": "No JSON data provided"}), 400
    
    try:
        data = cast(Dict[str, Any], edit_ticket_mechanics_schema.load(request.json))
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    add_ids = data.get('add_ids', [])
    remove_ids = data.get('remove_ids', [])
    role = data.get('role', 'Technician')
    minutes_worked = data.get('minutes_worked', 0)
    
    # Track changes for response message
    added_mechanics = []
    removed_mechanics = []
    errors = []
    
    # Remove mechanics from the ticket
    for mechanic_id in remove_ids:
        # Find the TicketMechanic association
        ticket_mechanic = db.session.execute(
            select(TicketMechanic).where(
                TicketMechanic.ticket_id == ticket_id,
                TicketMechanic.mechanic_id == mechanic_id
            )
        ).scalar_one_or_none()
        
        if ticket_mechanic:
            db.session.delete(ticket_mechanic)
            removed_mechanics.append(mechanic_id)
        else:
            errors.append(f"Mechanic {mechanic_id} is not assigned to this ticket")
    
    # Add mechanics to the ticket
    for mechanic_id in add_ids:
        # Check if mechanic exists
        mechanic = db.session.get(Mechanic, mechanic_id)
        if not mechanic:
            errors.append(f"Mechanic {mechanic_id} does not exist")
            continue
        
        # Check if mechanic is already assigned
        existing = db.session.execute(
            select(TicketMechanic).where(
                TicketMechanic.ticket_id == ticket_id,
                TicketMechanic.mechanic_id == mechanic_id
            )
        ).scalar_one_or_none()
        
        if existing:
            errors.append(f"Mechanic {mechanic_id} is already assigned to this ticket")
            continue
        
        # Create new TicketMechanic association
        new_ticket_mechanic = TicketMechanic(
            ticket_id=ticket_id,  # type: ignore
            mechanic_id=mechanic_id,  # type: ignore
            role=role,  # type: ignore
            minutes_worked=minutes_worked  # type: ignore
        )
        db.session.add(new_ticket_mechanic)
        added_mechanics.append(mechanic_id)
    
    db.session.commit()
    
    # Prepare response
    response = {
        "message": "Ticket mechanics updated successfully",
        "ticket_id": ticket_id,
        "added_mechanics": added_mechanics,
        "removed_mechanics": removed_mechanics
    }
    
    if errors:
        response["errors"] = errors
    
    return jsonify(response), 200


# UPDATE - PUT /service_tickets/<id>
@service_ticket_bp.route("/<int:ticket_id>", methods=['PUT'])
@jwt_required()
def update_service_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    
    if not ticket:
        return jsonify({"error": "Service ticket not found."}), 404
    
    if not request.json:
        return jsonify({"error": "No JSON data provided"}), 400
    
    try:
        ticket_data = cast(Dict[str, Any], service_ticket_schema.load(request.json))
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Update ticket attributes
    for key, value in ticket_data.items():
        setattr(ticket, key, value)
    
    db.session.commit()
    return jsonify(service_ticket_schema.dump(ticket)), 200


# ADD PART TO TICKET - POST /service_tickets/<ticket_id>/parts/<part_id>
@service_ticket_bp.route("/<int:ticket_id>/parts/<int:part_id>", methods=['POST'])
@jwt_required()
def add_part_to_ticket(ticket_id, part_id):
    """
    Add a part to a service ticket
    
    Request body:
    {
        "quantity_used": 2,
        "markup_percentage": 30.0,  # Optional, defaults to 30.0
        "warranty_months": 12,      # Optional
        "installed_by_mechanic_id": 1  # Optional
    }
    """
    # Verify service ticket exists
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    
    # Verify part exists
    part = db.session.get(Part, part_id)
    if not part:
        return jsonify({"error": "Part not found"}), 404
    
    # Check if part is already on this ticket
    existing = db.session.execute(
        select(TicketPart).where(
            TicketPart.ticket_id == ticket_id,
            TicketPart.part_id == part_id
        )
    ).scalar_one_or_none()
    
    if existing:
        return jsonify({"error": "Part is already added to this ticket"}), 400
    
    if not request.json or 'quantity_used' not in request.json:
        return jsonify({"error": "quantity_used is required"}), 400
    
    quantity_used = request.json['quantity_used']
    
    # Validate quantity
    try:
        quantity_used = int(quantity_used)
        if quantity_used <= 0:
            return jsonify({"error": "quantity_used must be positive"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "quantity_used must be a positive integer"}), 400
    
    # Check if enough parts in stock
    if part.quantity_in_stock < quantity_used:
        return jsonify({
            "error": "Insufficient parts in stock",
            "requested": quantity_used,
            "available": part.quantity_in_stock
        }), 400
    
    # Get optional fields
    markup_percentage = request.json.get('markup_percentage', 30.0)
    warranty_months = request.json.get('warranty_months')
    installed_by_mechanic_id = request.json.get('installed_by_mechanic_id')
    
    # Verify mechanic exists if provided
    if installed_by_mechanic_id:
        mechanic = db.session.get(Mechanic, installed_by_mechanic_id)
        if not mechanic:
            return jsonify({"error": f"Mechanic {installed_by_mechanic_id} not found"}), 404
    
    # Create TicketPart relationship
    ticket_part = TicketPart(
        ticket_id=ticket_id,
        part_id=part_id,
        quantity_used=quantity_used,
        unit_cost_cents=part.current_cost_cents,
        markup_percentage=markup_percentage,
        warranty_months=warranty_months,
        installed_by_mechanic_id=installed_by_mechanic_id
    )
    
    # Reduce part quantity in stock
    part.quantity_in_stock -= quantity_used
    
    db.session.add(ticket_part)
    db.session.commit()
    
    return jsonify({
        "message": "Part successfully added to ticket",
        "ticket_id": ticket_id,
        "part_id": part_id,
        "part_name": part.name,
        "quantity_used": quantity_used,
        "unit_cost_cents": part.current_cost_cents,
        "total_cost": ticket_part.get_total_cost(),
        "remaining_stock": part.quantity_in_stock
    }), 200


# DELETE - DELETE /service_tickets/<id>
@service_ticket_bp.route("/<int:ticket_id>", methods=['DELETE'])
@jwt_required()
def delete_service_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    
    if not ticket:
        return jsonify({"error": "Service ticket not found."}), 404
    
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({"message": f'Service ticket id: {ticket_id}, successfully deleted.'}), 200
