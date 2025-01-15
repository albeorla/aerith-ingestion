"""URL normalization implementation."""

from urllib.parse import urljoin

from aerith_ingestion.services.crawler.interfaces import URLNormalizer


class DefaultURLNormalizer(URLNormalizer):
    """Default implementation of URL normalization."""

    def normalize(self, url: str, base_url: str) -> str:
        """Normalize a URL to ensure it's absolute and properly formatted."""
        # Handle anchor links
        if url.startswith("#"):
            return base_url

        # Handle relative URLs
        if not url.startswith(("http://", "https://")):
            return urljoin(base_url, url)

        return url
