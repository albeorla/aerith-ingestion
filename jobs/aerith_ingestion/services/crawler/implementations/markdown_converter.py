"""Markdown conversion implementation."""

import mdformat
from crawl4ai.models import CrawlResult
from loguru import logger

from aerith_ingestion.services.crawler.interfaces import MarkdownConverter


class DefaultMarkdownConverter(MarkdownConverter):
    """Default implementation of markdown conversion."""

    MARKDOWN_OPTIONS = {
        "body_width": 0,
        "mark_code": True,
        "single_line_break": True,
        "protect_links": True,
        "ignore_images": True,
        "ignore_links": False,
        "ignore_emphasis": False,
        "escape_snob": False,
        "escape_html": True,
        "handle_code_in_pre": True,
    }

    def convert(self, result: CrawlResult) -> str:
        """Convert crawl result to markdown format."""
        if not result.markdown:
            return ""

        try:
            return mdformat.text(result.markdown, options=self.MARKDOWN_OPTIONS)
        except Exception as e:
            logger.error(f"Failed to format markdown: {str(e)}")
            return result.markdown
