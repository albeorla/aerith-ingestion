"""
Todoist data mapping service.

This module handles mapping between Todoist API responses and domain models.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from aerith_ingestion.domain.project import Project
from aerith_ingestion.domain.task import Due, Task


class TodoistDataMapper:
    """Maps Todoist API responses to domain models."""

    def map_project(self, project_data: Dict[str, Any]) -> Project:
        """Map Todoist project data to domain model."""
        return Project(
            id=str(project_data["id"]),
            name=project_data["name"],
            parent_id=(
                str(project_data["parent_id"])
                if project_data.get("parent_id")
                else None
            ),
            order=project_data.get("order", 0),
            comment_count=project_data.get("comment_count", 0),
            is_shared=project_data.get("is_shared", False),
            url=project_data.get("url", ""),
            view_style=project_data.get("view_style", "list"),
        )

    def map_task(self, task_data: Dict[str, Any]) -> Task:
        """Map Todoist task data to domain model."""
        return Task(
            id=str(task_data["id"]),
            project_id=str(task_data["project_id"]),
            content=task_data["content"],
            description=task_data.get("description", ""),
            priority=task_data.get("priority", 1),
            due=self._map_due(task_data.get("due")),
            parent_id=(
                str(task_data["parent_id"]) if task_data.get("parent_id") else None
            ),
            url=task_data.get("url", ""),
            order=task_data.get("order", 0),
            comment_count=task_data.get("comment_count", 0),
            created_at=datetime.fromisoformat(
                task_data["created_at"].replace("Z", "+00:00")
            ),
        )

    def _map_due(self, due_data: Optional[Dict[str, Any]]) -> Optional[Due]:
        """Map Todoist due date data to domain model."""
        if not due_data:
            return None

        return Due(
            date=due_data["date"],
            recurring=due_data.get("recurring", False),
            string=due_data.get("string", ""),
            datetime=(
                datetime.fromisoformat(due_data["datetime"].replace("Z", "+00:00"))
                if due_data.get("datetime")
                else None
            ),
            timezone=due_data.get("timezone", None),
        )

    def map_projects(self, raw_data: Dict[str, Any]) -> list[Project]:
        """Map a list of Todoist projects from raw API data."""
        return [self.map_project(project) for project in raw_data["projects"]]


def create_data_mapper() -> TodoistDataMapper:
    """Create a new Todoist data mapper."""
    return TodoistDataMapper()
