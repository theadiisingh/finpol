"""Logger utility for the application."""
import logging
import sys
from typing import Optional


def setup_logger(name: str = "finpol", level: int = logging.INFO) -> logging.Logger:
    """
    Setup application logger.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Simple formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a reusable logger instance.
    
    Args:
        name: Logger name (uses module name if not provided)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name or __name__)


# Default logger instance
logger = setup_logger()
