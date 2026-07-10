"""
Structured logging implementation for MindPy.
"""

import sys
from pathlib import Path
from typing import Optional
from loguru import logger
from rich.console import Console
from rich.logging import RichHandler


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    rotation: str = "10 MB",
    retention: str = "30 days",
    console: bool = True,
    json_logs: bool = False,
    format_string: Optional[str] = None
) -> None:
    """
    Configure structured logging for MindPy.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        rotation: Log file rotation setting
        retention: Log file retention setting
        console: Whether to enable console logging
        json_logs: Whether to output JSON logs
        format_string: Custom format string
    """
    # Remove default handler
    logger.remove()
    
    # Default format
    if format_string is None:
        format_string = (
            "{time:YYYY-MM-DD HH:mm:ss} | "
            "{level: <8} | "
            "{name}:{function}:{line} - "
            "{message}"
        )
    
    # Add console handler with rich output
    if console:
        console_handler = RichHandler(
            console=Console(stderr=True),
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            show_time=False,
            show_path=False
        )
        logger.add(
            console_handler,
            level=level,
            format="{message}"
        )
    
    # Add file handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        if json_logs:
            logger.add(
                log_file,
                level=level,
                rotation=rotation,
                retention=retention,
                format="{message}",
                serialize=True
            )
        else:
            logger.add(
                log_file,
                level=level,
                rotation=rotation,
                retention=retention,
                format=format_string
            )
    
    # Set default level
    logger.level(level)


def get_logger(name: str):
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logger.bind(name=name)
