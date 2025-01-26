"""Crawler workflow service for documentation sites."""

import os
from typing import List, Optional

from loguru import logger

from aerith_ingestion.services.crawler.implementations.batch_processor import (
    DefaultBatchProcessor,
)
from aerith_ingestion.services.crawler.implementations.crawler_service import (
    Crawl4AICrawlerService,
)
from aerith_ingestion.services.crawler.implementations.link_processor import (
    DefaultLinkProcessor,
)
from aerith_ingestion.services.crawler.implementations.markdown_converter import (
    DefaultMarkdownConverter,
)
from aerith_ingestion.services.crawler.implementations.result_saver import (
    MarkdownResultSaver,
)
from aerith_ingestion.services.crawler.interfaces import (
    BatchProcessor,
    CrawlerService,
    LinkProcessor,
    ResultSaver,
)


class CrawlerWorkflow:
    """Workflow for crawling documentation sites."""

    def __init__(
        self,
        crawler_service: CrawlerService,
        link_processor: LinkProcessor,
        result_saver: ResultSaver,
        batch_processor: BatchProcessor,
    ):
        """Initialize workflow with required services."""
        self.crawler_service = crawler_service
        self.link_processor = link_processor
        self.result_saver = result_saver
        self.batch_processor = batch_processor

    async def crawl_site(
        self,
        url: str,
        output: str,
        exclude_patterns: Optional[List[str]] = None,
    ) -> None:
        """Crawl a documentation website and save the results."""
        logger.info(f"Starting documentation crawl for {url}")
        os.makedirs(output, exist_ok=True)

        try:
            # Initial crawl
            initial_result = await self.crawler_service.crawl_url(url)
            if not initial_result.success:
                logger.error(
                    f"Failed to crawl initial URL: {initial_result.error_message}"
                )
                return

            # Save initial page
            self.result_saver.save_result(initial_result, output)

            # Process internal links
            internal_links = self.link_processor.extract_internal_links(
                initial_result, url, exclude_patterns
            )
            if not internal_links:
                logger.info("No internal links found (or all were excluded)")
                return

            logger.info(f"Found {len(internal_links)} internal links to crawl")
            await self.batch_processor.process_urls(internal_links, output)

            # Log final summary
            if isinstance(self.result_saver, MarkdownResultSaver):
                self.result_saver.log_final_summary()

        except Exception as e:
            logger.error(f"Crawl failed: {str(e)}")
            raise


def create_crawler_workflow() -> CrawlerWorkflow:
    """Create a new crawler workflow instance with default implementations."""
    # Create base services
    markdown_converter = DefaultMarkdownConverter()
    crawler_service = Crawl4AICrawlerService()
    result_saver = MarkdownResultSaver(markdown_converter)

    workflow = CrawlerWorkflow(
        crawler_service=crawler_service,
        link_processor=DefaultLinkProcessor(),
        result_saver=result_saver,
        batch_processor=DefaultBatchProcessor(crawler_service, result_saver),
    )

    return workflow
