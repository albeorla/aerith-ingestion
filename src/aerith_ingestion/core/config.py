"""
Configuration settings for the application following SOLID principles.
"""

import os
import sys
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Any, Dict, Optional

from loguru import logger
from pydantic import Field, validator
from pydantic_settings import BaseSettings


def log_section(title: str) -> None:
    """Log a section header with consistent formatting."""
    logger.info("\n\n========== {} ==========", title)


# Log format strings
DEFAULT_LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

DEFAULT_TRACE_FORMAT = DEFAULT_LOG_FORMAT

DEFAULT_ERROR_FORMAT = (
    "<red>{time:YYYY-MM-DD HH:mm:ss.SSS}</red> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<red>Error:</red> {message}\n"
    "<red>Exception:</red> {exception}\n"
    "<red>Context:</red>\n{extra}"
)

SIMPLE_CONSOLE_FORMAT = "<level>{message}</level>"

SIMPLE_ERROR_FORMAT = DEFAULT_ERROR_FORMAT
SIMPLE_TRACE_FORMAT = DEFAULT_LOG_FORMAT


class LogConfig(ABC):
    """Abstract base class for logging configuration."""

    @abstractmethod
    def setup_logging(self) -> None:
        """Set up logging configuration."""
        pass

    @abstractmethod
    def ensure_log_path(self) -> None:
        """Ensure log directory exists."""
        pass


class APIConfig(ABC):
    """Abstract base class for API configuration."""

    @abstractmethod
    def get_api_token(self) -> str:
        """Get API token."""
        pass


class VectorStoreSettings(BaseSettings):
    """Vector store settings"""

    collection_name: str = "todoist_tasks"
    embedding_model: str = "all-MiniLM-L6-v2"
    batch_size: int = 100
    similarity_top_k: int = 5
    persist_directory: Optional[str] = Field(
        default=None,
        description="Directory to persist vector store. If None, uses in-memory store.",
    )
    chroma_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "anonymized_telemetry": False,
            "allow_reset": True,
            "is_persistent": True,
        }
    )

    @validator("embedding_model")
    def validate_embedding_model(cls, v: str) -> str:
        """Validate embedding model choice"""
        valid_models = [
            "all-MiniLM-L6-v2",  # Fast, efficient, good for short texts
            "all-mpnet-base-v2",  # Better quality but slower
            "paraphrase-multilingual-MiniLM-L12-v2",  # Multi-language support
        ]
        if v not in valid_models:
            raise ValueError(f"Invalid embedding model. Must be one of {valid_models}")
        return v


class Settings(BaseSettings, LogConfig, APIConfig):
    """
    Configuration settings for the application implementing SOLID interfaces.
    """

    # API Configuration
    openai_api_key: str = Field(
        default="",
        env="OPENAI_API_KEY",
        description="OpenAI API key for AI operations",
    )
    todoist_api_token: str = Field(
        default="",
        env="TODOIST_API_TOKEN",
        description="Todoist API token for task management",
    )

    # Environment Configuration
    environment: str = Field(
        default="dev",
        env="ENVIRONMENT",
        description="Current environment (dev/prod)",
    )
    debug: bool = Field(default=False, env="DEBUG", description="Debug mode flag")

    # Logging Configuration
    log_path: str = Field(
        default="logs", env="LOG_PATH", description="Path for log files"
    )
    log_level: str = Field(default="INFO", env="LOG_LEVEL", description="Logging level")
    log_format: str = Field(
        default=DEFAULT_LOG_FORMAT,
        env="LOG_FORMAT",
        description="Log format string",
    )
    trace_log_format: str = Field(
        default=DEFAULT_TRACE_FORMAT,
        env="TRACE_LOG_FORMAT",
        description="Trace log format string",
    )
    error_log_format: str = Field(
        default=DEFAULT_ERROR_FORMAT,
        env="ERROR_LOG_FORMAT",
        description="Error log format string",
    )

    # Vector Store Configuration
    vector_store: VectorStoreSettings = Field(default_factory=VectorStoreSettings)

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    def setup_logging(self) -> None:
        """Set up logging configuration with file and console handlers."""
        self.ensure_log_path()

        # Remove default handler
        logger.remove()

        # Add console handler for development
        if self.environment == "dev" or self.debug:
            logger.add(
                sys.stderr,
                format=SIMPLE_CONSOLE_FORMAT,  # Simplified format for console
                level=self.log_level,
                colorize=True,
                enqueue=True,
            )

        # Add main application log file handler with full details
        log_file = os.path.join(self.log_path, "app.log")
        logger.add(
            log_file,
            format=self.trace_log_format,
            level=self.log_level,
            enqueue=True,
            mode="w",
        )

        # Add error-specific log file handler
        error_log_file = os.path.join(self.log_path, "error.log")
        logger.add(
            error_log_file,
            format=SIMPLE_ERROR_FORMAT,
            level="ERROR",
            enqueue=True,
            filter=lambda record: record["level"].name == "ERROR",
            mode="w",
        )

        # Add trace log file with full details
        trace_log_file = os.path.join(self.log_path, "trace.log")
        logger.add(
            trace_log_file,
            format=SIMPLE_TRACE_FORMAT,
            level="TRACE",
            enqueue=True,
            mode="w",
        )

        logger.trace("Logging initialized with level {}", self.log_level)

    def ensure_log_path(self) -> None:
        """Ensure log directory exists."""
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)

    def get_api_token(self) -> str:
        """Get API token."""
        return self.todoist_api_token

    @validator("log_level", pre=True, always=True)
    def set_log_level(cls, v: str, values: dict) -> str:
        """Validate and set log level."""
        valid_levels = [
            "TRACE",
            "DEBUG",
            "INFO",
            "SUCCESS",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ]
        v = v.upper()
        if v not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of {valid_levels}")
        return v

    def __init__(self, **kwargs):
        """Initialize settings and set up logging."""
        super().__init__(**kwargs)
        self.setup_logging()


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings using singleton pattern.
    Uses lru_cache to ensure only one instance is created.
    """
    return Settings()
