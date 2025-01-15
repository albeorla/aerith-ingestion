"""Navigation analysis implementation."""

import json
from typing import List, Optional
from urllib.parse import urlparse
import re

from crawl4ai.models import CrawlResult
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from loguru import logger

from aerith_ingestion.services.crawler.implementations.url_normalizer import (
    DefaultURLNormalizer,
)
from aerith_ingestion.services.crawler.interfaces import NavigationAnalyzer


class LLMNavigationAnalyzer(NavigationAnalyzer):
    """Navigation analyzer that uses LLM for pattern extraction."""

    DEFAULT_PATTERNS = ["community/", "news/"]

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """Initialize with optional LLM instance."""
        if llm is not None:
            try:
                # Test the LLM with a simple prompt
                test_prompt = ChatPromptTemplate.from_messages(
                    [
                        ("system", "Return the text 'ok' if you can read this."),
                        ("user", "Test connection"),
                    ]
                )
                response = llm.invoke(test_prompt.format_messages())
                if not response or not response.content:
                    logger.warning(
                        "LLM returned empty response during initialization test"
                    )
                    llm = None
            except Exception as e:
                logger.warning(f"LLM failed initialization test: {str(e)}")
                llm = None
        else:
            logger.info("No LLM provided, will use default patterns")

        self.llm = llm
        self.url_normalizer = DefaultURLNormalizer()

    async def extract_exclude_patterns(self, result: CrawlResult) -> List[str]:
        """Extract navigation paths to determine exclude patterns."""
        if not result.success:
            logger.warning("Crawl result was not successful")
            return []

        # If LLM not available, use basic exclusions
        if not self.llm:
            logger.info("Using basic exclusion patterns (LLM not available)")
            return self.DEFAULT_PATTERNS

        try:
            # Use Crawl4AI's built-in link extraction
            nav_links = {}
            if result.links:
                logger.debug(f"Raw links from Crawl4AI: {result.links}")

                # Get the initial URL path to skip it in navigation
                initial_path = urlparse(result.url).path.strip("/")
                if initial_path.endswith("/"):
                    initial_path = initial_path[:-1]
                logger.debug(f"Initial URL path to skip: {initial_path}")

                # Process navigation links from result.links
                for link_type, links in result.links.items():
                    logger.debug(f"Processing link type: {link_type}")
                    for link in links:
                        logger.debug(f"Processing link: {link}")
                        if isinstance(link, dict) and "href" in link:
                            href = link["href"]
                            text = link.get("text", "")

                            href = self.url_normalizer.normalize(href, result.url)
                            parsed = urlparse(href)
                            path = parsed.path.lstrip("/")

                            # Skip empty paths, fragments, and initial path
                            if not path or parsed.fragment:
                                logger.debug(f"Skipping path with fragment or empty path: {href}")
                                continue

                            # Normalize path by removing .html extension
                            if path.endswith(".html"):
                                path = path[:-5]  # Remove .html extension
                            path_normalized = path.rstrip("/")
                            if path_normalized == initial_path:
                                logger.debug(f"Skipping initial path: {path}")
                                continue

                            # Add trailing slash for storage
                            path = path_normalized + "/"
                            if path and path not in nav_links:
                                nav_links[path] = text
                                logger.debug(f"Added nav link: {path} -> {text}")

            # Log navigation data for debugging
            logger.debug(f"Final navigation links: {nav_links}")

            # Create prompt messages
            messages = [
                {
                    "role": "system",
                    "content": """You are a navigation analyzer for a documentation website crawler.
Your task is to identify which sections of the documentation should be excluded from crawling.

Common sections to exclude:
- Community pages (e.g., 'community/')
- News/blog sections (e.g., 'news/', 'blog/')
- Support/help pages
- API reference pages

Return ONLY the paths that should be excluded, formatted as a JSON array of strings.
Each path should:
- NOT include .html extensions
- End with a trailing slash
- Be relative (no leading slash)

Example good response: ["community/", "news/", "blog/"]
Example bad response: ["/community", "news.html", "'blog/'"]"""
                },
                {
                    "role": "user",
                    "content": f"Here are the navigation links found on the page: {nav_links}. Which paths should be excluded from crawling?"
                }
            ]

            # Get LLM response
            response = await self.llm.ainvoke(messages)
            content = response.content.strip()

            try:
                # Clean up the response
                content = content.strip()
                
                # Handle non-array responses
                if not content.startswith("["):
                    # Remove any quotes and normalize path
                    cleaned_path = content.strip().strip("'").strip('"').rstrip("/")
                    # Create a proper JSON array with the path
                    content = json.dumps([f"{cleaned_path}/"])
                else:
                    # Clean up array format
                    content = content.replace("'", '"')  # Replace single quotes with double quotes
                    # Parse and reformat to ensure proper JSON
                    paths = json.loads(content)
                    # Normalize each path
                    paths = [p.strip().strip("'").strip('"').rstrip("/") + "/" for p in paths]
                    # Convert back to JSON
                    content = json.dumps(paths)

                logger.debug(f"Cleaned LLM response: {content}")
                exclude_patterns = json.loads(content)
                logger.debug(f"Parsed exclude patterns: {exclude_patterns}")
                return exclude_patterns

            except json.JSONDecodeError as e:
                logger.error(f"Error in navigation extraction: {content!r}")
                logger.debug(f"JSON decode error: {str(e)}")
                return self.DEFAULT_PATTERNS

        except Exception as e:
            logger.error(f"Error in navigation extraction: {str(e)}")
            logger.debug(f"Context: {locals()}")  # Log local variables for debugging
            return self.DEFAULT_PATTERNS
