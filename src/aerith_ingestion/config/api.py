"""
API configuration settings.

This module provides configuration for external API services:
1. Todoist API for task/project data
2. OpenAI API for task analysis and embeddings
3. Google Calendar API for calendar integration
"""

from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class TodoistApiConfig:
    """Todoist API configuration."""

    api_key: str


@dataclass
class OpenAIConfig:
    """OpenAI API configuration for both task analysis and embeddings."""

    api_key: str
    model: str = "gpt-4o"  # Model for task analysis
    temperature: float = 0.7
    max_tokens: int = 1000
    embedding_model: Literal["text-embedding-ada-002"] = "text-embedding-ada-002"
    vector_index_path: Optional[str] = "data/vector_store/task_vectors.index"


@dataclass
class GoogleCalendarApiConfig:
    """Configuration for Google Calendar API."""

    client_id: str
    client_secret: str
    refresh_token: Optional[str] = None
    token_uri: str = "https://oauth2.googleapis.com/token"
    scopes: list[str] = None

    def __post_init__(self):
        """Set default scopes if none provided."""
        if self.scopes is None:
            self.scopes = [
                "https://www.googleapis.com/auth/calendar",
                "https://www.googleapis.com/auth/calendar.events",
            ]


@dataclass
class ApiConfig:
    """Combined API configuration settings."""

    todoist: TodoistApiConfig
    openai: OpenAIConfig
    google_calendar: GoogleCalendarApiConfig
