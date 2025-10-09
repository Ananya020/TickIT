# ==== backend/config.py ====
import os
from pydantic_settings import BaseSettings
from typing import Literal

# Define the base directory of the application
# This allows us to create absolute paths for models and logs
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Settings(BaseSettings):
    """
    Centralized application settings.
    Settings are loaded from environment variables.
    A .env file can be used for local development.
    """
    # --- Core Application Settings ---
    APP_NAME: str = "TickIT AI Incident Management Backend"
    DEBUG_MODE: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    
    # --- Database Configuration ---
    # Default to a local SQLite DB for ease of use
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'tickit.db')}"
    
    # --- JWT Authentication ---
    JWT_SECRET_KEY: str = "a_very_secret_key_that_should_be_changed"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    # --- CORS Origins ---
    FRONTEND_URL: str = "http://localhost:3000"
    
    # --- AI/ML Model and Data Paths ---
    # Use BASE_DIR to ensure paths are always correct, regardless of where the app is run from
    MODELS_DATA_DIR: str = os.path.join(BASE_DIR, "models_data")
    FAISS_INDEX_PATH: str = os.path.join(MODELS_DATA_DIR, "faiss_index.bin")
    RESOLUTIONS_DATA_PATH: str = os.path.join(MODELS_DATA_DIR, "resolutions.json")
    
    # --- External API Keys ---
    # These are optional and will be loaded from the environment
    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    
    # --- Task Scheduling ---
    ENABLE_SCHEDULER: bool = True

    class Config:
        # This tells Pydantic to look for a .env file
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Create a single, importable instance of the settings
settings = Settings()

# Ensure the models_data directory exists
os.makedirs(settings.MODELS_DATA_DIR, exist_ok=True)