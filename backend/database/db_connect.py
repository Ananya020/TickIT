# ==== backend/database/db_connect.py ====
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import logging

# Configure logging
db_logger = logging.getLogger(__name__)
db_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
db_logger.addHandler(handler)

# Get database URL from environment variables
# Default to SQLite for local dev
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tickit.db")

db_logger.info(f"Connecting to database: {SQLALCHEMY_DATABASE_URL.split('://')[0]}://***")

# Engine creation logic depending on DB type
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
elif SQLALCHEMY_DATABASE_URL.startswith("mysql"):
    # For MySQL (PlanetScale, Railway, local)
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )
elif SQLALCHEMY_DATABASE_URL.startswith("postgresql"):
    # For PostgreSQL
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )
else:
    raise ValueError(f"Unsupported database type in URL: {SQLALCHEMY_DATABASE_URL}")

# SQLAlchemy Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarative class
Base = declarative_base()

def get_db():
    """
    Provides a database session for each request.
    Closes automatically after completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
