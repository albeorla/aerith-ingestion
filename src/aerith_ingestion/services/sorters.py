"""
Project sorting implementations.
"""

from typing import List

from todoist_api_python.models import Project

from aerith_ingestion.core.base import TracedClass
from aerith_ingestion.domain.models import ProjectSorter


class DefaultProjectSorter(TracedClass, ProjectSorter):
    """Default implementation of project sorting."""

    def sort(self, projects: List[Project]) -> List[Project]:
        """Sort projects by priority: Inbox first, then by order and name."""

        def sort_key(p: Project):
            inbox_priority = -1 if p.is_inbox_project else 0
            order = p.order or 0
            name = p.name or ""
            return (inbox_priority, order, name)

        return sorted(projects, key=sort_key)
