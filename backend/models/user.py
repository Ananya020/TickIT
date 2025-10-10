# ==== backend/models/user.py ====
from sqlalchemy import Column, String
from ..database.db_connect import Base
from enum import Enum


class UserRole(str, Enum):
    """Enum for user roles."""
    ADMIN = "admin"
    AGENT = "agent"
    ENDUSER = "enduser"


class User(Base):
    """
    SQLAlchemy model for a user.
    """
    __tablename__ = "users"

    id = Column(String(255), primary_key=True, index=True)  # Using email as ID for simplicity
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default=UserRole.ENDUSER.value, nullable=False)

    def __init__(self, email: str, hashed_password: str, role: str = UserRole.ENDUSER.value):
        self.id = email
        self.email = email
        self.hashed_password = hashed_password
        self.role = role

    def __repr__(self):
        return f"<User(email='{self.email}', role='{self.role}')>"
