"""Client for interacting with Google Calendar API."""

from typing import Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from loguru import logger


class GoogleCalendarClient:
    """Client for interacting with Google Calendar API."""

    def __init__(self, credentials: Credentials):
        """Initialize the Google Calendar client.

        Args:
            credentials: Google OAuth2 credentials
        """
        logger.debug("Initializing Google Calendar client")
        self.service = build("calendar", "v3", credentials=credentials)

    def get_event(self, calendar_id: str, event_id: str) -> dict:
        """Get an event by ID.

        Args:
            calendar_id: ID of the calendar containing the event
            event_id: ID of the event to retrieve

        Returns:
            Event details
        """
        logger.debug(f"Fetching event {event_id} from calendar {calendar_id}")
        try:
            event = (
                self.service.events()
                .get(calendarId=calendar_id, eventId=event_id)
                .execute()
            )
            logger.debug(f"Successfully retrieved event {event_id}")
            return event
        except Exception as e:
            logger.error(f"Failed to fetch event {event_id}: {str(e)}")
            raise

    def list_events(self, calendar_id: str, updated_min: Optional[str] = None) -> list:
        """List events in a calendar.

        Args:
            calendar_id: ID of the calendar to list events from
            updated_min: Optional RFC3339 timestamp to filter events updated after this time

        Returns:
            List of events
        """
        logger.debug(f"Listing events for calendar {calendar_id}")
        try:
            params = {
                "calendarId": calendar_id,
                "maxResults": 100,  # Adjust as needed
                "singleEvents": True,
                "orderBy": "updated",
            }
            if updated_min:
                params["updatedMin"] = updated_min

            events = []
            page_token = None
            while True:
                if page_token:
                    params["pageToken"] = page_token

                response = self.service.events().list(**params).execute()
                events.extend(response.get("items", []))

                page_token = response.get("nextPageToken")
                if not page_token:
                    break

            logger.debug(f"Successfully retrieved {len(events)} events")
            return events

        except Exception as e:
            logger.error(f"Failed to list events: {str(e)}")
            raise
