"""
Factory for creating pre-configured TodoistService instances.
"""

from dataclasses import dataclass
from enum import Enum, auto

from loguru import logger

from aerith_ingestion.core.base import TracedClass
from aerith_ingestion.domain.models import (
    ProjectFormatter,
    ProjectRepository,
    ProjectSorter,
)
from aerith_ingestion.infrastructure.repositories import JSONProjectRepository
from aerith_ingestion.services.formatters import DefaultProjectFormatter
from aerith_ingestion.services.sorters import DefaultProjectSorter
from aerith_ingestion.services.todoist import TodoistService
from src.aerith_ingestion.core.config import Settings


class StorageType(Enum):
    """Supported storage types."""

    JSON = auto()
    # Add more storage types as needed
    # CSV = auto()
    # SQLite = auto()


@dataclass
class ServiceConfig:
    """Configuration for TodoistService factory."""

    storage_type: StorageType = StorageType.JSON
    storage_path: str = "tmp/projects.json"
    sorter: ProjectSorter = DefaultProjectSorter()
    formatter: ProjectFormatter = DefaultProjectFormatter()


class TodoistServiceFactory(TracedClass):
    """Factory for creating pre-configured TodoistService instances."""

    @staticmethod
    def create_repository(config: ServiceConfig) -> ProjectRepository:
        """Create a repository based on the storage type."""
        if config.storage_type == StorageType.JSON:
            return JSONProjectRepository(config.storage_path)
        # Add more storage types as needed
        raise ValueError(f"Unsupported storage type: {config.storage_type}")

    @classmethod
    def create_service(
        cls,
        settings: Settings,
        service_config: ServiceConfig = ServiceConfig(),
    ) -> TodoistService:
        """Create a pre-configured TodoistService instance."""
        try:
            repository = cls.create_repository(service_config)

            return TodoistService(
                config=settings,
                repository=repository,
                sorter=service_config.sorter,
                formatter=service_config.formatter,
            )
        except Exception as e:
            logger.error(f"Failed to create TodoistService: {e}")
            raise
