"""Interfaces for crawler services."""

from abc import ABC, abstractmethod
from typing import List, Optional

from crawl4ai.models import CrawlResult


class CrawlerService(ABC):
    """Interface for web crawling service."""

    @abstractmethod
    async def crawl_url(self, url: str) -> CrawlResult:
        """Crawl a URL and return the result."""
        pass


class LinkProcessor(ABC):
    """Interface for processing links from crawl results."""

    @abstractmethod
    def extract_internal_links(
        self, result: CrawlResult, base_url: str, exclude_patterns: Optional[List[str]] = None
    ) -> List[str]:
        """Extract internal links from crawl result."""
        pass


class MarkdownConverter(ABC):
    """Interface for converting crawl results to markdown."""

    @abstractmethod
    def convert(self, result: CrawlResult) -> str:
        """Convert crawl result to markdown."""
        pass


class ResultSaver(ABC):
    """Interface for saving crawl results."""

    @abstractmethod
    def save_result(self, result: CrawlResult, output_dir: str) -> None:
        """Save crawl result."""
        pass


class BatchProcessor(ABC):
    """Interface for processing batches of URLs."""

    @abstractmethod
    async def process_urls(self, urls: List[str], output_dir: str) -> None:
        """Process a batch of URLs."""
        pass
