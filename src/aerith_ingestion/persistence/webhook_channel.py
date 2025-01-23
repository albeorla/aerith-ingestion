"""Repository for managing webhook channel persistence."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from loguru import logger

from aerith_ingestion.persistence.database import Database


@dataclass
class WebhookChannel:
    """Represents a webhook channel."""

    channel_id: str
    resource_id: str
    calendar_id: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True


class SQLiteWebhookChannelRepository:
    """SQLite repository for webhook channels."""

    def __init__(self, db: Database):
        """Initialize the repository.

        Args:
            db: Database instance
        """
        self.db = db
        self._ensure_table()

    def _ensure_table(self):
        """Ensure the webhook_channels table exists."""
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS webhook_channels (
                channel_id TEXT PRIMARY KEY,
                resource_id TEXT NOT NULL,
                calendar_id TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                expires_at TIMESTAMP,
                is_active BOOLEAN NOT NULL DEFAULT 1
            )
        """
        )

    def save(self, channel: WebhookChannel) -> None:
        """Save a webhook channel.

        Args:
            channel: Channel to save
        """
        logger.debug(f"Saving webhook channel {channel.channel_id}")
        self.db.execute(
            """
            INSERT OR REPLACE INTO webhook_channels (
                channel_id, resource_id, calendar_id, created_at, expires_at, is_active
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                channel.channel_id,
                channel.resource_id,
                channel.calendar_id,
                channel.created_at,
                channel.expires_at,
                channel.is_active,
            ),
        )

    def get_active_channel(self, calendar_id: str) -> Optional[WebhookChannel]:
        """Get the active channel for a calendar.

        Args:
            calendar_id: Calendar ID to get channel for

        Returns:
            Active channel if exists, None otherwise
        """
        row = self.db.fetch_one(
            """
            SELECT channel_id, resource_id, calendar_id, created_at, expires_at, is_active
            FROM webhook_channels
            WHERE calendar_id = ? AND is_active = 1
            """,
            (calendar_id,),
        )

        if row:
            return WebhookChannel(
                channel_id=row[0],
                resource_id=row[1],
                calendar_id=row[2],
                created_at=datetime.fromisoformat(row[3]),
                expires_at=datetime.fromisoformat(row[4]) if row[4] else None,
                is_active=bool(row[5]),
            )
        return None

    def deactivate(self, channel_id: str) -> None:
        """Mark a channel as inactive.

        Args:
            channel_id: ID of channel to deactivate
        """
        logger.debug(f"Deactivating webhook channel {channel_id}")
        self.db.execute(
            "UPDATE webhook_channels SET is_active = 0 WHERE channel_id = ?",
            (channel_id,),
        )

    def get_all_active(self) -> List[WebhookChannel]:
        """Get all active channels.

        Returns:
            List of active channels
        """
        rows = self.db.fetch_all(
            """
            SELECT channel_id, resource_id, calendar_id, created_at, expires_at, is_active
            FROM webhook_channels
            WHERE is_active = 1
            """
        )

        return [
            WebhookChannel(
                channel_id=row[0],
                resource_id=row[1],
                calendar_id=row[2],
                created_at=datetime.fromisoformat(row[3]),
                expires_at=datetime.fromisoformat(row[4]) if row[4] else None,
                is_active=bool(row[5]),
            )
            for row in rows
        ]
