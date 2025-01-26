"""
LLM-based task analysis service.

This module provides functionality for analyzing tasks using LLM.
"""

import json
from typing import Any, Dict

from aerith_ingestion.config.api import OpenAIConfig
from aerith_ingestion.domain.task import Task, TaskAnalysisResult
from aerith_ingestion.services.enrichment.prompts import (
    TASK_ANALYSIS_PROMPT,
    TASK_RECOMMENDATIONS_PROMPT,
)


def create_task_analyzer(config: OpenAIConfig) -> "LLMTaskAnalyzer":
    """Create a new task analyzer instance."""
    return LLMTaskAnalyzer(config)


class LLMTaskAnalyzer:
    """Service for analyzing tasks using LLM."""

    def __init__(self, config: OpenAIConfig):
        """Initialize the task analyzer."""
        self.config = config

    def analyze_task(self, task: Task) -> TaskAnalysisResult:
        """Analyze a task using LLM to extract insights and recommendations."""
        # Get task analysis
        analysis_prompt = TASK_ANALYSIS_PROMPT.format(
            task_content=task.content,
            task_description=task.description,
        )
        analysis_result = self._call_llm(analysis_prompt)

        # Get recommendations
        recommendations_prompt = TASK_RECOMMENDATIONS_PROMPT.format(
            task_content=task.content,
            task_analysis=json.dumps(analysis_result),
        )
        recommendations_result = self._call_llm(recommendations_prompt)

        return TaskAnalysisResult(
            category=analysis_result.get("category", ""),
            complexity=analysis_result.get("complexity", ""),
            themes=analysis_result.get("themes", []),
            dependencies=analysis_result.get("dependencies", []),
            next_actions=recommendations_result.get("next_actions", []),
        )

    def _call_llm(self, prompt: str) -> Dict[str, Any]:
        """Call LLM with prompt and return parsed JSON response."""
        # TODO: Implement OpenAI API call
        return {}
