"""Crawler service implementation."""

from typing import List, Tuple

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    DefaultMarkdownGenerator,
)
from crawl4ai.models import CrawlResult

from aerith_ingestion.services.crawler.interfaces import CrawlerService


class Crawl4AICrawlerService(CrawlerService):
    """Crawler service implementation using Crawl4AI."""

    def __init__(self):
        """Initialize crawler with default configurations."""
        self.browser_config, self.run_config = self._create_default_configs()

    async def crawl_url(self, url: str) -> CrawlResult:
        """Crawl a single URL."""
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            return await crawler.arun(url, config=self.run_config)

    async def crawl_urls(self, urls: List[str]) -> List[CrawlResult]:
        """Crawl multiple URLs in parallel."""
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            return await crawler.arun_many(urls, config=self.run_config)

    def _create_default_configs(self) -> Tuple[BrowserConfig, CrawlerRunConfig]:
        """Create default browser and run configurations."""
        browser_config = BrowserConfig(
            headless=True,  # Run without GUI
            ignore_https_errors=True,  # Ignore SSL issues
            text_mode=True,  # Faster loading by disabling images
            light_mode=True,  # Better performance
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            verbose=True,  # Enable verbose logging
            accept_downloads=False,  # Disable downloads
            java_script_enabled=True,  # Enable JavaScript
        )

        run_config = CrawlerRunConfig(
            # Content Processing Parameters
            word_count_threshold=200,  # Minimum word count threshold
            only_text=True,  # Extract text-only content
            remove_forms=True,  # Remove form elements
            parser_type="lxml",  # Use lxml parser
            # Content Filtering
            excluded_selector="a[href*='#']",  # Exclude links with fragments
            # Caching Parameters
            cache_mode=CacheMode.BYPASS,  # Don't cache in memory
            # Navigation Parameters
            wait_until="domcontentloaded",  # Wait for DOM content loaded
            page_timeout=60000,  # 60 second timeout
            semaphore_count=5,  # Limit concurrent requests
            mean_delay=0.1,  # Base delay between requests
            max_range=0.3,  # Max additional random delay
            # Page Interaction
            ignore_body_visibility=True,  # Ignore body visibility checks
            scan_full_page=True,  # Scan full page content
            scroll_delay=0.2,  # Delay between scroll steps
            # Media Handling
            screenshot=False,  # Don't take screenshots
            pdf=False,  # Don't generate PDFs
            exclude_external_images=True,  # Exclude external images
            # Link Handling
            exclude_external_links=True,  # Exclude external links
            exclude_social_media_links=True,  # Exclude social media links
            # Markdown Generation
            markdown_generator=DefaultMarkdownGenerator(),
        )
        return browser_config, run_config
