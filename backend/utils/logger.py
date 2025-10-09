# ==== backend/utils/logger.py ====
import logging
import sys
import os
from logging.handlers import RotatingFileHandler

def setup_logging(name: str = "tickit_backend"):
    """
    Sets up a centralized logger with console and file handlers.
    Logs to stdout and a rotating file.
    
    Args:
        name (str): The name of the logger to configure.
        
    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper()) # Default to INFO, can be changed via env var

    # Ensure handlers are not duplicated if called multiple times
    if not logger.handlers:
        # Console Handler (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(console_handler)

        # File Handler (rotating file)
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "tickit.log")
        
        # Rotate log file after 1 MB, keep 5 backup files
        file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=5)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)

    return logger

# Example usage (for internal testing)
if __name__ == "__main__":
    test_logger = setup_logging("test_module")
    test_logger.debug("This is a debug message.")
    test_logger.info("This is an info message.")
    test_logger.warning("This is a warning message.")
    test_logger.error("This is an error message.")
    try:
        1 / 0
    except ZeroDivisionError:
        test_logger.exception("An exception occurred during division.")