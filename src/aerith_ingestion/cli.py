"""
Command-line interface for Aerith ingestion.
"""

import time
from collections import defaultdict

import click
from loguru import logger

from aerith_ingestion.api.server import run_server
from aerith_ingestion.core.config import log_section
from aerith_ingestion.infrastructure.repositories import EnrichedTaskRepository
from aerith_ingestion.services.task_processor import TaskProcessor
from aerith_ingestion.services.todoist import TodoistService
from aerith_ingestion.utils.vector_viz import visualize_embeddings


@click.group()
def cli():
    """Aerith ingestion CLI"""
    pass


@cli.command()
@click.option("--host", default="0.0.0.0", help="Server host")
@click.option("--port", default=8000, help="Server port")
def serve(host: str, port: int):
    """Run the API server"""
    try:
        run_server(host, port)
    except Exception:
        logger.exception("Error running server")
        raise


@cli.command()
@click.option(
    "--force", "-f", is_flag=True, help="Force sync all tasks, ignoring cache"
)
@click.option("--project", "-p", help="Sync specific project only")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed progress")
def sync(force: bool, project: str | None = None, verbose: bool = False):
    """Sync and process Todoist tasks"""
    try:
        start_time = time.time()
        processor = TaskProcessor()
        repository = EnrichedTaskRepository()
        todoist_service = TodoistService()

        logger.debug("Initializing task processing")
        log_section("Starting Todoist Sync")

        if not force:
            processed_tasks = repository.get_all_processed_tasks()
            logger.info("Found {} existing tasks", len(processed_tasks))
            if verbose:
                logger.trace("Existing task IDs: {}", list(processed_tasks))
        else:
            processed_tasks = set()
            logger.info("Force sync enabled - processing all tasks")

        # Fetch and convert Todoist data
        with click.progressbar(length=2, label="Fetching data", show_eta=True) as bar:
            fetch_start = time.time()
            logger.debug("Fetching data from Todoist API")
            project_data = todoist_service.fetch_all_data()
            fetch_time = time.time() - fetch_start
            bar.update(1)

            convert_start = time.time()
            logger.debug("Converting Todoist data to domain models")
            projects = todoist_service.convert_to_domain_models(project_data)
            convert_time = time.time() - convert_start
            bar.update(1)

        if verbose:
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
            if project and project.id != project:
                logger.debug("Skipping project: {}", project.name)
                continue

            logger.debug("Processing project: {}", project.name)
            with click.progressbar(
                project.tasks, label=f"Processing {project.name}", show_eta=True
            ) as tasks:
                for task in tasks:
                    if not force and task.id in processed_tasks:
                        skipped_tasks.append((task.id, project.name))
                        if verbose:
                            logger.trace(
                                "Skipping task {} from {}", task.id, project.name
                            )
                        continue

                    enriched_task = processor.process_task(task, project, None)
                    if enriched_task:
                        repository.save(enriched_task)
                        newly_processed_tasks.append((task.id, project.name))
                        if verbose:
                            logger.debug(
                                "Processed task {} from {}", task.id, project.name
                            )

        total_time = time.time() - start_time

        # Log final summary
        log_section("Processing Summary")
        logger.info("Tasks processed: {}", len(newly_processed_tasks))
        logger.info("Tasks skipped: {}", len(skipped_tasks))

        if verbose:
            logger.trace(
                "Processed task IDs: {}", [t[0] for t in newly_processed_tasks]
            )
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

        if verbose:
            logger.debug(
                "Performance breakdown - "
                "Fetch: {:.1f}%, Convert: {:.1f}%, Other: {:.1f}%",
                (fetch_time / total_time) * 100,
                (convert_time / total_time) * 100,
                ((total_time - fetch_time - convert_time) / total_time) * 100,
            )

    except Exception:
        logger.exception("Error during task processing")
        raise
    else:
        logger.success("Task processing completed successfully")


@cli.command()
@click.option("--output", "-o", default="vector_viz.html", help="Output HTML file")
@click.option(
    "--dimensions", "-d", default=2, type=int, help="Number of dimensions (2 or 3)"
)
def viz(output: str, dimensions: int):
    """Visualize task vector embeddings"""
    try:
        logger.info("Generating vector visualization...")
        visualize_embeddings(output_file=output, dimensions=dimensions)
        logger.success("Vector visualization saved to {}", output)
    except Exception:
        logger.exception("Error generating visualization")
        raise


if __name__ == "__main__":
    cli()
