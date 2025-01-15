"""
Project formatting and sorting operations.
"""

from typing import List

from todoist_api_python.models import Project

from aerith_ingestion.core.base import TracedClass
from aerith_ingestion.domain.models import ProjectFormatter, ProjectSorter


class ProjectOperations(TracedClass, ProjectFormatter, ProjectSorter):
    """Handles project formatting and sorting operations."""

    def format(self, project: Project) -> str:
        """Format a single project for display in logs."""
        status_flags = []
        if project.is_inbox_project:
            status_flags.append("INBOX")
        if project.is_shared:
            status_flags.append("SHARED")

        status = f" [{', '.join(status_flags)}]" if status_flags else ""
        return f"{project.name}{status} (ID: {project.id}, Order: {project.order})"

    def sort(self, projects: List[Project]) -> List[Project]:
        """Sort projects by priority: Inbox first, then by order and name."""

        def sort_key(p: Project):
            inbox_priority = -1 if p.is_inbox_project else 0
            order = p.order or 0
            name = p.name or ""
            return (inbox_priority, order, name)

        return sorted(projects, key=sort_key)
