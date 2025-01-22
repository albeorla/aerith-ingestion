"""Command for crawling documentation sites."""

import asyncio
import json
import os
from typing import List, Optional

import click
from loguru import logger

from aerith_ingestion.config.logging import LoggingConfig, setup_logging
from aerith_ingestion.services.crawler.workflow import create_crawler_workflow


def setup_crawler_logging(log_path: str) -> None:
    """Set up crawler-specific logging."""
    # Format for crawler logs
    crawler_format = (
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}:{function}</cyan> | "
        "{message}"
    )

    # Add crawler log handler
    crawler_log_file = os.path.join(log_path, "crawler.log")
    logger.add(
        crawler_log_file,
        format=crawler_format,
        level="TRACE",  # Capture all crawler logs
        enqueue=True,
        mode="w",
        filter=lambda record: record["name"].startswith(
            "aerith_ingestion.services.crawler"
        ),
    )


async def crawl_site(
    url: str, output: str, exclude_patterns: Optional[List[str]] = None
) -> None:
    """Crawl a single site."""
    workflow = create_crawler_workflow()
    await workflow.crawl_site(url, output, exclude_patterns)


async def crawl_all_sites() -> None:
    """Crawl all sites from configuration."""
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "sites.json")

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file not found at {config_path}")
        return
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in configuration file at {config_path}")
        return

    if not config.get("sites"):
        logger.error("No sites configured in configuration file")
        return

    # Create tasks for all sites
    tasks = []
    for site in config["sites"]:
        url = site.get("url")
        output_dir = site.get("output_dir")
        exclude_patterns = site.get("exclude_patterns")

        if not url or not output_dir:
            logger.warning(f"Skipping invalid site configuration: {site}")
            continue

        tasks.append(crawl_site(url, output_dir, exclude_patterns))

    # Run all crawls concurrently
    logger.info(f"Starting concurrent crawl of {len(tasks)} sites")
    await asyncio.gather(*tasks)
    logger.info("All crawls completed")


@click.command()
@click.argument("url", required=False)
@click.argument("output", required=False)
@click.option("--exclude", multiple=True, help="Patterns to exclude from crawling")
def crawl(url: Optional[str], output: Optional[str], exclude: Optional[tuple]) -> None:
    """Crawl documentation sites."""

    config = LoggingConfig()
    setup_logging(config)
    setup_crawler_logging(config.log_path)

    if url and output:
        asyncio.run(crawl_site(url, output, list(exclude) if exclude else None))
    else:
        asyncio.run(crawl_all_sites())
