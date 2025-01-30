from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class ProjectModel(BaseModel):
    """Pydantic model for Todoist projects."""

    id: str = Field(..., description="Unique identifier of the project")
    name: str = Field(..., description="Name of the project")
    color: str = Field(..., description="Color of the project")
    comment_count: int = Field(..., description="Number of comments in the project")
    is_shared: bool = Field(..., description="Indicates if the project is shared")
    is_favorite: bool = Field(..., description="Indicates if the project is a favorite")
    url: str = Field(..., description="URL of the project in Todoist")
    parent_id: Optional[str] = Field(None, description="ID of the parent project")
    order: int = Field(..., description="Order of the project in the list")
    view_style: str = Field(
        ..., description="View style of the project (list or board)"
    )


class ContentInfo(BaseModel):
    """Model for content processing information."""

    original_content: str
    processed_content: Optional[str] = None
    content_changes: List[str] = Field(default_factory=list)
    spelling_fixes: List[str] = Field(default_factory=list)
    grammar_fixes: List[str] = Field(default_factory=list)
    formatting_changes: List[str] = Field(default_factory=list)


class AdditionalInfo(BaseModel):
    """Model for additional categorization information."""

    categorization_timestamp: str
    model_used: str
    confidence_score: Optional[float] = None
    categorization_reason: Optional[str] = None
    estimated_duration: Optional[str] = None
    energy_level: Optional[str] = None
    context_tags: List[str] = Field(default_factory=list)
    content_info: Optional[ContentInfo] = None


class BaseTaskModel(BaseModel):
    """Base model for common task fields."""

    id: str
    content: str
    original_content: Optional[str] = None  # Store original content
    priority: int = 1
    due: Optional[Dict[str, Any]] = None
    project_id: Optional[str] = None
    description: str = ""
    original_description: Optional[str] = None  # Store original description
    is_completed: bool = False
    labels: List[str] = Field(default_factory=list)
    comment_count: int = 0
    creator_id: Optional[str] = None
    created_at: str
    url: Optional[str] = None


class TaskModel(BaseTaskModel):
    """Input model for Todoist tasks during processing."""

    source_project: Optional[str] = None  # Renamed to clarify it's just source tracking
    gtd_level: Optional[str] = None
    gtd_priority: Optional[str] = None
    timeframe: Optional[str] = None
    additional_info: Optional[Dict] = None
    raw_response: Optional[str] = None
    categorization_attempts: int = 0
    error_messages: List[str] = Field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskModel":
        """Safely create a TaskModel from a dictionary."""
        # Ensure required fields exist
        required_fields = {"id", "content"}
        if not all(field in data for field in required_fields):
            raise ValueError(f"Missing required fields. Required: {required_fields}")

        # Convert any None values to appropriate defaults
        cleaned_data = {
            k: v if v is not None else cls.model_fields[k].default
            for k, v in data.items()
            if k in cls.model_fields
        }

        return cls(**cleaned_data)


class GTDTaskOutput(BaseTaskModel):
    """Output model for GTD-categorized tasks in JSONL format."""

    gtd_level: Optional[str] = None
    gtd_priority: Optional[str] = None
    timeframe: Optional[str] = None
    additional_info: Optional[AdditionalInfo] = None
    raw_response: Optional[str] = None
    categorization_attempts: int = 0
    error_messages: List[str] = Field(default_factory=list)

    @classmethod
    def from_task_model(cls, task: TaskModel) -> "GTDTaskOutput":
        """Convert a TaskModel to GTDTaskOutput."""
        # Create dict of all fields from task, excluding source project info
        task_dict = task.model_dump(exclude={"source_project"})

        # Convert additional_info if it exists
        if task_dict.get("additional_info"):
            # Remove any source project info from additional_info
            additional_info = task_dict["additional_info"]
            if isinstance(additional_info, dict):
                additional_info.pop("project_name", None)
            task_dict["additional_info"] = AdditionalInfo(**additional_info)

        return cls(**task_dict)

    def to_jsonl(self) -> str:
        """Convert the model to a JSONL-formatted string."""
        return self.model_dump_json()
