import asyncio
import datetime
import json
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from functools import partial
from typing import Any, Dict, List, NamedTuple, Optional, Tuple

import backoff
from backoff_config import BackoffConfig
from gemini_service import GeminiService
from interfaces import (
    EnvironmentConfigProtocol,
    GeminiServiceProtocol,
    GTDProcessorProtocol,
    LoggerProtocol,
)
from models import ContentInfo, TaskModel
from monitoring import MonitoringDashboard

# TODO: Implement smart batching and queue management
# TODO: Add task state tracking and persistence
# TODO: Add failure recovery mechanisms
# TODO: Implement request deduplication
# TODO: Add performance monitoring and metrics


@dataclass
class TaskProcessingResult:
    """Container for task processing results."""

    # TODO: Add fields for:
    # - Processing state tracking
    # - Retry attempt count
    # - Performance metrics
    # - Cache hit/miss stats
    content_processing: Optional[Dict[str, Any]] = None
    gtd_categorization: Optional[Dict[str, Any]] = None
    prioritization: Optional[Dict[str, Any]] = None
    error_messages: List[str] = None

    def has_errors(self) -> bool:
        return bool(self.error_messages)


class TaskBatchResult(NamedTuple):
    """Results from processing a batch of tasks."""

    # TODO: Add fields for:
    # - Batch processing metrics
    # - Cache utilization stats
    # - Error recovery details
    processed_tasks: List[TaskModel]
    organization: Dict[str, Any]
    errors: List[Dict[str, Any]]


class GTDProcessor(GTDProcessorProtocol):
    """Processor for applying GTD principles to tasks."""

    def __init__(
        self,
        env_config: EnvironmentConfigProtocol,
        gemini_service: GeminiServiceProtocol,
        monitor: MonitoringDashboard = None,
    ):
        """
        Initialize the GTDProcessor with the provided environment configuration and GeminiService.

        Args:
            env_config: An object implementing the EnvironmentConfigProtocol.
            gemini_service: An object implementing the GeminiServiceProtocol.
            monitor: An instance of MonitoringDashboard for monitoring purposes.
        """
        # TODO: Add configuration for:
        # - Batch size limits
        # - Queue priority levels
        # - Cache settings
        # - Retry policies
        # - Performance thresholds
        self.gemini_service = gemini_service
        self.logger: LoggerProtocol = env_config.get_logger()
        self.logger.info("GTDProcessor initialized with GeminiService.")
        self.monitor = monitor or MonitoringDashboard()

    def process_task_content(self, content: str) -> ContentInfo:
        """Process task content using Gemini for improved clarity and formatting."""
        content_info = ContentInfo(original_content=content)

        try:
            # Get content processing from Gemini
            result = self.gemini_service.process_content(content)

            if result:
                content_info.processed_content = result.get("processed_content")
                changes = result.get("changes", {})

                # Transfer changes to our model
                content_info.spelling_fixes = changes.get("spelling_fixes", [])
                content_info.grammar_fixes = changes.get("grammar_fixes", [])
                content_info.formatting_changes = changes.get("formatting_fixes", [])
                content_info.content_changes = changes.get("content_changes", [])

            return content_info

        except Exception as e:
            self.logger.error(f"Error processing content: {e}")
            return content_info

    @BackoffConfig.exponential_backoff(
        max_tries=7
        # max_time=600  # Removed as it's not a valid argument
    )
    async def categorize_gtd_level(
        self, task_content: str, temperature: float = 0.2, max_output_tokens: int = 256
    ) -> Optional[dict]:
        """Categorize a task with consistent retry handling."""
        # Function implementation...

    def prioritize_tasks(self, tasks: List[TaskModel]) -> List[TaskModel]:
        """
        Prioritizes tasks within their GTD levels.

        Args:
            tasks: The list of tasks to prioritize.

        Returns:
            The list of tasks sorted by priority.
        """
        self.logger.info(f"Prioritizing {len(tasks)} tasks...")
        # Sort tasks by priority (higher priority first)
        sorted_tasks = sorted(tasks, key=lambda t: t.priority, reverse=True)
        self.logger.info(
            f"Tasks prioritized. Order: {[task.priority for task in sorted_tasks]}"
        )
        return sorted_tasks

    def organize_by_timeframe(
        self, tasks_by_gtd_level: Dict[str, List[TaskModel]]
    ) -> Dict[str, Dict[str, List[TaskModel]]]:
        """
        Organizes tasks by timeframe within each GTD level.

        Args:
            tasks_by_gtd_level: A dictionary of tasks grouped by GTD level.

        Returns:
            A dictionary of tasks grouped by GTD level and timeframe.
        """
        self.logger.info("Organizing tasks by timeframe...")
        organized_tasks = {}
        for gtd_level, tasks in tasks_by_gtd_level.items():
            self.logger.info(
                f"Organizing tasks for GTD level: {gtd_level} with {len(tasks)} tasks."
            )
            organized_tasks[gtd_level] = {
                "Now": [task for task in tasks if task.priority == 4],
                "Next": [task for task in tasks if task.priority == 3],
                "Soon": [task for task in tasks if task.priority == 2],
                "Later": [task for task in tasks if task.priority == 1],
            }
            self.logger.info(
                f"Tasks for {gtd_level} organized into timeframes: "
                f"Now({len(organized_tasks[gtd_level]['Now'])}), "
                f"Next({len(organized_tasks[gtd_level]['Next'])}), "
                f"Soon({len(organized_tasks[gtd_level]['Soon'])}), "
                f"Later({len(organized_tasks[gtd_level]['Later'])})."
            )
        self.logger.info("Task organization by timeframe complete.")
        return organized_tasks

    def prioritize_task(self, task: TaskModel) -> TaskModel:
        """Determine priority and timeframe for a task using Gemini."""
        try:
            result = self.gemini_service.prioritize_task(task.content, task.gtd_level)

            if result:
                task.priority = result.get("priority", task.priority)
                task.timeframe = result.get("timeframe")

                # Add prioritization info to additional_info
                if task.additional_info is None:
                    task.additional_info = {}

                task.additional_info.update(
                    {
                        "priority_reasoning": result.get("reasoning"),
                        "dependencies": result.get("dependencies", []),
                        "suggested_deadline": result.get("suggested_deadline"),
                        "effort_level": result.get("effort_level"),
                        "impact_assessment": result.get("impact_assessment"),
                    }
                )

            return task

        except Exception as e:
            self.logger.error(f"Error prioritizing task: {str(e)}")
            return task

    def organize_tasks(self, tasks: List[TaskModel]) -> Dict[str, Any]:
        """Organize tasks into optimal groupings and workflow."""
        try:
            # Convert tasks to simple dict format for the prompt
            task_dicts = [
                {
                    "content": task.content,
                    "gtd_level": task.gtd_level,
                    "priority": task.priority,
                }
                for task in tasks
            ]

            result = self.gemini_service.organize_tasks(task_dicts)

            if result:
                return {
                    "task_groups": result.get("task_groups", []),
                    "workflow_order": result.get("workflow_order", []),
                    "parallel_opportunities": result.get("parallel_opportunities", []),
                    "resource_recommendations": result.get(
                        "resource_recommendations", {}
                    ),
                }

            return {}

        except Exception as e:
            self.logger.error(f"Error organizing tasks: {str(e)}")
            return {}

    @BackoffConfig.exponential_backoff()
    async def process_single_task(
        self, task: TaskModel
    ) -> Tuple[TaskModel, TaskProcessingResult]:
        """Process a single task through all LLM stages."""
        # TODO: Add input validation
        # TODO: Implement request deduplication
        # TODO: Add performance tracking
        # TODO: Add failure recovery
        result = TaskProcessingResult(error_messages=[])

        try:
            # Stage 1: Content Processing
            task_id = task.id if hasattr(task, "id") else "unknown"
            self.logger.info(f"Stage 1: Processing content for task {task_id}")
            task.original_content = task.content
            content_result = await self.gemini_service.process_content(task.content)
            if content_result:
                result.content_processing = content_result
                task.content = content_result.get("processed_content", task.content)

            # Stage 2: GTD Categorization
            self.logger.info(f"Stage 2: GTD categorization for task {task.id}")
            gtd_result = await self.gemini_service.categorize_gtd_level(task.content)
            if gtd_result:
                result.gtd_categorization = gtd_result
                task.gtd_level = gtd_result.get("gtd_level")

                # Only proceed to prioritization if we have a GTD level
                if task.gtd_level:
                    # Stage 3: Prioritization
                    self.logger.info(f"Stage 3: Prioritization for task {task.id}")
                    priority_result = await self.gemini_service.prioritize_task(
                        task.content, task.gtd_level
                    )
                    if priority_result:
                        result.prioritization = priority_result
                        task.priority = priority_result.get("priority", task.priority)
                        task.timeframe = priority_result.get("timeframe")

            return task, result

        except Exception as e:
            error_msg = f"Error processing task: {str(e)}"
            self.logger.error(error_msg)
            result.error_messages.append(error_msg)
            return task, result

    async def process_task_async(
        self, task: TaskModel
    ) -> Tuple[TaskModel, TaskProcessingResult]:
        """Async version of process_single_task."""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.process_single_task, task
        )

    def calculate_concurrency(self, total_tasks: int) -> int:
        """Dynamically adjust concurrency based on workload."""
        if total_tasks < 50:
            return 5
        elif total_tasks < 100:
            return 10
        else:
            return min(20, total_tasks // 5)

    async def process_tasks_parallel(
        self,
        tasks: List[TaskModel],
        max_concurrent: Optional[int] = None,  # Now optional
        batch_size: int = 20,
    ) -> TaskBatchResult:
        """Process tasks with dynamic concurrency."""
        if self.monitor:
            self.monitor.metrics["gtd_processor"].active_requests += 1
            self.monitor.log_request("gtd_processor")

        try:
            # Calculate optimal concurrency
            calculated_concurrency = self.calculate_concurrency(len(tasks))
            effective_concurrency = max_concurrent or calculated_concurrency

            self.logger.info(
                f"Processing {len(tasks)} tasks with dynamic concurrency: {effective_concurrency}"
            )

            all_processed_tasks = []
            all_errors = []

            # Process in batches
            for i in range(0, len(tasks), batch_size):
                batch = tasks[i : i + batch_size]
                self.logger.info(
                    f"Processing batch {i//batch_size + 1} of {len(tasks)//batch_size + 1}"
                )

                # Create semaphore to limit concurrent tasks
                semaphore = asyncio.Semaphore(effective_concurrency)

                async def process_with_semaphore(task: TaskModel):
                    async with semaphore:
                        return await self.process_task_async(task)

                # Process batch concurrently
                results = await asyncio.gather(
                    *[process_with_semaphore(task) for task in batch],
                    return_exceptions=True,
                )

                # Process results
                for task, result in zip(batch, results):
                    if isinstance(result, Exception):
                        all_errors.append({"task_id": task.id, "errors": [str(result)]})
                        all_processed_tasks.append(task)
                    else:
                        processed_task, processing_result = result
                        if processing_result.has_errors():
                            all_errors.append(
                                {
                                    "task_id": processed_task.id,
                                    "errors": processing_result.error_messages,
                                }
                            )
                        all_processed_tasks.append(processed_task)

                # Add longer delay between batches
                if i + batch_size < len(tasks):
                    await asyncio.sleep(10)  # 10 second delay between batches

                # Check quota usage
                usage = self.gemini_service.rate_limiter.get_quota_usage()
                if usage["minute"] > 0.8:  # Over 80% of minute quota
                    self.logger.warning("High quota usage, adding extra delay")
                    await asyncio.sleep(30)  # 30 second cooldown

            # Process organization after all tasks complete
            organization = {}
            if all_processed_tasks:
                self.logger.info("Processing batch organization")
                organization = self.organize_tasks(all_processed_tasks)

            return TaskBatchResult(
                processed_tasks=all_processed_tasks,
                organization=organization,
                errors=all_errors,
            )
        finally:
            if self.monitor:
                self.monitor.metrics["gtd_processor"].active_requests -= 1
                self.monitor.update_throughput()

    @BackoffConfig.exponential_backoff()
    def process_tasks_with_retry(
        self,
        tasks: List[TaskModel],
        max_retries: int = 5,
        initial_delay: float = 3.0,
        max_delay: float = 60.0,
        max_concurrent: int = 10,
    ) -> TaskBatchResult:
        """Process tasks with enhanced retry logic and parallel execution."""
        retry_count = 0
        failed_tasks = []

        # Process initial batch in parallel
        result = asyncio.run(
            self.process_tasks_parallel(tasks, max_concurrent=max_concurrent)
        )

        # Identify failed tasks
        for task, error in zip(result.processed_tasks, result.errors):
            if error:
                failed_tasks.append(task)

        # Retry failed tasks with exponential backoff
        while failed_tasks and retry_count < max_retries:
            retry_count += 1
            delay = min(initial_delay * (2 ** (retry_count - 1)), max_delay)

            self.logger.info(
                f"Retry attempt {retry_count}/{max_retries} "
                f"for {len(failed_tasks)} tasks. "
                f"Waiting {delay:.1f}s before retry..."
            )

            time.sleep(delay)

            # Process retry batch in parallel
            retry_result = asyncio.run(
                self.process_tasks_parallel(failed_tasks, max_concurrent=max_concurrent)
            )

            # Update failed tasks list
            failed_tasks = [
                task
                for task, error in zip(
                    retry_result.processed_tasks, retry_result.errors
                )
                if error
            ]

            # Update original result
            result.processed_tasks.extend(
                task
                for task, error in zip(
                    retry_result.processed_tasks, retry_result.errors
                )
                if not error
            )
            result.errors.extend(error for error in retry_result.errors if error)

        if failed_tasks:
            self.logger.warning(
                f"Failed to process {len(failed_tasks)} tasks "
                f"after {max_retries} retry attempts"
            )

        return result
