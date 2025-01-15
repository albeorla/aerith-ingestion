"""
Application configuration.

This module provides the main configuration for the application,
combining settings from all subsystems.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from aerith_ingestion.config.api import ApiConfig, OpenAIConfig, TodoistApiConfig
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

    Returns:
        AppConfig: Fully initialized application configuration

    Raises:
        ValueError: If required environment variables are missing
    """
    # Load environment variables from .env file
    load_dotenv()

    # Load API keys
    todoist_api_key = os.getenv("TODOIST_API_TOKEN", "")  # Optional
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("Missing required OPENAI_API_KEY")

    # Create API config
    api_config = ApiConfig(
        todoist=TodoistApiConfig(api_key=todoist_api_key),
        openai=OpenAIConfig(
            api_key=openai_api_key,
            model="gpt-4o",  # Fixed model name
            embedding_model="text-embedding-ada-002",
            vector_index_path="data/vector_store/task_vectors.index",
        ),
    )

    # Create database config
    db_config = DatabaseConfig(
        sqlite=SQLiteConfig(
            database_path="data/todoist.db",
        ),
    )

    # Create enrichment config with customized settings
    enrichment_config = EnrichmentConfig(
        analysis=TaskAnalysisConfig(
            min_theme_count=2,
            max_theme_count=5,
        ),
        vector_search=VectorSearchConfig(
            similarity_threshold=0.7,
            top_k=5,
            cache_size=10000,
        ),
        batch_processing=BatchProcessingConfig(
            batch_size=100,
            max_retries=3,
            timeout=300,
        ),
    )

    # Create logging config and set up logging
    logging_config = LoggingConfig()
    setup_logging(logging_config)

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
