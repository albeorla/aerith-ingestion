"""Sync command for synchronizing Todoist data."""

import click
from loguru import logger
from openai import OpenAI

from aerith_ingestion.cli import pass_context
from aerith_ingestion.persistence.database import Database
from aerith_ingestion.persistence.project import SQLiteProjectRepository
from aerith_ingestion.persistence.task import SQLiteTaskRepository
from aerith_ingestion.services.enrichment.analyzer import create_task_analyzer
from aerith_ingestion.services.enrichment.store import create_vector_store
from aerith_ingestion.services.enrichment.workflow import create_enrichment_workflow
from aerith_ingestion.services.sync.workflow import create_sync_workflow
from aerith_ingestion.services.todoist.client import create_todoist_client
from aerith_ingestion.services.todoist.mapper import create_data_mapper


@click.command()
@pass_context
def sync(ctx):
    """Synchronize all Todoist data (projects and tasks).

    This command:
    1. Fetches all projects and tasks from Todoist
    2. Maps data to domain models
    3. Persists data to local storage
    """
    try:
        # Initialize database and repositories
        db = Database(ctx.config.database.sqlite.database_path)
        project_repository = SQLiteProjectRepository(db)
        task_repository = SQLiteTaskRepository(db)

        # Initialize Todoist services
        todoist_client = create_todoist_client(ctx.config.api.todoist)
        data_mapper = create_data_mapper()

        # Initialize enrichment services
        openai_client = OpenAI(api_key=ctx.config.api.openai.api_key)
        vector_store = create_vector_store(
            openai_client=openai_client,
            index_path=ctx.config.api.openai.vector_index_path,
        )
        task_analyzer = create_task_analyzer(ctx.config.api.openai)
        enrichment_workflow = create_enrichment_workflow(task_analyzer, vector_store)

        # Create and run sync workflow
        sync_workflow = create_sync_workflow(
            api_client=todoist_client,
            data_mapper=data_mapper,
            task_repository=task_repository,
            project_repository=project_repository,
            enrichment_workflow=enrichment_workflow,
        )
        projects, tasks = sync_workflow.sync_all()
        logger.info(f"Synchronized {len(projects)} projects and {len(tasks)} tasks")
    except Exception as e:
        logger.exception("Failed to sync data")
        raise click.ClickException(str(e))
