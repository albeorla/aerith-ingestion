"""Logging configuration settings."""

import os
import sys
from dataclasses import dataclass

from loguru import logger


@dataclass
class LoggingConfig:
    """Logging configuration settings."""

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

    log_path = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    # Remove default handler
    logger.remove()

    # Add console handler with simplified format
    logger.add(
        sys.stderr,
        format=config.console_format,
        level="DEBUG",
        colorize=True,
        enqueue=True,
    )

    # Add main log file handler
    log_file = os.path.join(log_path, "app.log")
    logger.add(
        log_file,
        format=config.log_format,
        level="DEBUG",
        enqueue=True,
        mode="w",
    )

    # Add error log file handler
    error_log_file = os.path.join(log_path, "error.log")
    logger.add(
        error_log_file,
        format=config.error_format,
        level="ERROR",
        enqueue=True,
        mode="w",
        filter=lambda record: record["level"].name == "ERROR",
    )
