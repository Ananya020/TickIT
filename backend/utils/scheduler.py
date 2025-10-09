# ==== backend/utils/scheduler.py ====
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import atexit

from ..utils.logger import setup_logging

logger = setup_logging()
scheduler = BackgroundScheduler(daemon=True)

def sample_scheduled_job():
    """
    An example of a job that runs periodically.
    In a real application, this could be a job to:
    - Recalculate SLA breach predictions for open tickets.
    - Clean up old logs or temporary files.
    - Retrain a lightweight ML model.
    """
    logger.info(f"Scheduled job running at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    # Add your recurring task logic here.

def start_scheduler():
    """
    Adds jobs to the scheduler and starts it.
    """
    if not scheduler.running:
        # Add jobs to the scheduler.
        # This job will run every 1 hour.
        scheduler.add_job(
            sample_scheduled_job,
            trigger=IntervalTrigger(hours=1),
            id="sample_job_1",
            name="Hourly sample job",
            replace_existing=True
        )
        
        # Start the scheduler
        scheduler.start()
        logger.info("APScheduler started successfully.")
        
        # Register a shutdown hook to gracefully stop the scheduler
        atexit.register(lambda: scheduler.shutdown())

def stop_scheduler():
    """
    Stops the scheduler if it is running.
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler shut down successfully.")