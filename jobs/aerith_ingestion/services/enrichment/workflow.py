"""
Task enrichment workflow that coordinates the process of analyzing and enriching tasks.

This module handles the workflow of:
1. Analyzing tasks using LLM
2. Extracting metadata
3. Generating vector embeddings
4. Creating enriched task objects
"""

from typing import List, Optional

from aerith_ingestion.domain.task import (
    EnrichedTask,
    Task,
    TaskAnalysisResult,
    VectorMetadata,
)
from aerith_ingestion.services.enrichment.analyzer import LLMTaskAnalyzer
from aerith_ingestion.services.enrichment.store import VectorStore


class TaskEnrichmentWorkflow:
    """Coordinates the process of enriching tasks with analysis and vector embeddings."""

    def __init__(
        self,
        task_analyzer: LLMTaskAnalyzer,
        vector_store: VectorStore,
    ):
        self.task_analyzer = task_analyzer
        self.vector_store = vector_store

    def enrich_task(self, task: Task) -> EnrichedTask:
        """Enrich a single task with analysis and vector metadata."""
        # Analyze task using LLM
        analysis = self.task_analyzer.analyze(task)

        # Generate vector embedding
        vector_metadata = self._generate_vector_metadata(task, analysis)

        # Create enriched task
        return EnrichedTask(
            **task.__dict__, analysis=analysis, vector_metadata=vector_metadata
        )

    def enrich_all(self, tasks: List[Task]) -> List[EnrichedTask]:
        """Enrich multiple tasks in parallel."""
        return [self.enrich_task(task) for task in tasks]

    def _generate_vector_metadata(
        self, task: Task, analysis: TaskAnalysisResult
    ) -> Optional[VectorMetadata]:
        """Generate vector metadata for a task."""
        # Combine task content with relevant metadata
        content_to_vectorize = f"{task.content}\n{task.description or ''}"
        if analysis:
            content_to_vectorize += f"\nCategory: {analysis.category}"
            content_to_vectorize += f"\nThemes: {', '.join(analysis.themes)}"

        # Generate vector embedding
        vector = self.vector_store.generate_embedding(content_to_vectorize)

        return VectorMetadata(
            task_id=task.id, vector=vector, content=content_to_vectorize
        )


def create_enrichment_workflow(
    task_analyzer: LLMTaskAnalyzer,
    vector_store: VectorStore,
) -> TaskEnrichmentWorkflow:
    """Create a new task enrichment workflow."""
    return TaskEnrichmentWorkflow(
        task_analyzer=task_analyzer,
        vector_store=vector_store,
    )
