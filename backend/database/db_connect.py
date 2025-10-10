# ==== backend/database/db_connect.py ====
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Configure logging
db_logger = logging.getLogger(__name__)
db_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
db_logger.addHandler(handler)

# --- Load Database URL ---
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "mysql+pymysql://root:root@localhost:3306/tickit"
)

db_logger.info(f"Connecting to database at: {SQLALCHEMY_DATABASE_URL.split('://')[0]}://***")

# --- Engine Configuration for MySQL ---
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,    # Recycles dead connections
    pool_size=10,          # Persistent connections
    max_overflow=20,       # Allows bursts beyond pool_size
    pool_recycle=1800,     # Reconnect every 30 mins
    echo=False             # Set True to debug SQL queries
)

# --- SQLAlchemy ORM Setup ---
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> "Session":
    """
    Provides a SQLAlchemy session for FastAPI dependency injection.
    Automatically closes session after each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
