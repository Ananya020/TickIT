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
    title: str = Field(..., min_length=5, max_length=200, example="My application is slow")
    description: str = Field(..., min_length=10, example="The accounting software is extremely slow, freezing every few minutes. I cannot get my reports done.")
    category: str = Field("Uncategorized", max_length=100, example="Software Issue")
    priority: TicketPriority = Field(TicketPriority.MEDIUM, example="High")
    status: TicketStatus = Field(TicketStatus.OPEN, example="In Progress")
    sla_deadline: Optional[datetime] = Field(None, example="2024-06-01T10:00:00Z")

class TicketCreate(TicketBase):
    """Schema for creating a new ticket."""
    # created_by will be set by the backend based on authenticated user
    pass

class TicketUpdate(BaseModel):
    """Schema for updating an existing ticket. All fields are optional."""
    title: Optional[str] = Field(None, min_length=5, max_length=200, example="My application is still slow")
    description: Optional[str] = Field(None, min_length=10, example="Still freezing, even after restart.")
    category: Optional[str] = Field(None, max_length=100, example="Software Issue")
    priority: Optional[TicketPriority] = Field(None, example="Critical")
    status: Optional[TicketStatus] = Field(None, example="Resolved")
    sla_deadline: Optional[datetime] = Field(None, example="2024-05-30T10:00:00Z")

class TicketResponse(TicketBase):
    """Schema for responding with ticket data, including generated fields."""
    ticket_id: uuid.UUID = Field(..., example="a1b2c3d4-e5f6-7890-1234-567890abcdef")
    created_at: datetime = Field(..., example="2024-05-29T14:30:00.123456Z")
    updated_at: datetime = Field(..., example="2024-05-29T15:00:00.123456Z")
    created_by: str = Field(..., example="user@example.com")

    class Config:
        orm_mode = True # Enable Pydantic to read data from SQLAlchemy models