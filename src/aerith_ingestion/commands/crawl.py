"""Crawl command for downloading and processing documentation sites."""

import asyncio
from urllib.parse import urlparse

import click
from loguru import logger

from aerith_ingestion.cli import pass_context
from aerith_ingestion.services.crawler.workflow import create_crawler_workflow


@click.command()
@click.argument("url")
@click.option(
    "--output-dir",
    default=None,
    help="Output directory (defaults to data/crawler/<domain>)",
)
@pass_context
def crawl(ctx, url: str, output_dir: str | None) -> None:
    """Crawl a documentation website and save as markdown.

    URL: The website URL to crawl
    """
    try:
        # Use domain name for output directory if not specified
        if not output_dir:
            domain = urlparse(url).netloc.replace(":", "_")
            output_dir = f"data/crawler/{domain}"

        # Run the crawler
        crawler = create_crawler_workflow()
        logger.info(f"Starting crawl of {url}")
        logger.info(f"Output directory: {output_dir}")

        asyncio.run(crawler.crawl_site(url=url, output=output_dir))

    except KeyboardInterrupt:
        logger.warning("Crawl interrupted by user")
        raise click.Abort()
    except Exception as e:
        logger.error(f"Crawl failed: {str(e)}")
        raise click.ClickException(str(e))
