"""
Enrichment configuration settings.

This module provides configuration for task enrichment:
1. Task analysis settings (complexity thresholds, categories)
2. Vector search settings (similarity thresholds, index settings)
3. Batch processing settings
"""

from dataclasses import dataclass, field
from typing import Dict, List, Literal


@dataclass
class TaskAnalysisConfig:
    """Configuration for task analysis.

    Attributes:
        complexity_levels: Valid complexity levels for task analysis
        categories: Valid task categories and their descriptions
        min_theme_count: Minimum number of themes to extract per task
        max_theme_count: Maximum number of themes to extract per task
    """

    complexity_levels: List[str] = field(
        default_factory=lambda: ["Low", "Medium", "High"]
    )
    categories: Dict[str, str] = field(
        default_factory=lambda: {
            "Development": "Code implementation and technical tasks",
            "Research": "Investigation and learning tasks",
            "Planning": "Project planning and organization",
            "Documentation": "Writing and maintaining docs",
            "Review": "Code review and feedback",
            "Bug": "Bug fixes and issues",
            "Feature": "New feature development",
            "Maintenance": "System maintenance and updates",
        }
    )
    min_theme_count: int = 2
    max_theme_count: int = 5


@dataclass
class VectorSearchConfig:
    """Configuration for vector similarity search.

    Attributes:
        similarity_threshold: Minimum similarity score (0-1) for related tasks
        top_k: Number of similar tasks to return
        index_refresh_interval: How often to refresh vector index (in seconds)
        cache_size: Maximum number of vectors to cache in memory
    """

    similarity_threshold: float = 0.7
    top_k: Literal[3, 5, 10] = 5
    index_refresh_interval: int = 3600  # 1 hour
    cache_size: int = 10000


@dataclass
class BatchProcessingConfig:
    """Configuration for batch processing.

    Attributes:
        batch_size: Number of tasks to process in parallel
        max_retries: Maximum number of retries for failed enrichments
        retry_delay: Delay between retries in seconds
        timeout: Maximum time to wait for batch completion in seconds
    """

    batch_size: int = 100
    max_retries: int = 3
    retry_delay: int = 5
    timeout: int = 300  # 5 minutes


@dataclass
class EnrichmentConfig:
    """Task enrichment configuration settings."""

    analysis: TaskAnalysisConfig = field(default_factory=TaskAnalysisConfig)
    vector_search: VectorSearchConfig = field(default_factory=VectorSearchConfig)
    batch_processing: BatchProcessingConfig = field(
        default_factory=BatchProcessingConfig
    )
