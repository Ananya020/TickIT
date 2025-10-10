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

router = APIRouter()
logger = setup_logging()


# ============================================================
# 1️⃣ DASHBOARD METRICS
# ============================================================
@router.get(
    "/metrics",
    summary="Get key performance metrics for the dashboard",
    response_description="Total tickets, open tickets, closed tickets, and mean time to resolution."
)
async def get_dashboard_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Retrieves key metrics for the dashboard, including total tickets,
    open tickets, closed tickets, and mean time to resolution (MTTR).
    Public endpoint.
    """
    logger.info("Dashboard metrics requested.")

    total_tickets = db.query(Ticket).count()
    open_tickets = db.query(Ticket).filter(Ticket.status != TicketStatus.RESOLVED).count()
    closed_tickets = db.query(Ticket).filter(Ticket.status == TicketStatus.RESOLVED).count()

    # Calculate Mean Time To Resolution (MTTR)
    resolved_tickets = db.query(Ticket).filter(
        Ticket.status == TicketStatus.RESOLVED, Ticket.updated_at != None
    ).all()

    total_resolution_time_seconds = 0
    resolved_count_for_mttr = 0

    for ticket in resolved_tickets:
        if ticket.created_at and ticket.updated_at:
            time_diff = (ticket.updated_at - ticket.created_at).total_seconds()
            total_resolution_time_seconds += time_diff
            resolved_count_for_mttr += 1

    mttr_hours = (
        total_resolution_time_seconds / resolved_count_for_mttr / 3600
        if resolved_count_for_mttr > 0
        else 0
    )

    metrics = {
        "totalTickets": total_tickets,
        "openTickets": open_tickets,
        "resolvedToday": closed_tickets,
        "avgResolutionTimeHours": round(mttr_hours, 2),
    }

    logger.info(f"Dashboard metrics response: {metrics}")
    return metrics


# ============================================================
# 2️⃣ HEATMAP MOCK DATA
# ============================================================
@router.get(
    "/heatmap",
    summary="Get mock data for geographical/category distribution heatmap",
    response_description="Mock data representing ticket distribution by location or category."
)
async def get_dashboard_heatmap_data() -> Dict[str, Any]:
    """
    Provides mock data suitable for displaying a heatmap,
    e.g., ticket distribution by geographical region or by category density.
    Public endpoint.
    """
    logger.info("Dashboard heatmap data requested.")

    mock_geo_data = [
    {"lat": 34.052235, "lon": -118.243683, "value": random.randint(10, 100), "city": "Los Angeles"},
    {"lat": 51.507351, "lon": -0.127758, "value": random.randint(10, 100), "city": "London"},
    {"lat": 35.689487, "lon": 139.691711, "value": random.randint(10, 100), "city": "Tokyo"},
    {"lat": -33.868820, "lon": 151.209290, "value": random.randint(10, 100), "city": "Sydney"},
    {"lat": 40.712776, "lon": -74.005974, "value": random.randint(10, 100), "city": "New York"},
    {"lat": 48.856613, "lon": 2.352222, "value": random.randint(10, 100), "city": "Paris"},
    {"lat": 55.755825, "lon": 37.617298, "value": random.randint(10, 100), "city": "Moscow"},
    {"lat": 19.432608, "lon": -99.133209, "value": random.randint(10, 100), "city": "Mexico City"},
    {"lat": -23.550520, "lon": -46.633308, "value": random.randint(10, 100), "city": "São Paulo"},
    {"lat": 1.352083, "lon": 103.819839, "value": random.randint(10, 100), "city": "Singapore"},
    {"lat": 31.230391, "lon": 121.473701, "value": random.randint(10, 100), "city": "Shanghai"},
    {"lat": 28.613939, "lon": 77.209023, "value": random.randint(10, 100), "city": "New Delhi"},
    {"lat": 41.902782, "lon": 12.496366, "value": random.randint(10, 100), "city": "Rome"},
    {"lat": 37.774929, "lon": -122.419418, "value": random.randint(10, 100), "city": "San Francisco"},
    {"lat": 52.520008, "lon": 13.404954, "value": random.randint(10, 100), "city": "Berlin"},
    {"lat": 59.329323, "lon": 18.068581, "value": random.randint(10, 100), "city": "Stockholm"},
    {"lat": -26.204103, "lon": 28.047305, "value": random.randint(10, 100), "city": "Johannesburg"},
    {"lat": 43.653225, "lon": -79.383186, "value": random.randint(10, 100), "city": "Toronto"},
    {"lat": 39.904202, "lon": 116.407394, "value": random.randint(10, 100), "city": "Beijing"},
    {"lat": 35.6762, "lon": 139.6503, "value": random.randint(10, 100), "city": "Tokyo"},
]


    logger.info("Generated mock heatmap data.")
    return {"type": "geographic", "data": mock_geo_data}


# ============================================================
# 3️⃣ TICKET TRENDS (FOR RECHARTS)
# ============================================================
@router.get(
    "/trends",
    summary="Get ticket trends over time",
    response_description="Daily open vs resolved ticket counts"
)
async def get_dashboard_trends_data(
    db: Session = Depends(get_db),
    days: int = 30
) -> List[Dict[str, Any]]:
    """
    Returns daily ticket trend data for charting.
    Each point has { date, open, resolved }.
    Public endpoint.
    """
    logger.info(f"Dashboard trends requested for last {days} days.")

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Initialize all days with zero counts
    daily_data = {
        (start_date + timedelta(days=i)).date().isoformat(): {"open": 0, "resolved": 0}
        for i in range(days + 1)
    }

    tickets = db.query(Ticket).filter(Ticket.created_at >= start_date).all()

    for t in tickets:
        date_key = t.created_at.date().isoformat()
        if date_key in daily_data:
            if t.status == TicketStatus.RESOLVED:
                daily_data[date_key]["resolved"] += 1
            else:
                daily_data[date_key]["open"] += 1

    trend_list = [
        {"date": d, "open": v["open"], "resolved": v["resolved"]}
        for d, v in sorted(daily_data.items())
    ]

    logger.info("Generated daily ticket trends for dashboard.")
    return trend_list
