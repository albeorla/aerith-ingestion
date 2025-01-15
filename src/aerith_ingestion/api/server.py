"""
FastAPI server for task search and management.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel

from aerith_ingestion.infrastructure.repositories import EnrichedTaskRepository

app = FastAPI(title="Aerith Task API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchQuery(BaseModel):
    query: str


# Mock tasks for testing
MOCK_TASKS = [
    {
        "id": "task1",
        "content": "Implement user authentication",
        "project": "Backend Development",
        "due_date": datetime.now(timezone.utc).isoformat(),
        "priority": 1,
    },
    {
        "id": "task2",
        "content": "Design landing page",
        "project": "Frontend Development",
        "due_date": None,
        "priority": 2,
    },
    {
        "id": "task3",
        "content": "Write API documentation",
        "project": "Documentation",
        "due_date": datetime.now(timezone.utc).isoformat(),
        "priority": 3,
    },
]


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@app.post("/api/tasks/search")
async def search_tasks(query: SearchQuery) -> List[Dict[str, Any]]:
    """Search for tasks based on query"""
    try:
        logger.info("Received search query: {}", query.query)

        # Try to get real tasks first
        repository = EnrichedTaskRepository()
        storage_dir = Path(repository.storage_dir)
        logger.debug("Looking for tasks in: {}", storage_dir)

        if storage_dir.exists():
            # List all files in storage
            task_files = list(storage_dir.glob("*.json"))
            logger.debug("Found {} task files in storage", len(task_files))

            # Get all task IDs first
            task_ids = repository.get_all_processed_tasks()
            logger.debug("Found {} task IDs in repository", len(task_ids))

            # Get full task data for each ID
            formatted_tasks = []
            for task_id in task_ids:
                logger.debug("Loading task {}", task_id)
                enriched_task = repository.get_by_id(task_id)
                if not enriched_task:
                    logger.warning("Task {} not found", task_id)
                    continue

                logger.debug(
                    "Processing task {} - {}", task_id, enriched_task.task.content
                )
                task_data = {
                    "id": task_id,
                    "content": enriched_task.task.content,
                    "project": enriched_task.project.name,
                    "due_date": (
                        enriched_task.task.due.datetime
                        if enriched_task.task.due
                        else None
                    ),
                    "priority": enriched_task.task.priority,
                }
                logger.debug("Formatted task data: {}", task_data)
                formatted_tasks.append(task_data)

            if formatted_tasks:
                logger.info("Returning {} real tasks", len(formatted_tasks))
                return formatted_tasks

        # If no real tasks found, return mock tasks
        logger.info("No real tasks found, returning {} mock tasks", len(MOCK_TASKS))
        return MOCK_TASKS

    except Exception as e:
        logger.exception("Error searching tasks")
        raise HTTPException(status_code=500, detail=str(e))


def run_server(
    host: str = "0.0.0.0", port: int = 8000, reload: bool = True, workers: int = 1
) -> None:
    """Run the FastAPI server

    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload on code changes
        workers: Number of worker processes
    """
    import uvicorn

    logger.info(
        "Starting API server on {}:{} (reload={}, workers={})",
        host,
        port,
        reload,
        workers,
    )
    uvicorn.run(
        "aerith_ingestion.api.server:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        log_level="info",
    )
