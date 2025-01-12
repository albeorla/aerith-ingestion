"""
Project formatting implementations.
"""

from todoist_api_python.models import Project

from aerith_ingestion.core.base import TracedClass
from aerith_ingestion.domain.models import ProjectFormatter


class DefaultProjectFormatter(TracedClass, ProjectFormatter):
    """Default implementation of project formatting."""

    def format(self, project: Project) -> str:
        """Format a single project for display in logs."""
        status_flags = []
        if project.is_inbox_project:
            status_flags.append("INBOX")
        if project.is_shared:
            status_flags.append("SHARED")

        status = f" [{', '.join(status_flags)}]" if status_flags else ""
        return f"{project.name}{status} " f"(ID: {project.id}, Order: {project.order})"
