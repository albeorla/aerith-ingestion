"""Main pipeline for processing Todoist tasks with GTD principles."""

import asyncio
import datetime
import logging
import random
import time
import uuid
from typing import List, Union

from backoff_config import BackoffConfig, CircuitBreaker, CircuitBreakerConfig
from data_storage import DataStorage
from environment_config import EnvironmentConfig
from error_handler import ErrorContext, ErrorHandler, ErrorSeverity
from gemini_service import GeminiService
from gtd_processor import GTDProcessor
from interfaces import DataStorageProtocol, GTDProcessorProtocol, LoggerProtocol
from models import GTDTaskOutput, TaskModel
from monitoring import MonitoringDashboard
from prefect import flow, get_run_logger, task
from prompt_templates import GTD_LEVEL_DEFINITIONS, get_task_categorization_prompt
from rate_limiter import QuotaConfig, RateLimiter
from request_manager import BatchConfig, Request, RequestManager, RequestPriority
from todoist_service import TodoistService

# TODO: Implement pipeline-level protections
# TODO: Add request deduplication across pipeline stages
# TODO: Add performance monitoring and metrics collection
# TODO: Implement smart batching and queueing
# TODO: Add failure recovery mechanisms

# Configure Prefect logger for enhanced console and file logging
prefect_logger = logging.getLogger("prefect")
prefect_logger.setLevel(logging.DEBUG)  # Set log level to DEBUG for detailed logging

# Create console handler with DEBUG level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create formatter and add it to the console handler
console_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
console_handler.setFormatter(console_formatter)

# Add the console handler to the Prefect logger if it doesn't already have handlers
if not prefect_logger.hasHandlers():
    prefect_logger.addHandler(console_handler)

# Prevent duplicate logs by disabling propagation if handlers are already set
prefect_logger.propagate = False

# Create file handler with WRITE mode to overwrite the log file on each run
file_handler = logging.FileHandler("pipeline.log", mode="w")
file_handler.setLevel(logging.DEBUG)

# Create formatter and add it to the file handler
file_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
file_handler.setFormatter(file_formatter)

# Add the file handler to the Prefect logger
prefect_logger.addHandler(file_handler)


@task
def initialize_services(logger: LoggerProtocol, monitor: MonitoringDashboard):
    """Initialize the services with enhanced configuration."""
    env_config = EnvironmentConfig(logger)
    logger.info("Environment Configuration:")
    logger.info(env_config.get_config_as_str())

    # Initialize error handling
    error_handler = ErrorHandler(logger)

    # Initialize rate limiting
    quota_config = QuotaConfig(
        requests_per_minute=30, min_delay_between_requests=2.0, cooldown_duration=30.0
    )
    rate_limiter = RateLimiter(quota_config)

    # Initialize circuit breaker
    circuit_breaker = CircuitBreaker(CircuitBreakerConfig())

    # Initialize request management
    batch_config = BatchConfig(
        max_batch_size=50, max_wait_time=2.0, min_batch_size=5, max_token_limit=8000
    )

    # Initialize services with enhanced configuration
    gemini_service = GeminiService(
        env_config, rate_limiter=rate_limiter, error_handler=error_handler
    )

    gtd_processor = GTDProcessor(
        env_config,
        gemini_service,
        request_manager=RequestManager(
            batch_processor=gemini_service.process_batch,
            batch_config=batch_config,
            logger=logger,
            monitor=monitor,
        ),
    )

    data_storage = DataStorage(env_config)

    # Inject monitor into services
    gtd_processor.request_manager.monitor = monitor

    return gtd_processor, data_storage, error_handler


@task(retries=3, retry_delay_seconds=10)
async def fetch_projects(
    data_storage: DataStorageProtocol,
    error_handler: ErrorHandler,
    cache_path="output/projects.json",
):
    """Fetch projects with enhanced error handling."""
    logger = get_run_logger()

    try:
        # Check cache first
        projects = data_storage.load_json(cache_path)
        if projects:
            logger.info(f"Loaded {len(projects)} projects from cache.")
            return projects

        # Initialize TodoistService and fetch projects
        logger.info("Fetching projects from Todoist API...")
        env_config = EnvironmentConfig(logger)
        todoist_service = TodoistService(env_config)

        context = ErrorContext(
            service="todoist_service",
            operation="fetch_projects",
            request_id=str(uuid.uuid4()),
        )

        projects = await todoist_service.fetch_projects()
        if not projects:
            await error_handler.handle_error(
                Exception("Failed to fetch projects"), context, ErrorSeverity.HIGH
            )
            return []

        # Save to cache
        data_storage.save_json(projects, cache_path)
        logger.info(f"Saved {len(projects)} projects to cache at {cache_path}")

        return projects

    except Exception as e:
        context = ErrorContext(
            service="fetch_projects", operation="main", request_id=str(uuid.uuid4())
        )
        await error_handler.handle_error(e, context, ErrorSeverity.HIGH)
        raise


@task(retries=3, retry_delay_seconds=10)
async def fetch_tasks(
    projects: list,
    data_storage: DataStorageProtocol,
    error_handler: ErrorHandler,
    cache_path="output/tasks.json",
):
    """Fetch tasks with enhanced error handling and batching."""
    logger = get_run_logger()

    try:
        # Check cache first
        tasks = data_storage.load_json(cache_path)
        if tasks:
            logger.info(f"Loaded tasks structure: {type(tasks)}")
            if isinstance(tasks, dict):
                logger.info(f"Sample project-level aggregate: {list(tasks.items())[0]}")
                return tasks
            elif isinstance(tasks, list):
                logger.info(f"Sample flat task: {tasks[0]}")
                return {"FlatTasks": tasks}

        # Initialize services
        env_config = EnvironmentConfig(logger)
        todoist_service = TodoistService(env_config)

        context = ErrorContext(
            service="todoist_service",
            operation="fetch_tasks",
            request_id=str(uuid.uuid4()),
        )

        # Fetch tasks with batching
        tasks = {}
        for project in projects:
            try:
                project_tasks = await todoist_service.fetch_project_tasks(
                    project["id"], batch_size=50
                )
                if project_tasks:
                    tasks[project["name"]] = project_tasks
            except Exception as e:
                await error_handler.handle_error(e, context, ErrorSeverity.MEDIUM)

        if not tasks:
            await error_handler.handle_error(
                Exception("Failed to fetch any tasks"), context, ErrorSeverity.HIGH
            )
            return {}

        # Save to cache
        data_storage.save_json(tasks, cache_path)
        logger.info(f"Saved tasks for {len(tasks)} projects to cache")

        return tasks

    except Exception as e:
        context = ErrorContext(
            service="fetch_tasks", operation="main", request_id=str(uuid.uuid4())
        )
        await error_handler.handle_error(e, context, ErrorSeverity.HIGH)
        raise


@task
async def filter_existing_tasks(
    raw_tasks: list,
    existing_tasks_path: str,
    data_storage: DataStorageProtocol,
    error_handler: ErrorHandler,
) -> list:
    """Filter tasks with deduplication."""
    logger = get_run_logger()

    try:
        logger.info("Loading existing tasks from JSONL file...")
        existing_tasks = data_storage.load_jsonl(existing_tasks_path)
        if existing_tasks is None:
            logger.warning("No existing tasks found.")
            existing_tasks = []

        existing_task_ids = {task["id"] for task in existing_tasks if task is not None}
        logger.info(f"Loaded {len(existing_task_ids)} existing tasks.")

        new_tasks = [task for task in raw_tasks if task["id"] not in existing_task_ids]
        logger.info(f"Filtered to {len(new_tasks)} new tasks.")
        return new_tasks

    except Exception as e:
        context = ErrorContext(
            service="filter_tasks", operation="main", request_id=str(uuid.uuid4())
        )
        await error_handler.handle_error(e, context, ErrorSeverity.MEDIUM)
        return []


@task
def flatten_tasks(
    project_aggregates: Union[dict, list], error_handler: ErrorHandler
) -> list[dict]:
    """Flatten tasks with error handling."""
    logger = get_run_logger()

    try:
        logger.info("Flattening tasks from project-level aggregates...")

        if isinstance(project_aggregates, list):
            return project_aggregates

        flat_tasks = []
        for project_name, tasks in project_aggregates.items():
            for task in tasks:
                if isinstance(task, TaskModel):
                    task = task.dict()
                task["source_project"] = project_name
                flat_tasks.append(task)

        logger.info(f"Flattened {len(flat_tasks)} tasks.")
        return flat_tasks

    except Exception as e:
        context = ErrorContext(
            service="flatten_tasks", operation="main", request_id=str(uuid.uuid4())
        )
        error_handler.handle_error(e, context, ErrorSeverity.MEDIUM)
        return []


@task
async def validate_and_categorize_tasks(
    gtd_processor: GTDProcessorProtocol,
    tasks: List[TaskModel],
    error_handler: ErrorHandler,
) -> List[GTDTaskOutput]:
    """Validate and process tasks with error tracking."""
    validated_tasks = []

    # NEW: Input validation
    if not isinstance(tasks, list) or len(tasks) == 0:
        error_handler.logger.error("Invalid tasks input - expected non-empty list")
        return []

    # Existing processing logic...
    try:
        batch_result = await gtd_processor.process_tasks_parallel(tasks)
        validated_tasks = [
            GTDTaskOutput.from_task_model(t) for t in batch_result.processed_tasks
        ]
    except Exception as e:
        error_handler.logger.error(f"Critical error during processing: {e}")
        raise

    # NEW: Output validation
    if len(validated_tasks) != len(tasks):
        error_handler.logger.warning(
            f"Task count mismatch: Input {len(tasks)} vs Output {len(validated_tasks)}"
        )

    return validated_tasks


@task
async def save_results(
    data_storage: DataStorageProtocol,
    categorized_tasks: list[TaskModel],
    error_handler: ErrorHandler,
):
    """Save results with error handling."""
    logger = get_run_logger()
    gtd_tasks_path = "./output/tasks_gtd_prioritized.jsonl"

    try:
        logger.info(f"Saving categorized tasks to: {gtd_tasks_path}")

        # Convert to GTDTaskOutput objects
        output_tasks = [
            GTDTaskOutput.from_task_model(task)
            for task in categorized_tasks
            if task is not None
        ]

        logger.info(f"Number of tasks to save: {len(output_tasks)}")
        if output_tasks:
            logger.info(f"Sample task to save: {output_tasks[0].model_dump()}")

        # Convert to JSONL format
        jsonl_data = [task.to_jsonl() for task in output_tasks]

        # Add summary statistics
        summary = {
            "total_tasks": len(output_tasks),
            "successful_categorizations": len(
                [t for t in output_tasks if t.gtd_level != "Unknown"]
            ),
            "failed_categorizations": len(
                [t for t in output_tasks if t.gtd_level == "Unknown"]
            ),
            "errors": [t.error_messages for t in output_tasks if t.error_messages],
            "timestamp": datetime.datetime.now().isoformat(),
        }

        # Save both tasks and summary
        data_storage.save_json(summary, f"{gtd_tasks_path}.summary.json")
        data_storage.save_jsonl(jsonl_data, gtd_tasks_path)

        logger.info(f"Results saved successfully to: {gtd_tasks_path}")

    except Exception as e:
        context = ErrorContext(
            service="save_results", operation="main", request_id=str(uuid.uuid4())
        )
        await error_handler.handle_error(e, context, ErrorSeverity.HIGH)
        raise


@flow(
    retries=7,
    retry_delay_seconds=BackoffConfig.DEFAULT_INITIAL_WAIT,
    timeout_seconds=3600,
)
async def todoist_pipeline():
    """Main pipeline with monitoring and alerts"""
    # Configure Prefect logger (already configured above)
    monitor = MonitoringDashboard()
    logger = get_run_logger()
    logger.info("Pipeline started: Initializing services...")

    # Initialize error_handler before the try block to ensure it's available in except
    error_handler = ErrorHandler(logger)

    try:
        gtd_processor, data_storage = initialize_services(logger, monitor)

        # Stage 1: Fetch and prepare data
        projects = await fetch_projects(data_storage, error_handler)
        raw_tasks = await fetch_tasks(projects, data_storage, error_handler)
        flat_tasks = await flatten_tasks(raw_tasks, error_handler)
        new_tasks = await filter_existing_tasks(
            flat_tasks,
            "./output/tasks_gtd_prioritized.jsonl",
            data_storage,
            error_handler,
        )

        if not new_tasks:
            logger.warning("No new tasks to process.")
            return

        # Stage 2: Process tasks
        categorized_tasks = await validate_and_categorize_tasks(
            gtd_processor, new_tasks, error_handler
        )

        # Stage 3: Save results
        await save_results(data_storage, categorized_tasks, error_handler)

        # Export error report
        error_handler.export_error_report("./output/error_report.json")

        # NEW: Check for critical alerts
        alerts = monitor.check_alert_conditions()
        if alerts:
            logger.error("CRITICAL ALERTS:\n• " + "\n• ".join(alerts))

    except Exception as e:
        context = ErrorContext(
            service="pipeline", operation="main", request_id=str(uuid.uuid4())
        )
        await error_handler.handle_error(e, context, ErrorSeverity.FATAL)
        raise

    finally:
        logger.info("Pipeline execution completed.")
        logger.info(monitor.get_metrics_report())


if __name__ == "__main__":
    asyncio.run(todoist_pipeline())
