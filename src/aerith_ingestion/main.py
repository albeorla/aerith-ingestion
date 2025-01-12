"""
Main entry point for the Todoist ingestion application.
"""

import json
from pathlib import Path
from typing import Dict, List

from loguru import logger
from todoist_api_python.models import Due

from aerith_ingestion.domain.models import Project, Task, TaskDue
from aerith_ingestion.infrastructure.repositories import EnrichedTaskRepository
from aerith_ingestion.services.task_processor import TaskProcessor
from aerith_ingestion.services.todoist import TodoistService


def convert_to_dict(obj):
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
            result[key] = convert_to_dict(value)
        else:
            result[key] = value
    return result


def fetch_todoist_data() -> List[Dict]:
    """Fetch fresh data from Todoist API"""
    try:
        todoist_service = TodoistService()

        # Get all projects and tasks
        projects = todoist_service.api.get_projects()
        project_aggregates = []

        for project in projects:
            tasks = todoist_service.api.get_tasks(project_id=project.id)
            project_dict = convert_to_dict(project)
            project_dict["tasks"] = [convert_to_dict(task) for task in tasks]
            project_aggregates.append(project_dict)
            logger.info(f"Fetched {len(tasks)} tasks for project {project.name}")

        return project_aggregates

    except Exception as e:
        logger.exception(f"Failed to fetch data from Todoist: {e}")
        raise


def convert_to_domain_models(project_data: List[Dict]) -> List[Project]:
    """Convert raw API data to domain models"""
    projects = []
    for project_dict in project_data:
        # Convert tasks
        tasks = []
        tasks_data = project_dict.pop("tasks", [])

        for task_dict in tasks_data:
            # Extract only the fields we want for Task
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

            # Create task
            task = Task(due=due, **task_fields)
            tasks.append(task)

        # Extract only the fields we want for Project
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

        # Create project with tasks
        project = Project(tasks=tasks, **project_fields)
        projects.append(project)

    return projects


def process_projects(projects: List[Project]) -> None:
    """Process all tasks in all projects"""
    processor = TaskProcessor()
    repository = EnrichedTaskRepository()

    # Get all previously processed tasks and their timestamps
    processed_tasks = repository.get_all_processed_tasks()
    logger.info(f"Found {len(processed_tasks)} previously processed tasks")

    processed_count = 0
    skipped_count = 0
    skipped_tasks = []

    for project in projects:
        for task in project.tasks:
            # Skip if we've already processed this task
            if task.id in processed_tasks:
                skipped_count += 1
                skipped_tasks.append((task.id, project.name))
                logger.debug(
                    f"Skipping already processed task {task.id} from project "
                    f"{project.name}"
                )
                continue

            # Process new task
            enriched_task = processor.process_task(
                task, project, None
            )  # No previous version needed for new tasks

            if enriched_task:
                repository.save(enriched_task)
                processed_count += 1
                logger.info(
                    f"Processed and saved new task {task.id} from project "
                    f"{project.name}"
                )

    # Log summary
    logger.info(
        f"Processing complete: {processed_count} new tasks processed, "
        f"{skipped_count} existing tasks skipped"
    )
    if skipped_tasks:
        logger.info("Skipped tasks:")
        for task_id, project_name in skipped_tasks:
            logger.info(f"  - Task {task_id} in project {project_name}")


def main():
    # Fetch fresh data from Todoist
    logger.info("Fetching data from Todoist API...")
    project_data = fetch_todoist_data()

    # Save raw data for reference
    output_path = Path("tmp/project_aggregates.json")
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(project_data, f, indent=2)
    logger.info(f"Saved raw project data to {output_path}")

    # Convert to domain models
    logger.info("Converting to domain models...")
    projects = convert_to_domain_models(project_data)

    # Process all tasks
    logger.info("Processing tasks...")
    process_projects(projects)
    logger.info("Task processing complete")


if __name__ == "__main__":
    main()
