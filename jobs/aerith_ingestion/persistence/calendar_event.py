"""Repository for managing calendar event persistence."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from loguru import logger

from aerith_ingestion.persistence.database import Database


@dataclass
class CalendarEvent:
    """Represents a calendar event."""

    event_id: str
    calendar_id: str
    summary: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    location: Optional[str]
    created_at: datetime
    updated_at: datetime
    status: str  # confirmed, tentative, cancelled
    is_recurring: bool
    recurrence: Optional[str]  # RRULE string if recurring
    attendees: Optional[str]  # JSON string of attendees
    conference_data: Optional[str]  # JSON string of conference details

    @classmethod
    def from_google_event(cls, calendar_id: str, event: dict) -> "CalendarEvent":
        """Create a CalendarEvent from a Google Calendar event.

        Args:
            calendar_id: ID of the calendar containing the event
            event: Google Calendar event data

        Returns:
            CalendarEvent instance
        """
        import json

        from dateutil.parser import parse

        # Parse start and end times
        start = event.get("start", {})
        end = event.get("end", {})

        # Handle both date and dateTime formats
        start_time = start.get("dateTime") or start.get("date")
        end_time = end.get("dateTime") or end.get("date")

        # Convert to datetime objects
        start_time = parse(start_time)
        end_time = parse(end_time)

        # Parse timestamps
        created_at = parse(event["created"])
        updated_at = parse(event["updated"])

        # Handle attendees
        attendees = event.get("attendees")
        if attendees:
            attendees = json.dumps(attendees)

        # Handle conference data
        conference_data = event.get("conferenceData")
        if conference_data:
            conference_data = json.dumps(conference_data)

        return cls(
            event_id=event["id"],
            calendar_id=calendar_id,
            summary=event.get("summary", "Untitled"),
            description=event.get("description"),
            start_time=start_time,
            end_time=end_time,
            location=event.get("location"),
            created_at=created_at,
            updated_at=updated_at,
            status=event.get("status", "confirmed"),
            is_recurring=bool(event.get("recurrence")),
            recurrence=(
                json.dumps(event["recurrence"]) if event.get("recurrence") else None
            ),
            attendees=attendees,
            conference_data=conference_data,
        )


class SQLiteCalendarEventRepository:
    """SQLite repository for calendar events."""

    def __init__(self, db: Database):
        """Initialize the repository.

        Args:
            db: Database instance
        """
        self.db = db
        self._ensure_table()

    def _ensure_table(self):
        """Ensure the calendar_events table exists."""
        # Main events table
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS calendar_events (
                event_id TEXT,
                calendar_id TEXT,
                summary TEXT NOT NULL,
                description TEXT,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP NOT NULL,
                location TEXT,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                status TEXT NOT NULL,
                is_recurring BOOLEAN NOT NULL DEFAULT 0,
                recurrence TEXT,
                attendees TEXT,
                conference_data TEXT,
                is_deleted BOOLEAN NOT NULL DEFAULT 0,
                PRIMARY KEY (event_id, calendar_id)
            )
        """
        )

        # Event history table for tracking changes
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS calendar_event_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL,
                calendar_id TEXT NOT NULL,
                change_type TEXT NOT NULL,  -- 'created', 'updated', 'deleted'
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                old_data TEXT,  -- JSON of old event data if update/delete
                new_data TEXT,  -- JSON of new event data if create/update
                FOREIGN KEY (event_id, calendar_id) 
                    REFERENCES calendar_events (event_id, calendar_id)
            )
        """
        )

    def save(self, event: CalendarEvent) -> None:
        """Save a calendar event.

        Args:
            event: Event to save
        """
        import json

        logger.debug(f"Saving calendar event {event.event_id}")

        # Check if event exists and get current data
        existing = self.get_event(event.event_id, event.calendar_id)
        change_type = "created" if not existing else "updated"

        # Prepare event data for history
        new_data = {
            "summary": event.summary,
            "description": event.description,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "location": event.location,
            "status": event.status,
            "is_recurring": event.is_recurring,
            "recurrence": event.recurrence,
            "attendees": event.attendees,
            "conference_data": event.conference_data,
        }

        # Save the event
        self.db.execute(
            """
            INSERT OR REPLACE INTO calendar_events (
                event_id, calendar_id, summary, description, start_time, end_time,
                location, created_at, updated_at, status, is_recurring,
                recurrence, attendees, conference_data, is_deleted
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                event.event_id,
                event.calendar_id,
                event.summary,
                event.description,
                event.start_time,
                event.end_time,
                event.location,
                event.created_at,
                event.updated_at,
                event.status,
                event.is_recurring,
                event.recurrence,
                event.attendees,
                event.conference_data,
            ),
        )

        # Record the change in history
        self.db.execute(
            """
            INSERT INTO calendar_event_history (
                event_id, calendar_id, change_type, 
                old_data, new_data
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                event.event_id,
                event.calendar_id,
                change_type,
                json.dumps(self._event_to_dict(existing)) if existing else None,
                json.dumps(new_data),
            ),
        )

    def delete(self, event_id: str, calendar_id: str) -> None:
        """Delete a calendar event.

        Args:
            event_id: ID of event to delete
            calendar_id: ID of calendar containing the event
        """
        import json

        logger.debug(f"Deleting calendar event {event_id}")

        # Get current data before deletion
        existing = self.get_event(event_id, calendar_id)
        if not existing:
            logger.warning(f"Event {event_id} not found for deletion")
            return

        # Soft delete the event
        self.db.execute(
            """
            UPDATE calendar_events 
            SET is_deleted = 1, updated_at = datetime('now')
            WHERE event_id = ? AND calendar_id = ?
            """,
            (event_id, calendar_id),
        )

        # Record deletion in history
        self.db.execute(
            """
            INSERT INTO calendar_event_history (
                event_id, calendar_id, change_type, old_data
            ) VALUES (?, ?, 'deleted', ?)
            """,
            (event_id, calendar_id, json.dumps(self._event_to_dict(existing))),
        )

    def get_event(self, event_id: str, calendar_id: str) -> Optional[CalendarEvent]:
        """Get a specific event.

        Args:
            event_id: ID of event to get
            calendar_id: ID of calendar containing the event

        Returns:
            CalendarEvent if found, None otherwise
        """
        row = self.db.fetch_one(
            """
            SELECT event_id, calendar_id, summary, description, start_time, end_time,
                   location, created_at, updated_at, status, is_recurring,
                   recurrence, attendees, conference_data
            FROM calendar_events
            WHERE event_id = ? AND calendar_id = ? AND is_deleted = 0
            """,
            (event_id, calendar_id),
        )

        if row:
            return CalendarEvent(
                event_id=row[0],
                calendar_id=row[1],
                summary=row[2],
                description=row[3],
                start_time=datetime.fromisoformat(row[4]),
                end_time=datetime.fromisoformat(row[5]),
                location=row[6],
                created_at=datetime.fromisoformat(row[7]),
                updated_at=datetime.fromisoformat(row[8]),
                status=row[9],
                is_recurring=bool(row[10]),
                recurrence=row[11],
                attendees=row[12],
                conference_data=row[13],
            )
        return None

    def get_event_history(self, event_id: str, calendar_id: str) -> List[dict]:
        """Get the change history for an event.

        Args:
            event_id: ID of event to get history for
            calendar_id: ID of calendar containing the event

        Returns:
            List of history entries, each containing:
            - change_type: Type of change (created/updated/deleted)
            - timestamp: When the change occurred
            - old_data: Previous event data if update/delete
            - new_data: New event data if create/update
        """
        import json

        rows = self.db.fetch_all(
            """
            SELECT change_type, timestamp, old_data, new_data
            FROM calendar_event_history
            WHERE event_id = ? AND calendar_id = ?
            ORDER BY timestamp DESC
            """,
            (event_id, calendar_id),
        )

        return [
            {
                "change_type": row[0],
                "timestamp": datetime.fromisoformat(row[1]),
                "old_data": json.loads(row[2]) if row[2] else None,
                "new_data": json.loads(row[3]) if row[3] else None,
            }
            for row in rows
        ]

    def _event_to_dict(self, event: Optional[CalendarEvent]) -> Optional[dict]:
        """Convert a CalendarEvent to a dictionary for history storage.

        Args:
            event: Event to convert

        Returns:
            Dictionary representation of the event, or None if event is None
        """
        if not event:
            return None

        return {
            "summary": event.summary,
            "description": event.description,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "location": event.location,
            "status": event.status,
            "is_recurring": event.is_recurring,
            "recurrence": event.recurrence,
            "attendees": event.attendees,
            "conference_data": event.conference_data,
        }

    def get_all_events(self, calendar_id: str) -> List[CalendarEvent]:
        """Get all events from a calendar.

        Args:
            calendar_id: Calendar ID to get events for

        Returns:
            List of calendar events
        """
        rows = self.db.fetch_all(
            """
            SELECT event_id, calendar_id, summary, description, start_time, end_time,
                   location, created_at, updated_at, status, is_recurring,
                   recurrence, attendees, conference_data
            FROM calendar_events
            WHERE calendar_id = ?
            ORDER BY start_time DESC
            """,
            (calendar_id,),
        )

        return [
            CalendarEvent(
                event_id=row[0],
                calendar_id=row[1],
                summary=row[2],
                description=row[3],
                start_time=datetime.fromisoformat(row[4]),
                end_time=datetime.fromisoformat(row[5]),
                location=row[6],
                created_at=datetime.fromisoformat(row[7]),
                updated_at=datetime.fromisoformat(row[8]),
                status=row[9],
                is_recurring=bool(row[10]),
                recurrence=row[11],
                attendees=row[12],
                conference_data=row[13],
            )
            for row in rows
        ]

    def get_upcoming_events(
        self, calendar_id: str, limit: int = 10
    ) -> List[CalendarEvent]:
        """Get upcoming events from a calendar.

        Args:
            calendar_id: Calendar ID to get events for
            limit: Maximum number of events to return

        Returns:
            List of upcoming calendar events
        """
        rows = self.db.fetch_all(
            """
            SELECT event_id, calendar_id, summary, description, start_time, end_time,
                   location, created_at, updated_at, status, is_recurring,
                   recurrence, attendees, conference_data
            FROM calendar_events
            WHERE calendar_id = ? AND end_time >= datetime('now')
            ORDER BY start_time ASC
            LIMIT ?
            """,
            (calendar_id, limit),
        )

        return [
            CalendarEvent(
                event_id=row[0],
                calendar_id=row[1],
                summary=row[2],
                description=row[3],
                start_time=datetime.fromisoformat(row[4]),
                end_time=datetime.fromisoformat(row[5]),
                location=row[6],
                created_at=datetime.fromisoformat(row[7]),
                updated_at=datetime.fromisoformat(row[8]),
                status=row[9],
                is_recurring=bool(row[10]),
                recurrence=row[11],
                attendees=row[12],
                conference_data=row[13],
            )
            for row in rows
        ]

    def get_latest_event(self, calendar_id: str) -> Optional[CalendarEvent]:
        """Get the most recently updated event for a calendar.

        Args:
            calendar_id: The ID of the calendar to query

        Returns:
            The most recently updated CalendarEvent or None if no events exist
        """
        query = """
            SELECT * FROM calendar_events 
            WHERE calendar_id = ? AND is_deleted = 0
            ORDER BY updated_at DESC 
            LIMIT 1
        """

        result = self.db.fetch_one(query, (calendar_id,))
        if result:
            return CalendarEvent(**result)
        return None
