"""
Main entry point for the Todoist ingestion application.
"""

import logging
import os
import time
from collections import defaultdict

# Configure logging before imports
logging.getLogger("nltk").setLevel(logging.ERROR)

# Third party imports
import nltk  # noqa: E402
from loguru import logger  # noqa: E402

# Local imports
from aerith_ingestion.core.config import log_section  # noqa: E402
from aerith_ingestion.infrastructure.repositories import (  # noqa: E402
    EnrichedTaskRepository,
)
from aerith_ingestion.services.task_processor import TaskProcessor  # noqa: E402
from aerith_ingestion.services.todoist import TodoistService  # noqa: E402

# Configure NLTK silently
os.environ["NLTK_DATA"] = os.path.join(os.path.dirname(__file__), "nltk_data")
nltk.data.path = [os.environ["NLTK_DATA"]]
nltk.download("punkt", quiet=True)


def process_projects() -> None:
    """Process all tasks in all projects"""
    start_time = time.time()
    processor = TaskProcessor()
    repository = EnrichedTaskRepository()
    todoist_service = TodoistService()

    logger.debug("Initializing task processing")
    log_section("Starting Todoist Sync")
    processed_tasks = repository.get_all_processed_tasks()
    logger.info("Found {} existing tasks", len(processed_tasks))
    logger.trace("Existing task IDs: {}", list(processed_tasks))

    # Fetch and convert Todoist data
    fetch_start = time.time()
    logger.debug("Fetching data from Todoist API")
    project_data = todoist_service.fetch_all_data()
    fetch_time = time.time() - fetch_start

    convert_start = time.time()
    logger.debug("Converting Todoist data to domain models")
    projects = todoist_service.convert_to_domain_models(project_data)
    convert_time = time.time() - convert_start
    logger.trace(
        "Converted {} projects with {} total tasks",
        len(projects),
        sum(len(p.tasks) for p in projects),
    )

    skipped_tasks = []
    newly_processed_tasks = []

    # Process each project's tasks
    logger.debug("Processing tasks from all projects")
    for project in projects:
        logger.debug("Processing project: {}", project.name)
        for task in project.tasks:
            if task.id in processed_tasks:
                skipped_tasks.append((task.id, project.name))
                logger.trace("Skipping task {} from {}", task.id, project.name)
                continue

            enriched_task = processor.process_task(task, project, None)
            if enriched_task:
                repository.save(enriched_task)
                newly_processed_tasks.append((task.id, project.name))
                logger.debug("Processed task {} from {}", task.id, project.name)

    total_time = time.time() - start_time

    # Log final summary
    log_section("Processing Summary")
    logger.info("Tasks processed: {}", len(newly_processed_tasks))
    logger.info("Tasks skipped: {}", len(skipped_tasks))
    logger.trace("Processed task IDs: {}", [t[0] for t in newly_processed_tasks])
    logger.trace("Skipped task IDs: {}", [t[0] for t in skipped_tasks])

    if skipped_by_project := defaultdict(list):
        for task_id, project_name in skipped_tasks:
            skipped_by_project[project_name].append(task_id)

        log_section("Project Details")
        for project, tasks in sorted(skipped_by_project.items()):
            logger.info("{}: {} tasks", project, len(tasks))
            logger.trace("Project {} task IDs: {}", project, tasks)

    log_section("Performance")
    logger.info("Fetch time:    {:.2f}s", fetch_time)
    logger.info("Convert time:  {:.2f}s", convert_time)
    logger.info("Total time:    {:.2f}s", total_time)
    logger.debug(
        "Performance breakdown - Fetch: {:.1f}%, Convert: {:.1f}%, Other: {:.1f}%",
        (fetch_time / total_time) * 100,
        (convert_time / total_time) * 100,
        ((total_time - fetch_time - convert_time) / total_time) * 100,
    )


def main():
    """Main entry point"""
    try:
        process_projects()
    except Exception:
        logger.exception("Error during task processing")
        raise
    else:
        logger.success("Task processing completed successfully")


if __name__ == "__main__":
    main()
