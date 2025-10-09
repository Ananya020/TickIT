# ==== backend/database/init_db.py ====
from ..database.db_connect import engine, Base
from ..models import ticket, user # Import models to ensure they are registered with Base
import logging

# Configure logging for init_db
init_db_logger = logging.getLogger(__name__)
init_db_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
init_db_logger.addHandler(handler)

def create_tables():
    """
    Creates all database tables defined by SQLAlchemy models.
    """
    init_db_logger.info("Attempting to create database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        init_db_logger.info("Database tables created or already exist.")
    except Exception as e:
        init_db_logger.error(f"Error creating database tables: {e}")
        raise # Re-raise the exception to indicate a critical startup failure