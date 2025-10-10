# ==== backend/models/ticket.py ====
import uuid
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.mysql import CHAR
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

    # Use CHAR(36) instead of PostgreSQL UUID (MySQL-safe)
    ticket_id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False, index=True)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), default="Uncategorized")
    priority = Column(String(50), default=TicketPriority.MEDIUM.value)
    status = Column(String(50), default=TicketStatus.OPEN.value)

    sla_deadline = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    created_by = Column(String(255), nullable=False, default="system")

    def __repr__(self):
        return f"<Ticket(id={self.ticket_id}, title='{self.title}', status='{self.status}')>"
