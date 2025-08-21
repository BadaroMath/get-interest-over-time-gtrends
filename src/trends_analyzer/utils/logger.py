"""Logging utilities for Google Trends Analyzer."""

import logging
import sys
from pathlib import Path
from typing import Optional
from rich.logging import RichHandler
import structlog


def setup_logger(
    name: str = "trends_analyzer",
    level: str = "INFO",
    log_file: Optional[str] = None,
    console: bool = True,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Set up structured logging with both file and console output.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        console: Whether to log to console
        format_string: Custom format string
    
    Returns:
        Configured logger instance
    """
    # Remove existing handlers
    logger = logging.getLogger(name)
    logger.handlers.clear()
    
    # Set level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Default format
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    
    formatter = logging.Formatter(format_string)
    
    # Console handler with Rich for beautiful output
    if console:
        console_handler = RichHandler(
            rich_tracebacks=True,
            show_path=False,
            show_time=True
        )
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    return logger


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class AnalysisContext:
    """Context manager for logging analysis operations."""
    
    def __init__(self, logger: logging.Logger, operation: str, **context):
        self.logger = logger
        self.operation = operation
        self.context = context
    
    def __enter__(self):
        self.logger.info(f"Starting {self.operation}", extra=self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.logger.info(f"Completed {self.operation}", extra=self.context)
        else:
            self.logger.error(
                f"Failed {self.operation}: {exc_val}", 
                extra=self.context,
                exc_info=True
            )
        return False