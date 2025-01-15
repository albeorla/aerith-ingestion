"""
Service for interacting with Todoist API and converting data.
"""

from typing import Dict, List

from loguru import logger
from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Due

from aerith_ingestion.core.base import TracedClass
from aerith_ingestion.core.config import get_settings, log_section
from aerith_ingestion.domain.models import Project, Task, TaskDue


class TodoistService(TracedClass):
    """Service for interacting with Todoist API."""

    def __init__(self):
        """Initialize the Todoist service."""
        settings = get_settings()
        self.api = TodoistAPI(settings.todoist_api_token)

    def _convert_to_dict(self, obj) -> Dict:
        """Convert a Todoist object to a dictionary by getting all public attributes."""
        if isinstance(obj, Due):
            return {
                "date": obj.date,
                "is_recurring": obj.is_recurring,
                "string": obj.string,
                "datetime": str(obj.datetime) if obj.datetime else None,
                "timezone": obj.timezone,
            }

        result = {}
        for key, value in obj.__dict__.items():
            if key.startswith("_"):
                continue
            if isinstance(value, Due):
                result[key] = self._convert_to_dict(value)
            else:
                result[key] = value
        return result

    def fetch_all_data(self) -> List[Dict]:
        """Fetch fresh data from Todoist API"""
        try:
            logger.debug("Fetching projects from Todoist API")
            projects = self.api.get_projects()
            logger.trace("Retrieved {} projects", len(projects))
            project_aggregates = []

            log_section("Fetching Todoist Data")
            for project in projects:
                logger.debug("Fetching tasks for project: {}", project.name)
                tasks = self.api.get_tasks(project_id=project.id)
                logger.trace(
                    "Project {} tasks: {}", project.name, [t.id for t in tasks]
                )

                project_dict = self._convert_to_dict(project)
                project_dict["tasks"] = [self._convert_to_dict(task) for task in tasks]
                project_aggregates.append(project_dict)
                logger.info("{:<15} {} tasks", project.name + ":", len(tasks))

            return project_aggregates

        except Exception as e:
            logger.exception("Failed to fetch data from Todoist")
            raise e

    def convert_to_domain_models(self, project_data: List[Dict]) -> List[Project]:
        """Convert raw API data to domain models"""
        logger.debug("Converting {} projects to domain models", len(project_data))
        projects = []
        for project_dict in project_data:
            logger.trace("Converting project: {}", project_dict["name"])
            # Convert tasks
            tasks = []
            tasks_data = project_dict.pop("tasks", [])
            logger.debug(
                "Converting {} tasks for project {}",
                len(tasks_data),
                project_dict["name"],
            )

            for task_dict in tasks_data:
                # Extract task fields
                task_fields = {
                    "id": task_dict["id"],
                    "content": task_dict["content"],
                    "description": task_dict.get("description", ""),
                    "project_id": task_dict["project_id"],
                    "created_at": task_dict["created_at"],
                    "priority": task_dict.get("priority", 1),
                    "url": task_dict.get("url", ""),
                    "comment_count": task_dict.get("comment_count", 0),
                    "order": task_dict.get("order", 0),
                    "is_completed": task_dict.get("is_completed", False),
                    "labels": task_dict.get("labels", []),
                    "parent_id": task_dict.get("parent_id"),
                    "assignee_id": task_dict.get("assignee_id"),
                    "assigner_id": task_dict.get("assigner_id"),
                    "section_id": task_dict.get("section_id"),
                    "duration": task_dict.get("duration"),
                    "sync_id": task_dict.get("sync_id"),
                }
                logger.trace(
                    "Converting task: {} (ID: {})",
                    task_fields["content"],
                    task_fields["id"],
                )

                # Convert due date if present
                due_data = task_dict.get("due")
                if due_data:
                    due = TaskDue(
                        date=due_data["date"],
                        is_recurring=due_data["is_recurring"],
                        string=due_data["string"],
                        datetime=due_data.get("datetime"),
                        timezone=due_data.get("timezone"),
                    )
                else:
                    due = None

                task = Task(due=due, **task_fields)
                tasks.append(task)

            # Extract project fields
            project_fields = {
                "id": project_dict["id"],
                "name": project_dict["name"],
                "color": project_dict.get("color", "charcoal"),
                "comment_count": project_dict.get("comment_count", 0),
                "is_favorite": project_dict.get("is_favorite", False),
                "is_inbox_project": project_dict.get("is_inbox_project", False),
                "is_shared": project_dict.get("is_shared", False),
                "is_team_inbox": project_dict.get("is_team_inbox", False),
                "can_assign_tasks": project_dict.get("can_assign_tasks"),
                "order": project_dict.get("order", 0),
                "parent_id": project_dict.get("parent_id"),
                "url": project_dict.get("url", ""),
                "view_style": project_dict.get("view_style", "list"),
            }

            project = Project(tasks=tasks, **project_fields)
            projects.append(project)
            logger.debug(
                "Converted project {} with {} tasks", project.name, len(project.tasks)
            )

        return projects
