import os
from datetime import datetime
from typing import Any, Dict, Optional

from ..domain.models import EnrichedTask, Project, Task
from .enrichment import TaskEnrichmentService
from .vector_store import VectorStoreService


class TaskProcessor:
    """
    Service for processing and enriching tasks with additional context
    and metadata
    """

    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.enrichment_service = TaskEnrichmentService(openai_api_key=openai_api_key)
        self.vector_store = VectorStoreService()

    def process_task(
        self,
        task: Task,
        project: Project,
        previous_task: Optional[EnrichedTask] = None,
    ) -> Optional[EnrichedTask]:
        """
        Process a single task and enrich it with metadata.
        Returns None if no changes detected.
        """

        # If we have a previous version, check if content has changed
        if (
            previous_task
            and task.get_content_hash() == previous_task.task.get_content_hash()
        ):
            return None

        # Extract base metadata
        metadata = self._extract_metadata(task, project)

        # Enrich with LangChain/OpenAI analysis for the individual task
        enrichment_data = self.enrichment_service.analyze_task(task)
        metadata.update(enrichment_data)

        # Create enriched task
        enriched_task = EnrichedTask(
            task=task,
            project=project,
            metadata=metadata,
            embeddings=enrichment_data["embeddings"],
            vector_metadata=None,  # Will be set after vector store update
            processed_at=datetime.now(),
        )

        # Update vector store and get vector metadata
        vector_metadata = self.vector_store.upsert_task(enriched_task)
        enriched_task.vector_metadata = vector_metadata

        return enriched_task

    def _extract_metadata(self, task: Task, project: Project) -> Dict[str, Any]:
        """Extract and process metadata from task and project"""
        metadata = {
            "project_name": project.name,
            "project_type": self._determine_project_type(project),
            "task_type": self._determine_task_type(task),
            "priority_level": self._get_priority_level(task.priority),
            "has_due_date": task.due is not None,
            "is_recurring": task.due.is_recurring if task.due else False,
            "has_description": bool(task.description.strip()),
            "has_comments": task.comment_count > 0,
            "is_subtask": task.parent_id is not None,
            "has_assignee": task.assignee_id is not None,
            "project_context": {
                "is_favorite": project.is_favorite,
                "is_shared": project.is_shared,
                "is_inbox": project.is_inbox_project,
                "is_team_inbox": project.is_team_inbox,
            },
        }

        # Add temporal metadata
        if task.due:
            metadata.update(self._extract_temporal_metadata(task))

        return metadata

    def _determine_project_type(self, project: Project) -> str:
        """Determine the type of project based on its characteristics"""
        if project.is_inbox_project:
            return "inbox"
        elif project.is_team_inbox:
            return "team_inbox"
        elif project.is_shared:
            return "shared"
        else:
            return "personal"

    def _determine_task_type(self, task: Task) -> str:
        """Determine the type of task based on its characteristics"""
        if task.parent_id:
            return "subtask"
        elif task.due and task.due.is_recurring:
            return "recurring"
        elif task.assignee_id:
            return "assigned"
        else:
            return "standard"

    def _get_priority_level(self, priority: int) -> str:
        """Convert numeric priority to string representation"""
        priority_map = {1: "low", 2: "medium", 3: "high", 4: "urgent"}
        return priority_map.get(priority, "none")

    def _extract_temporal_metadata(self, task: Task) -> Dict[str, Any]:
        """Extract temporal metadata from task due date"""
        if not task.due:
            return {}

        return {
            "due_date": task.due.date,
            "due_datetime": task.due.datetime,
            "due_timezone": task.due.timezone,
            "due_string": task.due.string,
        }
