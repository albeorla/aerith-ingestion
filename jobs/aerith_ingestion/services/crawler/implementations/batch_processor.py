"""Batch processing implementation."""

from typing import List

from loguru import logger

from aerith_ingestion.services.crawler.interfaces import (
    BatchProcessor,
    CrawlerService,
    ResultSaver,
)


class DefaultBatchProcessor(BatchProcessor):
    """Default implementation of batch processing."""

    def __init__(self, crawler_service: CrawlerService, result_saver: ResultSaver):
        """Initialize with required services."""
        self.crawler_service = crawler_service
        self.result_saver = result_saver

    async def process_urls(
        self,
        urls: List[str],
        output_dir: str,
        batch_size: int = 10,
    ) -> None:
        """Process URLs in batches."""
        for i in range(0, len(urls), batch_size):
            batch = urls[i : i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(urls) - 1) // batch_size + 1

            logger.debug(f"Processing batch {batch_num}/{total_batches}")
            results = await self.crawler_service.crawl_urls(batch)

            for result in results:
                if result.success:
                    self.result_saver.save_result(result, output_dir)
