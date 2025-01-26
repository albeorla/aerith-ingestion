"""Link processing implementation."""

from typing import List, Optional

from crawl4ai.models import CrawlResult
from loguru import logger

from aerith_ingestion.services.crawler.interfaces import LinkProcessor


class DefaultLinkProcessor(LinkProcessor):
    """Default implementation of link processing."""

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
                url = link["href"] if isinstance(link, dict) else link

                if exclude_patterns and any(
                    pattern in url for pattern in exclude_patterns
                ):
                    logger.debug(f"Skipping excluded URL: {url}")
                    continue

                internal_links.append(url)

        return internal_links
