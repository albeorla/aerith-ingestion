"""
Domain models and interfaces for the Todoist ingestion application.
"""

import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, NamedTuple, Optional, Protocol


class ViewStyle(str, Enum):
    """Project view style options."""

    LIST = "list"
    BOARD = "board"
    CALENDAR = "calendar"


class TaskPriority(int, Enum):
    """Task priority levels."""

    NONE = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4


class TaskStats(NamedTuple):
    """Statistics about tasks in a project or task group."""

    total: int
    completed: int
    overdue: int
    high_priority: int
    has_due_date: int
    completion_rate: float


@dataclass
class DueDate:
    """Due date information for tasks and projects."""

    date: str
    datetime: Optional[datetime] = None
    timezone: Optional[str] = None
    is_recurring: bool = False
    string: Optional[str] = None

    def is_overdue(self, reference_time: Optional[datetime] = None) -> bool:
        """Check if the due date is overdue relative to the reference time."""
        if not self.datetime:
            return False
        reference = reference_time or datetime.now()
        return self.datetime < reference

    def __str__(self) -> str:
        """Human readable due date representation."""
        if self.string:
            return f"{self.string} {'(recurring)' if self.is_recurring else ''}"
        return self.date


@dataclass
class TaskDue:
    date: str
    is_recurring: bool
    string: str
    datetime: Optional[str]
    timezone: Optional[str]


@dataclass
class Task:
    id: str
    content: str
    description: str
    project_id: str
    created_at: str
    due: Optional[TaskDue]
    priority: int
    url: str
    comment_count: int
    order: int
    is_completed: bool
    labels: List[str]
    parent_id: Optional[str]
    assignee_id: Optional[str]
    assigner_id: Optional[str]
    section_id: Optional[str]
    duration: Optional[int]
    sync_id: Optional[str]

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def get_content_hash(self) -> str:
        """Generate a hash of the task's content to detect changes"""
        content = (
            f"{self.content}|{self.description}|{self.priority}|"
            f"{self.due.date if self.due else ''}"
        )
        return hashlib.sha256(content.encode()).hexdigest()


@dataclass
class Project:
    id: str
    name: str
    color: str
    comment_count: int
    is_favorite: bool
    is_inbox_project: bool
    is_shared: bool
    is_team_inbox: bool
    can_assign_tasks: Optional[bool]
    order: int
    parent_id: Optional[str]
    url: str
    view_style: str
    tasks: List[Task]


@dataclass
class VectorMetadata:
    """Metadata for vector database storage"""

    doc_id: str  # The document ID in the vector store
    embedding_model: str  # The model used to generate embeddings
    last_updated: datetime  # When the vector was last updated
    content_hash: str  # Hash of the content when last vectorized


@dataclass
class EnrichedTask:
    """A task enriched with additional metadata and context"""

    task: Task
    project: Project
    metadata: Dict[str, Any]  # For storing enriched data
    embeddings: Optional[List[float]]  # For vector storage
    vector_metadata: Optional[VectorMetadata]  # For tracking vector db state
    processed_at: datetime


class ProjectSorter(Protocol):
    """Protocol for project sorting strategies."""

    def sort(self, projects: List[Project]) -> List[Project]:
        """Sort the projects according to the strategy."""
        pass


class ProjectFormatter(Protocol):
    """Protocol for project formatting strategies."""

    def format(self, project: Project) -> str:
        """Format a project for display."""
        pass


class ProjectRepository(ABC):
    """Abstract base class for project storage."""

    @abstractmethod
    def save(self, projects: List[Project]) -> None:
        """Save projects to storage."""
        pass
