# ==== backend/schemas/ticket.py ====
import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from enum import Enum


# --- Enums for consistency ---
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


# --- Base Schema ---
class TicketBase(BaseModel):
    """Base schema for ticket data."""
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10)
    category: str = Field("Uncategorized", max_length=100)
    priority: TicketPriority = Field(default=TicketPriority.MEDIUM)
    status: TicketStatus = Field(default=TicketStatus.OPEN)
    sla_deadline: Optional[datetime] = None


# --- Create Schema ---
class TicketCreate(TicketBase):
    """Schema for creating a new ticket."""
    pass  # created_by will be set in the backend


# --- Update Schema ---
class TicketUpdate(BaseModel):
    """Schema for updating an existing ticket. All fields are optional."""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = Field(None, max_length=100)
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    sla_deadline: Optional[datetime] = None


# --- Response Schema ---
class TicketResponse(TicketBase):
    """Schema for responding with ticket data, including generated fields."""
    ticket_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    created_by: str

    # ✅ Pydantic v2: replaces `orm_mode = True`
    model_config = ConfigDict(from_attributes=True)


# --- Paginated Response ---
class TicketsResponse(BaseModel):
    """Paginated response for a list of tickets."""
    items: List[TicketResponse]
    page: int
    pageSize: int
    total: int
