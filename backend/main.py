# ==== backend/main.py ====
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import AsyncGenerator

from .database.db_connect import get_db, engine
from .database import init_db
from .routers import tickets, classify, recommend, sla, anomaly, chatbot, dashboard, auth
from .utils.logger import setup_logging
from .utils.seed_data import seed_initial_data

# Set up logging
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Handles startup and shutdown events for the application.
    Initializes the database and seeds data on startup.
    """
    logger.info("Application startup event triggered.")
    try:
        init_db.create_tables()
        logger.info("Database tables created successfully.")

        # Seed initial data if the database is empty
        with Session(engine) as session:
            # Check if any tickets exist
            from .models.ticket import Ticket  # Import here to avoid circular dependency issues during startup
            if session.query(Ticket).count() == 0:
                logger.info("Database is empty, seeding initial data...")
                seed_initial_data(session)
                logger.info("Initial data seeded successfully.")
            else:
                logger.info("Database already contains data, skipping seeding.")
    except Exception as e:
        logger.error(f"Error during database initialization or seeding: {e}")
        # Depending on severity, you might want to raise the exception or exit

    yield
    logger.info("Application shutdown event triggered.")
    # Add any cleanup tasks here if necessary

app = FastAPI(
    title="TickIT AI Incident Management Backend",
    description="An AI-powered platform for automated IT incident management, featuring ticket classification, resolution recommendations, SLA prediction, and anomaly detection.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
origins = [
    os.getenv("FRONTEND_URL", "http://localhost:3000"),  # Allow your frontend to connect
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(tickets.router, prefix="/tickets", tags=["Ticket Management"])
app.include_router(classify.router, prefix="/classify", tags=["AI: Classification"])
app.include_router(recommend.router, prefix="/recommend", tags=["AI: Recommendation"])
app.include_router(sla.router, prefix="/sla", tags=["AI: SLA Prediction"])
app.include_router(anomaly.router, prefix="/anomaly", tags=["AI: Anomaly Detection"])
app.include_router(chatbot.router, prefix="/chat", tags=["AI: Conversational Assistant"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Analytics & Dashboard"])

@app.get("/", summary="Root endpoint for API status check")
async def root():
    """
    Root endpoint to check if the API is running.
    """
    logger.info("Root endpoint accessed.")
    return {"message": "Welcome to TickIT AI Incident Management API!"}