"""Link processing implementation."""

from typing import List, Optional

from crawl4ai.models import CrawlResult
from loguru import logger

from aerith_ingestion.services.crawler.interfaces import LinkProcessor, URLNormalizer


class DefaultLinkProcessor(LinkProcessor):
    """Default implementation of link processing."""

    def __init__(self, url_normalizer: URLNormalizer):
        """Initialize with URL normalizer."""
        self.url_normalizer = url_normalizer

    def extract_internal_links(
        self,
        result: CrawlResult,
        base_url: str,
        exclude_patterns: Optional[List[str]] = None,
    ) -> List[str]:
        """Extract and filter internal links from crawl result."""
        internal_links = []

        if result.links and "internal" in result.links:
            for link in result.links["internal"]:
                url_to_check = link["href"] if isinstance(link, dict) else link
                normalized_url = self.url_normalizer.normalize(url_to_check, base_url)

                if exclude_patterns and any(
                    pattern in normalized_url for pattern in exclude_patterns
                ):
                    logger.debug(f"Skipping excluded URL: {normalized_url}")
                    continue

                internal_links.append(normalized_url)

        return internal_links
