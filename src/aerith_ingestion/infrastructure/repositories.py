"""
Repository implementations for project storage.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from loguru import logger
from todoist_api_python.models import Project as TodoistProject

from aerith_ingestion.core.base import TracedClass
from aerith_ingestion.domain.models import (
    EnrichedTask,
    Project,
    ProjectRepository,
    Task,
    TaskDue,
)


class JSONProjectRepository(TracedClass, ProjectRepository):
    """JSON file implementation of project storage."""

    def __init__(self, file_path: str = "tmp/projects.json"):
        self.file_path = file_path

    def save(self, projects: List[TodoistProject]) -> None:
        """Save projects to a JSON file."""
        logger.debug("Writing projects to JSON file")
        try:
            projects_data = [
                {
                    "id": p.id,
                    "name": p.name,
                    "color": p.color,
                    "is_shared": p.is_shared,
                    "is_favorite": p.is_favorite,
                    "is_inbox_project": p.is_inbox_project,
                    "view_style": p.view_style,
                    "comment_count": p.comment_count,
                    "order": p.order,
                    "parent_id": p.parent_id,
                    "url": p.url,
                }
                for p in projects
            ]

            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

            with open(self.file_path, "w") as f:
                json.dump(projects_data, f, indent=2)
            logger.debug(f"Successfully wrote projects to {self.file_path}")

        except Exception as e:
            logger.error(f"Failed to write projects to file: {e}")
            raise


class EnrichedTaskRepository:
    """Repository for storing and retrieving enriched tasks"""

    def __init__(self, storage_dir: str = "data/enriched_tasks"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save(self, enriched_task: EnrichedTask) -> None:
        """Save an enriched task to storage"""
        # Create filename from task ID and timestamp
        filename = f"{enriched_task.task.id}.json"
        filepath = self.storage_dir / filename

        # Convert to dictionary for storage
        task_data = {
            "task_id": enriched_task.task.id,
            "project_id": enriched_task.project.id,
            "task": self._task_to_dict(enriched_task.task),
            "project": self._project_to_dict(enriched_task.project),
            "metadata": enriched_task.metadata,
            "embeddings": enriched_task.embeddings,
            "processed_at": enriched_task.processed_at.isoformat(),
        }

        # Save to file
        with open(filepath, "w") as f:
            json.dump(task_data, f, indent=2)

    def get_by_id(self, task_id: str) -> Optional[EnrichedTask]:
        """Retrieve the most recent enriched task by task ID"""
        # Find all files for this task ID
        task_files = list(self.storage_dir.glob(f"{task_id}_*.json"))

        if not task_files:
            return None

        # Get most recent file
        latest_file = max(task_files, key=lambda p: int(p.stem.split("_")[1]))

        # Load and convert back to EnrichedTask
        with open(latest_file) as f:
            data = json.load(f)

        return EnrichedTask(
            task=self._dict_to_task(data["task"]),
            project=self._dict_to_project(data["project"]),
            metadata=data["metadata"],
            embeddings=data["embeddings"],
            processed_at=datetime.fromisoformat(data["processed_at"]),
        )

    def get_all_processed_tasks(self) -> Dict[str, datetime]:
        """Get a dictionary of all processed task IDs and their last
        processed timestamps"""
        processed_tasks = {}
        for file_path in self.storage_dir.glob("*.json"):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    task_id = data["task_id"]
                    processed_at = datetime.fromisoformat(data["processed_at"])

                    # Only keep the most recent processing timestamp
                    if (
                        task_id not in processed_tasks
                        or processed_at > processed_tasks[task_id]
                    ):
                        processed_tasks[task_id] = processed_at
            except Exception as e:
                logger.error(f"Error reading task file {file_path}: {e}")
                continue

        return processed_tasks

    def _task_to_dict(self, task: Task) -> dict:
        """Convert Task to dictionary"""
        task_dict = {
            "id": task.id,
            "content": task.content,
            "description": task.description,
            "project_id": task.project_id,
            "created_at": task.created_at,
            "priority": task.priority,
            "url": task.url,
            "comment_count": task.comment_count,
            "order": task.order,
            "is_completed": task.is_completed,
            "labels": task.labels,
            "parent_id": task.parent_id,
            "assignee_id": task.assignee_id,
            "assigner_id": task.assigner_id,
            "section_id": task.section_id,
            "duration": task.duration,
            "sync_id": task.sync_id,
        }

        if task.due:
            task_dict["due"] = {
                "date": task.due.date,
                "is_recurring": task.due.is_recurring,
                "string": task.due.string,
                "datetime": task.due.datetime,
                "timezone": task.due.timezone,
            }
        else:
            task_dict["due"] = None

        return task_dict

    def _project_to_dict(self, project: TodoistProject) -> dict:
        """Convert Project to dictionary"""
        return {
            "id": project.id,
            "name": project.name,
            "color": project.color,
            "comment_count": project.comment_count,
            "is_favorite": project.is_favorite,
            "is_inbox_project": project.is_inbox_project,
            "is_shared": project.is_shared,
            "is_team_inbox": project.is_team_inbox,
            "can_assign_tasks": project.can_assign_tasks,
            "order": project.order,
            "parent_id": project.parent_id,
            "url": project.url,
            "view_style": project.view_style,
            "tasks": [self._task_to_dict(task) for task in project.tasks],
        }

    def _dict_to_task(self, data: dict) -> Task:
        """Convert dictionary to Task"""
        due_data = data.pop("due")
        if due_data:
            due = TaskDue(**due_data)
        else:
            due = None

        return Task(due=due, **data)

    def _dict_to_project(self, data: dict) -> Project:
        """Convert dictionary to Project"""
        tasks_data = data.pop("tasks")
        tasks = [self._dict_to_task(task_data) for task_data in tasks_data]
        return Project(tasks=tasks, **data)
