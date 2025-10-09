# ==== backend/database/db_connect.py ====
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import logging

# Configure logging for the database connection
db_logger = logging.getLogger(__name__)
db_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
db_logger.addHandler(handler)

# Database connection URL from environment variables
# Default to SQLite for easy local development, or PostgreSQL for production
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tickit.db")

db_logger.info(f"Connecting to database at: {SQLALCHEMY_DATABASE_URL.split('://')[0]}://***")

# Determine engine arguments based on database type
connect_args = {}
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    connect_args["check_same_thread"] = False
    # Use StaticPool for SQLite with FastAPI to prevent issues with multiple threads accessing the same connection
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args=connect_args,
        poolclass=StaticPool
    )
else:
    # For PostgreSQL, use a standard connection pool
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True # Ensures connections are still alive
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Dependency to provide a database session for each request.
    Ensures the session is closed after the request is processed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()