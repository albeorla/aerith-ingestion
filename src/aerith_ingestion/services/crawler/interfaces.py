"""Interfaces for crawler components."""

from abc import ABC, abstractmethod
from typing import List, Optional, Protocol

from crawl4ai.models import CrawlResult


class URLNormalizer(Protocol):
    """Protocol for URL normalization."""

    def normalize(self, url: str, base_url: str) -> str:
        """Normalize a URL relative to a base URL."""
        ...


class NavigationAnalyzer(Protocol):
    """Protocol for analyzing navigation structure."""

    async def extract_exclude_patterns(self, result: CrawlResult) -> List[str]:
        """Extract patterns of URLs to exclude from crawling."""
        ...


class MarkdownConverter(Protocol):
    """Protocol for converting crawl results to markdown."""

    def convert(self, result: CrawlResult) -> str:
        """Convert a crawl result to markdown format."""
        ...


class CrawlerService(ABC):
    """Abstract base class for crawler service."""

    @abstractmethod
    async def crawl_url(self, url: str) -> CrawlResult:
        """Crawl a single URL."""
        pass

    @abstractmethod
    async def crawl_urls(self, urls: List[str]) -> List[CrawlResult]:
        """Crawl multiple URLs in parallel."""
        pass


class LinkProcessor(Protocol):
    """Protocol for processing and filtering links."""

    def extract_internal_links(
        self,
        result: CrawlResult,
        base_url: str,
        exclude_patterns: Optional[List[str]] = None,
    ) -> List[str]:
        """Extract and filter internal links from crawl result."""
        ...


class ResultSaver(Protocol):
    """Protocol for saving crawl results."""

    def save_result(self, result: CrawlResult, output_dir: str) -> None:
        """Save a crawl result to the output directory."""
        ...


class BatchProcessor(Protocol):
    """Protocol for processing URLs in batches."""

    async def process_urls(
        self,
        urls: List[str],
        output_dir: str,
        batch_size: int = 10,
    ) -> None:
        """Process a list of URLs in batches."""
        ...
