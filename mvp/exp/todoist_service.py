from typing import Dict, List, Optional

import backoff
import requests
from interfaces import EnvironmentConfigProtocol
from requests.exceptions import RequestException


class TodoistService:
    """Service to interact with the Todoist API."""

    def __init__(self, env_config: EnvironmentConfigProtocol):
        self.env_config = env_config
        self.api_token = self.env_config.get_todoist_api_token()
        self.logger = env_config.get_logger()
        if not self.api_token:
            self.logger.error("Todoist API token is not set in the environment.")
            raise ValueError("Todoist API token is not set in the environment.")

    @backoff.on_exception(
        backoff.expo,
        RequestException,
        max_tries=3,
        jitter=backoff.full_jitter,
    )
    def _make_request(
        self, url: str, params: Optional[Dict] = None
    ) -> Optional[List[Dict]]:
        """Make a request to the Todoist API with retry logic."""
        headers = {"Authorization": f"Bearer {self.api_token}"}
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            self.logger.error(f"Request error: {e}")
            raise  # Let backoff handle retries
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return None

    def fetch_projects(self) -> Optional[List[Dict]]:
        """Fetches projects from the Todoist API."""
        url = "https://api.todoist.com/rest/v2/projects"
        try:
            projects = self._make_request(url)
            if projects:
                self.logger.info(f"Successfully fetched {len(projects)} projects")
                return projects
            return None
        except Exception as e:
            self.logger.error(f"Error fetching projects: {e}")
            return None

    def fetch_tasks_for_project(self, project_id: str) -> Optional[List[Dict]]:
        """Fetches tasks for a specific project."""
        url = "https://api.todoist.com/rest/v2/tasks"
        params = {"project_id": project_id}
        try:
            tasks = self._make_request(url, params)
            if tasks:
                self.logger.info(
                    f"Successfully fetched {len(tasks)} tasks for project {project_id}"
                )
                return tasks
            return None
        except Exception as e:
            self.logger.error(f"Error fetching tasks for project {project_id}: {e}")
            return None

    def fetch_all_tasks(self, projects: List[Dict]) -> Dict[str, List[Dict]]:
        """Fetches tasks for all projects with error handling."""
        all_tasks = {}
        for project in projects:
            project_id = project.get("id")
            project_name = project.get("name")
            if not project_id or not project_name:
                self.logger.warning(f"Skipping invalid project: {project}")
                continue

            self.logger.info(
                f"Fetching tasks for project: {project_name} (ID: {project_id})"
            )
            try:
                tasks = self.fetch_tasks_for_project(project_id)
                if tasks is not None:
                    self.logger.info(
                        f"Fetched {len(tasks)} tasks for project: {project_name}"
                    )
                    all_tasks[project_name] = tasks
                else:
                    self.logger.warning(
                        f"No tasks retrieved for project: {project_name}"
                    )
                    all_tasks[project_name] = []
            except Exception as e:
                self.logger.error(f"Error processing project {project_name}: {e}")
                all_tasks[project_name] = []

        return all_tasks
