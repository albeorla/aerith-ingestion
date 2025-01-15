"""
Database configuration settings.
"""

from dataclasses import dataclass


@dataclass
class SQLiteConfig:
    """SQLite database configuration."""

    database_path: str = "data/todoist.db"
    echo: bool = False


@dataclass
class DatabaseConfig:
    """Database configuration settings."""

    sqlite: SQLiteConfig
