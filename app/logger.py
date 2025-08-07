import logging
import sys
from typing import Optional


def setup_logger(
    name: Optional[str] = None,
    log_level: int = logging.INFO,
    format_string: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
) -> logging.Logger:
    """Setup and configure logger with consistent formatting.

    Args:
        name: Logger name. If None, returns root logger
        log_level: Logging level (default: INFO)
        format_string: Log message format

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Formatter
    formatter = logging.Formatter(format_string)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    # Prevent propagation to avoid duplicate logs
    logger.propagate = False

    return logger


# Create default logger for the application
default_logger = setup_logger("app")
