# ==== backend/events/startup.py ====
from ..utils.logger import setup_logging
from ..routers import recommend, chatbot, anomaly, classify # Import routers to access their init functions
from ..utils.scheduler import start_scheduler
from ..config import settings

logger = setup_logging()

def initialize_ai_models():
    """
    Initializes all AI models required for the application.
    This function is called once on application startup.
    """
    logger.info("Starting AI model initialization...")
    
    # Initialize the Recommendation Engine (FAISS, SentenceTransformer)
    recommend.load_faiss_index()
    
    # Initialize the Conversational AI Assistant (LangChain Agent)
    chatbot.initialize_chatbot_agent()
    
    # Initialize the Anomaly Detection model (Isolation Forest)
    anomaly.train_anomaly_model()

    # Initialize the Classification Engine model (TF-IDF/BERT)
    classify.initialize_classification_models() # We need to create this function
    
    logger.info("AI model initialization complete.")

def start_background_tasks():
    """
    Starts any background tasks, such as scheduled jobs.
    """
    if settings.ENABLE_SCHEDULER:
        logger.info("Starting background scheduler...")
        start_scheduler()
    else:
        logger.warning("Background scheduler is disabled by configuration.")
        