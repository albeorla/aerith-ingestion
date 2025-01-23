"""
Application configuration.

This module provides the main configuration for the application,
combining settings from all subsystems.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from aerith_ingestion.config.api import (
    ApiConfig,
    GoogleCalendarApiConfig,
    OpenAIConfig,
    TodoistApiConfig,
)
from aerith_ingestion.config.db import DatabaseConfig, SQLiteConfig
from aerith_ingestion.config.enrichment import (
    BatchProcessingConfig,
    EnrichmentConfig,
    TaskAnalysisConfig,
    VectorSearchConfig,
)
from aerith_ingestion.config.logging import LoggingConfig, setup_logging


@dataclass
class AppConfig:
    """Main application configuration.

    Attributes:
        api: API configurations for external services
        database: Database connection settings
        enrichment: Task enrichment settings
        logging: Logging configuration
    """

    api: ApiConfig
    database: DatabaseConfig
    enrichment: EnrichmentConfig
    logging: LoggingConfig


def load_config() -> AppConfig:
    """Load configuration from environment variables and defaults.

    Required environment variables:
        OPENAI_API_KEY: API key for OpenAI

    Optional environment variables:
        TODOIST_API_TOKEN: API key for Todoist (only required for sync command)
        GOOGLE_CALENDAR_CLIENT_ID: Client ID for Google Calendar API
        GOOGLE_CALENDAR_CLIENT_SECRET: Client secret for Google Calendar API
        GOOGLE_CALENDAR_REFRESH_TOKEN: Refresh token for Google Calendar API

    Returns:
        Loaded application configuration
    """
    load_dotenv()

    # API configuration
    api_config = ApiConfig(
        todoist=TodoistApiConfig(api_key=os.getenv("TODOIST_API_TOKEN", "")),
        openai=OpenAIConfig(api_key=os.getenv("OPENAI_API_KEY", "")),
        google_calendar=GoogleCalendarApiConfig(
            client_id=os.getenv("GOOGLE_CALENDAR_CLIENT_ID", ""),
            client_secret=os.getenv("GOOGLE_CALENDAR_CLIENT_SECRET", ""),
            refresh_token=os.getenv("GOOGLE_CALENDAR_REFRESH_TOKEN"),
            token_uri="https://oauth2.googleapis.com/token",
            scopes=[
                "https://www.googleapis.com/auth/calendar",
                "https://www.googleapis.com/auth/calendar.events",
            ],
        ),
    )

    # Database configuration
    db_config = DatabaseConfig(
        sqlite=SQLiteConfig(database_path=os.getenv("SQLITE_DB_PATH", "data/aerith.db"))
    )

    # Enrichment configuration
    enrichment_config = EnrichmentConfig(
        analysis=TaskAnalysisConfig(),
        vector_search=VectorSearchConfig(),
        batch_processing=BatchProcessingConfig(),
    )

    # Logging configuration
    logging_config = LoggingConfig()

    return AppConfig(
        api=api_config,
        database=db_config,
        enrichment=enrichment_config,
        logging=logging_config,
    )


__all__ = [
    "AppConfig",
    "load_config",
    "ApiConfig",
    "OpenAIConfig",
    "TodoistApiConfig",
    "DatabaseConfig",
    "SQLiteConfig",
    "EnrichmentConfig",
    "TaskAnalysisConfig",
    "VectorSearchConfig",
    "BatchProcessingConfig",
    "LoggingConfig",
    "setup_logging",
]
