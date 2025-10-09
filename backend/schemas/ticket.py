# ==== backend/schemas/ticket.py ====
import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

# Re-import enums from models to ensure consistency and avoid direct model import in routers
class TicketStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"
    PENDING = "Pending"

class TicketPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class TicketBase(BaseModel):
    """Base schema for ticket data."""
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10)
    category: str = Field("Uncategorized", max_length=100)
    priority: TicketPriority = Field(TicketPriority.MEDIUM)
    status: TicketStatus = Field(TicketStatus.OPEN)
    sla_deadline: Optional[datetime] = None

class TicketCreate(TicketBase):
    """Schema for creating a new ticket."""
    # created_by will be set by the backend based on authenticated user
    pass

class TicketUpdate(BaseModel):
    """Schema for updating an existing ticket. All fields are optional."""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = Field(None, max_length=100)
    priority: Optional[TicketPriority] = Field(None)
    status: Optional[TicketStatus] = Field(None)
    sla_deadline: Optional[datetime] = None

class TicketResponse(TicketBase):
    """Schema for responding with ticket data, including generated fields."""
    ticket_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    created_by: str

    class Config:
        orm_mode = True # Enable Pydantic to read data from SQLAlchemy models