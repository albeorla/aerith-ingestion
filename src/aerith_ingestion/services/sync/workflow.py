"""
Todoist synchronization workflow.

This module provides the workflow for synchronizing data with Todoist:
1. Fetch data from Todoist API
2. Map to domain models
3. Persist to local storage
"""

from typing import List, Tuple

from aerith_ingestion.domain.project import Project
from aerith_ingestion.domain.task import Task
from aerith_ingestion.persistence.project import SQLiteProjectRepository
from aerith_ingestion.persistence.task import SQLiteTaskRepository
from aerith_ingestion.services.todoist import TodoistApiClient, TodoistDataMapper


class TodoistSyncWorkflow:
    """Workflow for synchronizing data with Todoist."""

    def __init__(
        self,
        api_client: TodoistApiClient,
        data_mapper: TodoistDataMapper,
        task_repository: SQLiteTaskRepository,
        project_repository: SQLiteProjectRepository,
    ):
        """Initialize the workflow."""
        self.api_client = api_client
        self.data_mapper = data_mapper
        self.task_repository = task_repository
        self.project_repository = project_repository

    def sync_all(self) -> Tuple[List[Project], List[Task]]:
        """Synchronize all data from Todoist."""
        # Fetch data
        raw_data = self.api_client.get_all_data()

        # Map to domain models
        projects = self.data_mapper.map_projects(raw_data)
        tasks = self.data_mapper.map_tasks(raw_data)

        # Persist data
        self.project_repository.save_all(projects)
        self.task_repository.save_all(tasks)

        return projects, tasks


def create_sync_workflow(
    api_client: TodoistApiClient,
    data_mapper: TodoistDataMapper,
    task_repository: SQLiteTaskRepository,
    project_repository: SQLiteProjectRepository,
) -> TodoistSyncWorkflow:
    """Create TodoistSyncWorkflow with its dependencies."""
    return TodoistSyncWorkflow(
        api_client=api_client,
        data_mapper=data_mapper,
        task_repository=task_repository,
        project_repository=project_repository,
    )
