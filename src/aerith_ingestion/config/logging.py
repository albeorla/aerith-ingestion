"""
Logging configuration settings.
"""

import os
import sys
from dataclasses import dataclass

from loguru import logger


@dataclass
class LoggingConfig:
    """Logging configuration settings."""

    log_path: str = "logs"
    log_level: str = "INFO"
    log_format: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    error_format: str = (
        "<red>{time:YYYY-MM-DD HH:mm:ss.SSS}</red> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<red>Error:</red> {message}\n"
        "<red>Exception:</red> {exception}\n"
        "<red>Context:</red>\n{extra}"
    )
    console_format: str = "<level>{message}</level>"


def setup_logging(config: LoggingConfig) -> None:
    """Set up logging configuration."""
    # Ensure log directory exists
    if not os.path.exists(config.log_path):
        os.makedirs(config.log_path)

    # Remove default handler
    logger.remove()

    # Add console handler
    logger.add(
        sys.stderr,
        format=config.console_format,
        level=config.log_level,
        colorize=True,
        enqueue=True,
    )

    # Add main log file handler
    log_file = os.path.join(config.log_path, "app.log")
    logger.add(
        log_file,
        format=config.log_format,
        level="DEBUG",
        enqueue=True,
        mode="w",
    )

    # Add trace log file handler
    trace_log_file = os.path.join(config.log_path, "trace.log")
    logger.add(
        trace_log_file,
        format=config.log_format,
        level="TRACE",
        enqueue=True,
        mode="w",
    )

    # Add error log file handler
    error_log_file = os.path.join(config.log_path, "error.log")
    logger.add(
        error_log_file,
        format=config.error_format,
        level="ERROR",
        enqueue=True,
        filter=lambda record: record["level"].name == "ERROR",
        mode="w",
    )
