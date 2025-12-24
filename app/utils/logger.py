import logging
import sys
from datetime import datetime
from typing import Optional


def setup_logger(name: str = __name__, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with both file and console handlers
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    try:
        file_handler = logging.FileHandler(f"logs/app_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except:
        # If logs directory doesn't exist, just use console
        pass
    
    return logger


# Global logger instance
app_logger = setup_logger("standard_insights")