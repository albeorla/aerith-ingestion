"""
Service for interacting with Todoist API.
"""

from loguru import logger
from todoist_api_python.api import TodoistAPI

from aerith_ingestion.core.base import BaseService
from aerith_ingestion.core.config import Settings
from aerith_ingestion.core.logging_aspect import LogMethod


class TodoistService(BaseService):
    """
    Service for interacting with the Todoist API.
    """

    def __init__(self) -> None:
        super().__init__(self.sync_projects_and_tasks)
        self.api = TodoistAPI(Settings().todoist_api_token)

    @LogMethod()
    def sync_projects_and_tasks(self) -> None:
        """
        Synchronizes projects and their tasks from Todoist.
        """
        try:
            projects = self.api.get_projects()
            logger.info(f"Retrieved {len(projects)} projects from Todoist")
            for project in projects:
                logger.info(f"Project: {project.name} (ID: {project.id})")
                self.sync_tasks_for_project(project.id)
        except Exception as e:
            logger.error(f"Error getting projects from Todoist: {e}")

    @LogMethod()
    def sync_tasks_for_project(self, project_id: int) -> None:
        """
        Synchronizes tasks for a specific project from Todoist.
        """
        try:
            tasks = self.api.get_tasks(project_id=project_id)
            logger.info(f"Retrieved {len(tasks)} tasks for project {project_id}")
            for task in tasks:
                logger.info(
                    f"Task: {task.content} (ID: {task.id}, "
                    f"Project ID: {task.project_id})"
                )
        except Exception as e:
            logger.error(
                f"Error getting tasks for project {project_id} from Todoist: {e}"
            )

    @LogMethod()
    def get_task(self, task_id: int) -> None:
        """
        Gets a task from Todoist.
        """
        try:
            task = self.api.get_task(task_id=task_id)
            logger.info(
                f"Task: {task.content} (ID: {task.id}, "
                f"Project ID: {task.project_id})"
            )
        except Exception as e:
            logger.error(f"Error getting task {task_id} from Todoist: {e}")
