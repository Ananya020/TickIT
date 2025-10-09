# ==== backend/models/ticket.py ====
import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from enum import Enum

from ..database.db_connect import Base

class TicketStatus(str, Enum):
    """Enum for possible ticket statuses."""
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"
    PENDING = "Pending"

class TicketPriority(str, Enum):
    """Enum for possible ticket priorities."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class Ticket(Base):
    """
    SQLAlchemy model for an incident ticket.
    """
    __tablename__ = "tickets"

    ticket_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, default="Uncategorized", nullable=False) # e.g., Software Issue, Hardware Failure
    priority = Column(String, default=TicketPriority.MEDIUM.value, nullable=False) # e.g., Low, Medium, High, Critical
    status = Column(String, default=TicketStatus.OPEN.value, nullable=False) # e.g., Open, In Progress, Resolved, Closed
    
    sla_deadline = Column(DateTime, nullable=True) # Service Level Agreement deadline
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    created_by = Column(String, nullable=False) # Email of the user who created the ticket

    def __repr__(self):
        return f"<Ticket(id={self.ticket_id}, title='{self.title}', status='{self.status}')>"