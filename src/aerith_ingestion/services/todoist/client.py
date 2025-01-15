"""
Todoist API client.

This module provides a client for interacting with the Todoist API.
"""

from typing import Any, Dict, List

import requests

from aerith_ingestion.config.api import TodoistApiConfig


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

    def get_all_data(self) -> Dict[str, Any]:
        """Get all projects and tasks from Todoist."""
        projects = self.get_projects()
        tasks = self.get_tasks()
        return {
            "projects": projects,
            "items": tasks,
        }

    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects from Todoist."""
        response = requests.get(
            f"{self.base_url}/projects",
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()

    def get_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks from Todoist."""
        response = requests.get(
            f"{self.base_url}/tasks",
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()


def create_todoist_client(config: TodoistApiConfig) -> TodoistApiClient:
    """Create TodoistApiClient with the provided configuration."""
    return TodoistApiClient(config)
