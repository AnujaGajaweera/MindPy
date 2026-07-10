"""
Logging system for MindPy.

Provides structured logging with rich console output and file logs.
"""

from mindpy.logging.logger import get_logger, setup_logging

__all__ = [
    "get_logger",
    "setup_logging",
]
