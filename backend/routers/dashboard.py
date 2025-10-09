# ==== backend/routers/dashboard.py ====
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random

from ..database.db_connect import get_db
from ..models.ticket import Ticket
from ..schemas.ticket import TicketStatus, TicketPriority
from ..utils.logger import setup_logging
from ..dependencies import get_current_user, require_roles
from ..schemas.auth import UserRole

router = APIRouter()
logger = setup_logging()

@router.get("/metrics",
            summary="Get key performance metrics for the dashboard",
            response_description="Total tickets, open tickets, closed tickets, and mean time to resolution.",
            dependencies=[Depends(require_roles([UserRole.AGENT, UserRole.ADMIN]))])
async def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retrieves key metrics for the dashboard, including total tickets,
    open tickets, closed tickets, and mean time to resolution (MTTR).
    Requires 'Agent' or 'Admin' role.
    """
    logger.info(f"User {current_user['email']} requested dashboard metrics.")

    total_tickets = db.query(Ticket).count()
    open_tickets = db.query(Ticket).filter(Ticket.status != TicketStatus.RESOLVED).count()
    closed_tickets = db.query(Ticket).filter(Ticket.status == TicketStatus.RESOLVED).count()

    # Calculate Mean Time To Resolution (MTTR)
    resolved_tickets = db.query(Ticket).filter(Ticket.status == TicketStatus.RESOLVED, Ticket.updated_at != None).all()
    
    total_resolution_time_seconds = 0
    resolved_count_for_mttr = 0
    for ticket in resolved_tickets:
        if ticket.created_at and ticket.updated_at:
            time_diff = (ticket.updated_at - ticket.created_at).total_seconds()
            total_resolution_time_seconds += time_diff
            resolved_count_for_mttr += 1

    mttr_hours = (total_resolution_time_seconds / resolved_count_for_mttr / 3600) if resolved_count_for_mttr > 0 else 0

    metrics = {
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "closed_tickets": closed_tickets,
        "mean_time_to_resolution_hours": round(mttr_hours, 2)
    }
    logger.info(f"Dashboard metrics: {metrics}")
    return metrics

@router.get("/heatmap",
            summary="Get mock data for geographical/category distribution heatmap",
            response_description="Mock data representing ticket distribution by location or category.",
            dependencies=[Depends(require_roles([UserRole.AGENT, UserRole.ADMIN]))])
async def get_dashboard_heatmap_data(
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Provides mock data suitable for displaying a heatmap,
    e.g., ticket distribution by geographical region or by category density.
    Requires 'Agent' or 'Admin' role.
    """
    logger.info(f"User {current_user['email']} requested dashboard heatmap data.")

    # Mock geographical regions
    regions = ["North America", "Europe", "Asia", "South America", "Africa", "Australia"]
    categories = ["Software Issue", "Hardware Failure", "Network Problem", "Account Management"]

    # Generate mock data points
    heatmap_data = []
    for _ in range(20): # 20 mock data points
        region = random.choice(regions)
        category = random.choice(categories)
        value = random.randint(5, 50) # Mock intensity/count

        heatmap_data.append({
            "region": region,
            "category": category,
            "value": value
        })
    
    # Alternatively, for a simple geo heatmap:
    mock_geo_data = [
        {"lat": 34.052235, "lon": -118.243683, "value": random.randint(10, 100), "city": "Los Angeles"},
        {"lat": 51.507351, "lon": -0.127758, "value": random.randint(10, 100), "city": "London"},
        {"lat": 35.689487, "lon": 139.691711, "value": random.randint(10, 100), "city": "Tokyo"},
        {"lat": -33.868820, "lon": 151.209290, "value": random.randint(10, 100), "city": "Sydney"},
        {"lat": 40.712776, "lon": -74.005974, "value": random.randint(10, 100), "city": "New York"},
    ]

    logger.info("Generated mock heatmap data.")
    return {
        "type": "geographic", # Or "category_distribution"
        "data": mock_geo_data
    }

@router.get("/trends",
            summary="Get ticket trends over time by date and category",
            response_description="Data for visualizing ticket creation trends and category breakdown.",
            dependencies=[Depends(require_roles([UserRole.AGENT, UserRole.ADMIN]))])
async def get_dashboard_trends_data(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    days: int = 30 # Number of days to look back
) -> Dict[str, Any]:
    """
    Retrieves data for visualizing ticket creation trends over time and
    the distribution of tickets by category.
    Requires 'Agent' or 'Admin' role.
    """
    logger.info(f"User {current_user['email']} requested dashboard trends for last {days} days.")

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Fetch tickets within the date range
    recent_tickets = db.query(Ticket).filter(Ticket.created_at >= start_date).all()

    # Aggregate by date
    daily_trends = {}
    for i in range(days + 1):
        current_date = (start_date + timedelta(days=i)).date()
        daily_trends[current_date.isoformat()] = 0

    for ticket in recent_tickets:
        ticket_date = ticket.created_at.date().isoformat()
        if ticket_date in daily_trends:
            daily_trends[ticket_date] += 1
    
    # Aggregate by category
    category_distribution = {}
    for ticket in recent_tickets:
        category_distribution[ticket.category] = category_distribution.get(ticket.category, 0) + 1

    logger.info(f"Generated dashboard trends data for {days} days.")
    return {
        "ticket_volume_by_date": [{"date": k, "count": v} for k, v in sorted(daily_trends.items())],
        "ticket_volume_by_category": [{"category": k, "count": v} for k, v in category_distribution.items()]
    }