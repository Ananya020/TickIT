# ==== backend/utils/seed_data.py ====
import uuid
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session

from ..models.ticket import Ticket, TicketStatus, TicketPriority
from ..models.user import User, UserRole
from ..utils.auth_utils import get_password_hash # Import for hashing default passwords
from ..utils.logger import setup_logging

logger = setup_logging()

def seed_initial_data(db: Session):
    """
    Seeds the database with initial users and synthetic ticket data.
    This function should only be called if the database is empty.
    """
    logger.info("Starting to seed initial data...")

    # --- Seed Users ---
    if db.query(User).count() == 0:
        logger.info("No users found, creating default users...")
        users_to_create = [
            User(email="admin@example.com", hashed_password=get_password_hash("adminpass"), role=UserRole.ADMIN.value),
            User(email="agent@example.com", hashed_password=get_password_hash("agentpass"), role=UserRole.AGENT.value),
            User(email="user1@example.com", hashed_password=get_password_hash("userpass"), role=UserRole.ENDUSER.value),
            User(email="user2@example.com", hashed_password=get_password_hash("userpass"), role=UserRole.ENDUSER.value),
        ]
        db.add_all(users_to_create)
        db.commit()
        for user in users_to_create:
            db.refresh(user)
        logger.info(f"Created {len(users_to_create)} default users.")
    else:
        logger.info("Users already exist, skipping user seeding.")

    # --- Seed Tickets ---
    if db.query(Ticket).count() == 0:
        logger.info("No tickets found, generating synthetic ticket data...")

        categories = ["Software Issue", "Hardware Failure", "Network Problem", "Account Management", "Security Incident", "Performance Issue", "Data Request"]
        priorities = [TicketPriority.LOW, TicketPriority.MEDIUM, TicketPriority.HIGH, TicketPriority.CRITICAL]
        statuses = [TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED, TicketStatus.CLOSED, TicketStatus.PENDING]
        
        ticket_descriptions = [
            "Application is crashing frequently after recent update.",
            "Laptop not powering on, completely unresponsive.",
            "Cannot connect to VPN from home office, all other internet works.",
            "Need password reset for my HR portal account.",
            "Suspicious email received, looks like phishing.",
            "Database queries are running very slow, impacting reports.",
            "Request for new user account setup for John Doe.",
            "Printer in department X is offline and not responding.",
            "Shared drive access denied for user Jane Smith.",
            "Web server returning 500 internal server error for all requests.",
            "Monitor flickering continuously, tried reseating cables.",
            "External website is unreachable from company network.",
            "Request to upgrade software license for Adobe Creative Suite.",
            "Unauthorized access attempt detected on file server.",
            "High CPU usage on critical production server.",
            "Unable to log into my email, receiving authentication error.",
        ]

        agent_users = db.query(User).filter(User.role == UserRole.AGENT.value).all()
        end_users = db.query(User).filter(User.role == UserRole.ENDUSER.value).all()
        all_emails = [u.email for u in (agent_users + end_users)] # For created_by field

        tickets = []
        for i in range(50): # Generate 50 synthetic tickets
            created_at = datetime.utcnow() - timedelta(days=random.randint(1, 60), hours=random.randint(0, 23))
            
            status = random.choice(statuses)
            
            # Ensure sensible created_at and updated_at for resolved/closed tickets
            updated_at = None
            if status in [TicketStatus.RESOLVED, TicketStatus.CLOSED]:
                updated_at = created_at + timedelta(hours=random.randint(4, 72))
                if updated_at > datetime.utcnow(): # Don't make future resolved tickets
                    updated_at = datetime.utcnow() - timedelta(hours=random.randint(1, 3)) # Ensure past

            priority = random.choice(priorities)
            category = random.choice(categories)
            
            # Calculate SLA deadline based on priority (mock values)
            sla_hours = {
                TicketPriority.CRITICAL: 4,
                TicketPriority.HIGH: 8,
                TicketPriority.MEDIUM: 24,
                TicketPriority.LOW: 48,
            }[priority]
            sla_deadline = created_at + timedelta(hours=sla_hours)

            # Ensure some tickets are by end-users
            created_by = random.choice(all_emails)
            
            ticket = Ticket(
                ticket_id=uuid.uuid4(),
                title=f"Issue {i+1}: {random.choice(ticket_descriptions).split(',')[0]}",
                description=random.choice(ticket_descriptions) + f" (Ticket generated for {category} / {priority.value})",
                category=category,
                priority=priority.value,
                status=status.value,
                sla_deadline=sla_deadline,
                created_at=created_at,
                updated_at=updated_at if updated_at else created_at,
                created_by=created_by
            )
            tickets.append(ticket)

        db.add_all(tickets)
        db.commit()
        for ticket in tickets:
            db.refresh(ticket)
        logger.info(f"Generated {len(tickets)} synthetic tickets.")
    else:
        logger.info("Tickets already exist, skipping ticket seeding.")

    logger.info("Initial data seeding complete.")