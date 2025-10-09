# ==== backend/models/ticket_crud.py ====
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models.ticket import Ticket, TicketStatus, TicketPriority
from ..schemas.ticket import TicketCreate, TicketUpdate
from ..utils.logger import setup_logging

logger = setup_logging()

def get_ticket_by_id(db: Session, ticket_id: uuid.UUID) -> Optional[Ticket]:
    """
    Retrieves a single ticket by its UUID.
    """
    return db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()

def get_all_tickets(db: Session, skip: int = 0, limit: int = 100) -> List[Ticket]:
    """
    Retrieves all tickets with optional pagination.
    """
    return db.query(Ticket).order_by(desc(Ticket.created_at)).offset(skip).limit(limit).all()

def create_ticket(db: Session, ticket: TicketCreate, created_by_email: str) -> Ticket:
    """
    Creates a new ticket in the database.
    """
    db_ticket = Ticket(
        ticket_id=uuid.uuid4(),
        title=ticket.title,
        description=ticket.description,
        category=ticket.category,
        priority=ticket.priority.value, # Store enum value as string
        status=ticket.status.value,     # Store enum value as string
        sla_deadline=ticket.sla_deadline,
        created_by=created_by_email
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    logger.info(f"Ticket {db_ticket.ticket_id} created by {created_by_email}.")
    return db_ticket

def update_ticket(db: Session, db_ticket: Ticket, ticket_update: TicketUpdate) -> Ticket:
    """
    Updates an existing ticket with new data.
    """
    update_data = ticket_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if key == "priority" or key == "status": # Handle enums
            setattr(db_ticket, key, value.value)
        else:
            setattr(db_ticket, key, value)
    
    db_ticket.updated_at = datetime.utcnow() # Automatically update timestamp
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    logger.info(f"Ticket {db_ticket.ticket_id} updated.")
    return db_ticket

def delete_ticket(db: Session, db_ticket: Ticket):
    """
    Deletes a ticket from the database.
    """
    ticket_id = db_ticket.ticket_id
    db.delete(db_ticket)
    db.commit()
    logger.info(f"Ticket {ticket_id} deleted.")