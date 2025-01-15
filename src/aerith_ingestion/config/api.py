"""
API configuration settings.

This module provides configuration for external API services:
1. Todoist API for task/project data
2. OpenAI API for task analysis and embeddings
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
class ApiConfig:
    """Combined API configuration settings."""

    todoist: TodoistApiConfig
    openai: OpenAIConfig
