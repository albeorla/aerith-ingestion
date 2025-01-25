"""
Todoist API client.

This module provides a client for interacting with the Todoist API.
"""

from typing import Any, Dict, List

import requests
from todoist_api_python.api import TodoistAPI

from aerith_ingestion.config.api import TodoistApiConfig
from aerith_ingestion.integration.todoist.domain.models import Project, Task


class TodoistApiClient:
    """Client for interacting with the Todoist API."""

    def __init__(self, config: TodoistApiConfig):
        """Initialize the client."""
        self.config = config
        self.base_url = "https://api.todoist.com/rest/v2"
        self.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        }
        self.api = TodoistAPI(config.api_key) if config.api_key else None

    def get_all_data(self) -> Dict[str, Any]:
        """Get all projects and tasks from Todoist."""
        projects = self.get_projects()
        tasks = self.get_tasks()
        return {
            "projects": projects,
            "items": tasks,
        }

    def get_projects(self) -> List[Project]:
        """Get all projects from Todoist."""
        # TODO: Implement project fetching
        return []

    def get_tasks(self) -> List[Task]:
        """Get all tasks from Todoist."""
        # TODO: Implement task fetching
        return []


def create_todoist_client(config: TodoistApiConfig) -> TodoistApiClient:
    """Create TodoistApiClient with the provided configuration."""
    return TodoistApiClient(config)
