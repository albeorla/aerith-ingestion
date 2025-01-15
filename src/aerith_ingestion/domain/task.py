"""
Task domain models.

This module provides:
1. Core Task model and related types
2. Enriched task models with analysis and vector data
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Due:
    """Task due date information."""

    date: str
    recurring: bool
    string: str
    datetime: Optional[datetime] = None
    timezone: Optional[str] = None


@dataclass
class Task:
    """A Todoist task."""

    id: str
    project_id: str
    content: str
    description: str = ""
    priority: int = 1
    due: Optional[Due] = None
    parent_id: Optional[str] = None
    url: str = ""
    order: int = 0
    comment_count: int = 0
    created_at: datetime = None


@dataclass
class VectorMetadata:
    """Vector embedding metadata for a task."""

    task_id: str
    vector: List[float]
    content: str  # Text used to generate the vector


@dataclass
class TaskAnalysisResult:
    """Results from LLM analysis of a task."""

    category: str  # e.g. "Development", "Research", "Planning"
    complexity: str  # e.g. "High", "Medium", "Low"
    themes: List[str]  # Key themes/topics
    dependencies: List[str]  # Required dependencies/prerequisites
    next_actions: List[str]  # Suggested next steps


@dataclass
class EnrichedTask(Task):
    """Task enriched with metadata and analysis."""

    analysis: Optional[TaskAnalysisResult] = None
    vector_metadata: Optional[VectorMetadata] = None
