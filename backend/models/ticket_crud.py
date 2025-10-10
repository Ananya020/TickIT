# ==== backend/models/ticket_crud.py ====
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models.ticket import Ticket
from ..schemas.ticket import TicketCreate, TicketUpdate
from ..utils.logger import setup_logging

logger = setup_logging()

def create_ticket(db: Session, ticket: TicketCreate, created_by_email: str) -> Ticket:
    """
    Creates a new ticket record in the database.

    Args:
        db (Session): The SQLAlchemy database session.
        ticket (TicketCreate): The Pydantic schema containing the new ticket's data.
        created_by_email (str): The email of the user creating the ticket.

    Returns:
        Ticket: The newly created SQLAlchemy Ticket object.
    """
    # Create a new SQLAlchemy Ticket model instance from the Pydantic schema
    db_ticket = Ticket(
        ticket_id=uuid.uuid4(),  # Generate a new unique ID
        title=ticket.title,
        description=ticket.description,
        category=ticket.category,
        priority=ticket.priority.value,   # Store the string value of the enum
        status=ticket.status.value,       # Store the string value of the enum
        sla_deadline=ticket.sla_deadline,
        created_by=created_by_email
    )
    
    # Add the new ticket to the session, commit it to the database,
    # and refresh the instance to get any new data from the DB (like defaults)
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    
    logger.info(f"Ticket {db_ticket.ticket_id} created by user {created_by_email}.")
    return db_ticket

def get_ticket_by_id(db: Session, ticket_id: uuid.UUID) -> Optional[Ticket]:
    """
    Retrieves a single ticket from the database by its unique ID.

    Args:
        db (Session): The SQLAlchemy database session.
        ticket_id (uuid.UUID): The unique identifier of the ticket.

    Returns:
        Optional[Ticket]: The SQLAlchemy Ticket object if found, otherwise None.
    """
    return db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()

def get_all_tickets(db: Session, skip: int = 0, limit: int = 100) -> List[Ticket]:
    """
    Retrieves a list of all tickets from the database with pagination.
    Tickets are ordered by creation date, with the newest first.

    Args:
        db (Session): The SQLAlchemy database session.
        skip (int): The number of records to skip (for pagination).
        limit (int): The maximum number of records to return.

    Returns:
        List[Ticket]: A list of SQLAlchemy Ticket objects.
    """
    return db.query(Ticket).order_by(desc(Ticket.created_at)).offset(skip).limit(limit).all()

def update_ticket(db: Session, db_ticket: Ticket, ticket_update: TicketUpdate) -> Ticket:
    """
    Updates an existing ticket record in the database.

    Args:
        db (Session): The SQLAlchemy database session.
        db_ticket (Ticket): The existing SQLAlchemy Ticket object to update.
        ticket_update (TicketUpdate): The Pydantic schema containing the fields to update.

    Returns:
        Ticket: The updated SQLAlchemy Ticket object.
    """
    # Get the update data from the Pydantic model, excluding any fields that were not set
    update_data = ticket_update.dict(exclude_unset=True)
    
    # Iterate over the provided data and update the model's attributes
    for key, value in update_data.items():
        # For enum fields, make sure to store their string value
        if key in ("priority", "status") and value is not None:
            setattr(db_ticket, key, value.value)
        else:
            setattr(db_ticket, key, value)
            
    # Manually set the updated_at timestamp to the current time
    db_ticket.updated_at = datetime.utcnow()
    
    # Add the changes to the session and commit them to the database
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    
    logger.info(f"Ticket {db_ticket.ticket_id} has been updated.")
    return db_ticket

def delete_ticket(db: Session, db_ticket: Ticket) -> None:
    """
    Deletes a ticket record from the database.

    Args:
        db (Session): The SQLAlchemy database session.
        db_ticket (Ticket): The SQLAlchemy Ticket object to delete.
    """
    ticket_id_to_log = db_ticket.ticket_id
    
    # Mark the object for deletion and commit the transaction
    db.delete(db_ticket)
    db.commit()
    
    logger.info(f"Ticket {ticket_id_to_log} has been deleted.")