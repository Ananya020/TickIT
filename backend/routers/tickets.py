# ==== backend/routers/tickets.py ====
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from ..database.db_connect import get_db
from ..schemas.ticket import TicketCreate, TicketUpdate, TicketResponse
from ..models.ticket import Ticket
from ..utils.logger import setup_logging
from ..dependencies import get_current_user
from ..schemas.auth import UserPayload, UserRole

router = APIRouter()
logger = setup_logging()

@router.post("/create", response_model=TicketResponse, status_code=status.HTTP_201_CREATED,
             summary="Create a new ticket",
             response_description="The newly created ticket details.")
async def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user) # Only authenticated users can create
):
    """
    Creates a new incident ticket in the system.
    Requires authentication.
    """
    logger.info(f"User {current_user.email} attempting to create a ticket.")
    db_ticket = Ticket(**ticket.dict(), ticket_id=uuid.uuid4(), created_by=current_user.email)
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    logger.info(f"Ticket {db_ticket.ticket_id} created by {current_user.email}.")
    return db_ticket

@router.get("/all", response_model=List[TicketResponse],
            summary="Retrieve all tickets",
            response_description="A list of all tickets in the system.")
async def get_all_tickets(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserPayload = Depends(get_current_user) # Only authenticated users can view
):
    """
    Retrieves a list of all incident tickets, with pagination.
    Requires authentication.
    """
    logger.info(f"User {current_user.email} requesting all tickets (skip={skip}, limit={limit}).")
    tickets = db.query(Ticket).offset(skip).limit(limit).all()
    return tickets

@router.get("/{ticket_id}", response_model=TicketResponse,
            summary="Retrieve a ticket by ID",
            response_description="The ticket details for the given ID.")
async def get_ticket(
    ticket_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user) # Only authenticated users can view
):
    """
    Retrieves a specific incident ticket by its unique ID.
    Requires authentication.
    """
    logger.info(f"User {current_user.email} requesting ticket {ticket_id}.")
    db_ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if db_ticket is None:
        logger.warning(f"Ticket {ticket_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return db_ticket

@router.put("/update/{ticket_id}", response_model=TicketResponse,
            summary="Update an existing ticket",
            response_description="The updated ticket details.")
async def update_ticket(
    ticket_id: uuid.UUID,
    ticket_update: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user) # Only authenticated users can update
):
    """
    Updates an existing incident ticket identified by its ID.
    Requires authentication. Only 'Agent' and 'Admin' roles can update all fields.
    EndUsers might be restricted to specific fields (e.g., description, status change to 'Resolved' for their own tickets).
    For simplicity, this example allows agents/admins to update.
    """
    logger.info(f"User {current_user.email} attempting to update ticket {ticket_id}.")
    db_ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if db_ticket is None:
        logger.warning(f"Attempt to update non-existent ticket {ticket_id}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    # Basic authorization: Only admins/agents can update all fields
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        # Example of restricted update for EndUser: Only status change or description
        if ticket_update.status and db_ticket.created_by != current_user.email:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this ticket's status.")
        if any([
            ticket_update.category, ticket_update.priority, ticket_update.sla_deadline # Restricted fields
        ]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update these fields.")
    
    update_data = ticket_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_ticket, key, value)
    db_ticket.updated_at = datetime.utcnow() # Update timestamp
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    logger.info(f"Ticket {ticket_id} updated by {current_user.email}.")
    return db_ticket

@router.delete("/delete/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete a ticket",
               response_description="No content upon successful deletion.")
async def delete_ticket(
    ticket_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    """
    Deletes an incident ticket by its ID.
    Requires 'Admin' role authentication.
    """
    if current_user.role != UserRole.ADMIN:
        logger.warning(f"User {current_user.email} with role {current_user.role} attempted to delete ticket {ticket_id} (Forbidden).")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can delete tickets.")

    logger.info(f"Admin user {current_user.email} attempting to delete ticket {ticket_id}.")
    db_ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if db_ticket is None:
        logger.warning(f"Attempt to delete non-existent ticket {ticket_id}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    db.delete(db_ticket)
    db.commit()
    logger.info(f"Ticket {ticket_id} deleted by {current_user.email}.")
    return