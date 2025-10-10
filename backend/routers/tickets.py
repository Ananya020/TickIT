# ==== backend/routers/tickets.py ====
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from ..database.db_connect import get_db
from ..schemas.ticket import TicketCreate, TicketUpdate, TicketResponse, TicketsResponse
from ..models.ticket import Ticket
from ..utils.logger import setup_logging
from ..dependencies import get_current_user
from ..schemas.auth import UserPayload, UserRole

router = APIRouter()
logger = setup_logging()

# ----------------------------
# CREATE TICKET
# ----------------------------
@router.post("/create", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    logger.info(f"User {current_user.email} attempting to create a ticket.")
    db_ticket = Ticket(
        **ticket.dict(),
        ticket_id=uuid.uuid4(),
        created_by=current_user.email,
        created_at=datetime.utcnow()
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    logger.info(f"Ticket {db_ticket.ticket_id} created by {current_user.email}.")
    return TicketResponse.model_validate(db_ticket)  # <-- v2 fix

# ----------------------------
# GET ALL TICKETS (paginated)
# ----------------------------
@router.get("/all", response_model=TicketsResponse)
async def get_all_tickets(
    db: Session = Depends(get_db),
    query: str = "",
    status_filter: str = "All",
    priority_filter: str = "All",
    page: int = 1,
    page_size: int = 20,
    current_user: UserPayload = Depends(get_current_user)
):
    tickets_query = db.query(Ticket)

    if query:
        tickets_query = tickets_query.filter(Ticket.title.ilike(f"%{query}%"))

    if status_filter != "All":
        tickets_query = tickets_query.filter(Ticket.status == status_filter)

    if priority_filter != "All":
        tickets_query = tickets_query.filter(Ticket.priority == priority_filter)

    total = tickets_query.count()
    tickets = tickets_query.order_by(Ticket.created_at.desc()) \
                           .offset((page - 1) * page_size) \
                           .limit(page_size) \
                           .all()

    return TicketsResponse(
        items=[TicketResponse.model_validate(t) for t in tickets],  # <-- v2 fix
        page=page,
        pageSize=page_size,
        total=total
    )

# ----------------------------
# GET TICKET BY ID
# ----------------------------
@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    logger.info(f"User {current_user.email} requesting ticket {ticket_id}.")
    db_ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if db_ticket is None:
        logger.warning(f"Ticket {ticket_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return TicketResponse.model_validate(db_ticket)  # <-- v2 fix

# ----------------------------
# UPDATE TICKET
# ----------------------------
@router.put("/update/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: uuid.UUID,
    ticket_update: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    db_ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if db_ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        # Restrict EndUser updates
        if ticket_update.status and db_ticket.created_by != current_user.email:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this ticket's status.")
        if any([ticket_update.category, ticket_update.priority, ticket_update.sla_deadline]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update these fields.")

    for key, value in ticket_update.dict(exclude_unset=True).items():
        setattr(db_ticket, key, value)
    db_ticket.updated_at = datetime.utcnow()

    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return TicketResponse.model_validate(db_ticket)  # <-- v2 fix

# ----------------------------
# DELETE TICKET
# ----------------------------
@router.delete("/delete/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(
    ticket_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can delete tickets.")

    db_ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if db_ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    db.delete(db_ticket)
    db.commit()
    return
