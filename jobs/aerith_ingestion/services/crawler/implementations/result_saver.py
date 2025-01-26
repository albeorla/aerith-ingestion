"""Result saving implementation."""

import os
from urllib.parse import urlparse

from crawl4ai.models import CrawlResult
from loguru import logger

from aerith_ingestion.services.crawler.interfaces import MarkdownConverter, ResultSaver


class MarkdownResultSaver(ResultSaver):
    """Implementation for saving results as markdown files."""

    def __init__(self, markdown_converter: MarkdownConverter):
        """Initialize with markdown converter."""
        self.markdown_converter = markdown_converter
        self.processed_files = []  # Track all processed files

    def save_result(self, result: CrawlResult, output_dir: str) -> None:
        """Save crawl result as markdown file."""
        if not result.success or not result.url:
            return

        try:
            parsed = urlparse(result.url)
            path_parts = parsed.path.strip("/").split("/")

            # Create filename
            if not path_parts or path_parts[-1] == "":
                filename = "index.md"
            else:
                filename = path_parts[-1]
                # Remove .html extension if present
                if filename.endswith(".html"):
                    filename = filename[:-5]
                # Add .md extension if needed
                if not filename.endswith(".md"):
                    filename = f"{filename}.md"

            # Create directory structure
            if len(path_parts) > 1:
                dir_path = os.path.join(output_dir, *path_parts[:-1])
                os.makedirs(dir_path, exist_ok=True)
            else:
                dir_path = output_dir

            # Save markdown
            file_path = os.path.join(dir_path, filename)
            markdown = self.markdown_converter.convert(result)

            # Truncate content until first main heading
            lines = markdown.splitlines()
            original_line_count = len(lines)
            logger.trace(f"First 10 lines of content for {file_path}:")
            for i, line in enumerate(lines[:10]):
                logger.trace(f"Line {i}: {repr(line)}")

            # Find first main heading (h1)
            start_index = 0
            found_heading = None
            for i, line in enumerate(lines):
                line = line.strip()
                # Look for lines that start with exactly one # followed by a space
                if line and line.startswith("# ") and not line.startswith("## "):
                    logger.trace(f"Found main heading at line {i}: {repr(line)}")
                    start_index = i
                    found_heading = line
                    break

            # If no main heading found, look for the first heading of any level
            if start_index == 0:
                for i, line in enumerate(lines):
                    line = line.strip()
                    if line and line.startswith("#"):
                        logger.trace(f"Found first heading at line {i}: {repr(line)}")
                        start_index = i
                        found_heading = line
                        break

            # Keep content from the heading onwards
            if start_index > 0:
                markdown = "\n".join(lines[start_index:])
                final_line_count = len(lines) - start_index
                logger.trace(f"Truncated content to start from line {start_index}")
            else:
                final_line_count = original_line_count
                logger.trace(f"No heading found in {file_path}")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(markdown)

            # Track file processing details
            file_info = {
                "filename": filename,
                "heading": found_heading,
                "lines_removed": start_index,
                "original_lines": original_line_count,
                "final_lines": final_line_count,
                "url": result.url,
            }
            self.processed_files.append(file_info)

            # Log trace details for this file
            summary = []
            summary.append(f"File: {filename}")
            if found_heading:
                summary.append(f"Found heading: {found_heading}")
                summary.append(f"Removed {start_index} lines before heading")
            else:
                summary.append("No heading found - kept original content")
            summary.append(f"Original lines: {original_line_count}")
            summary.append(f"Final lines: {final_line_count}")
            logger.trace(" | ".join(summary))

            logger.trace(f"Saved markdown to {file_path}")

        except Exception as e:
            logger.error(f"Failed to save markdown for {result.url}: {str(e)}")

    def log_final_summary(self) -> None:
        """Log a summary of all processed files."""
        total_files = len(self.processed_files)
        files_with_headings = sum(1 for f in self.processed_files if f["heading"])
        total_lines_removed = sum(f["lines_removed"] for f in self.processed_files)

        logger.info("\n=== Markdown Processing Summary ===")
        logger.info(f"Total files processed: {total_files}")
        logger.info(f"Files with headings: {files_with_headings}")
        logger.info(f"Files without headings: {total_files - files_with_headings}")
        logger.info(f"Total lines removed: {total_lines_removed}")
        logger.info("Files processed:")

        # Sort by filename for consistent output
        sorted_files = sorted(self.processed_files, key=lambda x: x["filename"])
        for file_info in sorted_files:
            status = "✓" if file_info["heading"] else "✗"
            heading = file_info["heading"] or "No heading"
            logger.info(f"{status} {file_info['filename']}: {heading}")

        logger.info("===============================\n")
