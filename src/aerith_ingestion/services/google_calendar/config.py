"""Configuration for Google Calendar service."""

from typing import Optional

from loguru import logger
from pydantic import HttpUrl
from pydantic_settings import BaseSettings


class GoogleCalendarSettings(BaseSettings):
    """
    Configuration settings for Google Calendar integration, including
    OAuth details and webhook parameters.
    """

    # OAuth2 credentials
    client_id: str
    client_secret: str
    refresh_token: Optional[str] = None
    scopes: list[str] = ["https://www.googleapis.com/auth/calendar"]
    token_uri: str = "https://oauth2.googleapis.com/token"

    # Webhook configuration
    webhook_base_url: HttpUrl
    webhook_path: str = "/webhook/google-calendar"
    webhook_token: Optional[str] = None

    # Channel configuration
    channel_expiration_days: int = 7  # Default to 7 days

    @property
    def webhook_url(self) -> str:
        """
        Get the full webhook URL by combining webhook_base_url and webhook_path.
        """
        base_url = str(self.webhook_base_url).rstrip("/")
        url = base_url + self.webhook_path
        logger.debug(f"Constructed webhook URL: {url}")
        return url

    class Config:
        """
        Pydantic configuration, setting environment variable prefix to 'GOOGLE_CALENDAR_'.
        """
        env_prefix = "GOOGLE_CALENDAR_"

    def __init__(self, **kwargs):
        """
        Initialize settings and log configuration.
        """
        super().__init__(**kwargs)
        logger.info("Loaded Google Calendar settings")
        logger.debug(f"Client ID: {self.client_id[:6]}... (masked)")
        logger.debug(f"Webhook base URL: {self.webhook_base_url}")
        logger.debug(f"Webhook path: {self.webhook_path}")
        logger.debug(f"Channel expiration: {self.channel_expiration_days} days")
