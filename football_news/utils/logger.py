"""Centralized logging configuration with daily rotation."""

import os
import sys
from pathlib import Path
from loguru import logger

# Create logs directory
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Remove default handler
logger.remove()

# Console handler with colors
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=os.getenv("LOG_LEVEL", "INFO"),
    colorize=True,
)

# File handler with daily rotation
logger.add(
    LOG_DIR / "football-news-{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level=os.getenv("LOG_LEVEL", "INFO"),
    rotation="00:00",  # Rotate at midnight
    retention="30 days",  # Keep logs for 30 days
    compression="zip",  # Compress old logs
    enqueue=True,  # Thread-safe logging
)

# Error file handler for errors and critical logs
logger.add(
    LOG_DIR / "football-news-errors-{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="00:00",
    retention="30 days",
    compression="zip",
    enqueue=True,
)

# Export configured logger
__all__ = ["logger"]
