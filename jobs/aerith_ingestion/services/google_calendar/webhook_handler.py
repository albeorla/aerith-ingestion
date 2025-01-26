"""Handler for Google Calendar webhook notifications."""

from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse

from fastapi import Depends, Request, Response
from loguru import logger

from aerith_ingestion.config import load_config
from aerith_ingestion.persistence.calendar_event import CalendarEvent
from aerith_ingestion.persistence.database import Database
from aerith_ingestion.services.google_calendar.auth import create_credentials
from aerith_ingestion.services.google_calendar.client import GoogleCalendarClient


def get_calendar_client() -> GoogleCalendarClient:
    """Get an authenticated Google Calendar client."""
    config = load_config()
    credentials = create_credentials(config.api.google_calendar)
    return GoogleCalendarClient(credentials)


class GoogleCalendarHandler:
    """Handler for Google Calendar webhook notifications."""

    def __init__(self, calendar_client: GoogleCalendarClient):
        """Initialize the handler.

        Args:
            calendar_client: Authenticated Google Calendar client
        """
        logger.debug("Initializing Google Calendar webhook handler")
        self.calendar_client = calendar_client
        config = load_config()
        self.db = Database(config.database.sqlite.database_path)

    async def handle_notification(
        self, headers: Dict[str, str], body: Optional[Dict[str, Any]] = None
    ) -> None:
        """Handle an incoming webhook notification.

        Args:
            headers: Request headers containing notification metadata
            body: Optional request body
        """
        resource_state = next(
            (v for k, v in headers.items() if k.lower() == "x-goog-resource-state"),
            None,
        )
        logger.debug(f"Processing notification with state: {resource_state}")

        # Handle resource state changes
        if resource_state == "exists":
            await self._handle_calendar_update(headers)
        elif resource_state == "not_exists":
            await self._handle_calendar_delete(headers)
        else:
            logger.warning(f"Unknown resource state: {resource_state}")

    async def _handle_calendar_update(self, headers: Dict[str, str]) -> None:
        """Handle calendar update notification."""
        resource_uri = next(
            (v for k, v in headers.items() if k.lower() == "x-goog-resource-uri"),
            None,
        )
        if not resource_uri:
            logger.warning("Missing resource URI in notification")
            return

        try:
            # Parse the resource URI to determine the type of change
            parsed = urlparse(resource_uri)
            path_parts = [p for p in parsed.path.split("/") if p]
            query_params = parse_qs(parsed.query)

            # Calendar list format: /calendar/v3/calendars/primary/events?alt=json
            # Single event format: /calendar/v3/calendars/{calendarId}/events/{eventId}
            if path_parts[-1] == "events" and "alt" in query_params:
                await self._handle_calendar_list_update(path_parts[-2])
            elif path_parts[-2] == "events":
                await self._handle_single_event_update(path_parts[-3], path_parts[-1])
            else:
                logger.warning(f"Unknown resource URI format: {resource_uri}")

        except Exception as e:
            logger.error(f"Failed to process calendar update: {str(e)}")
            logger.exception("Full traceback:")

    async def _handle_calendar_list_update(self, calendar_id: str) -> None:
        """Handle calendar list update."""
        logger.info(f"Calendar list changed for calendar {calendar_id}")
        try:
            # Get the latest sync token or timestamp from the database
            latest_event = self.event_repo.get_latest_event(calendar_id)
            updated_min = latest_event.updated_at if latest_event else None

            # Fetch only updated events
            events = self.calendar_client.list_events(
                calendar_id, updated_min=updated_min
            )
            logger.info(f"Fetched {len(events)} updated events")

            # Process each event
            for event in events:
                logger.debug(f"Processing event: {event.get('summary', 'Untitled')}")
                calendar_event = CalendarEvent.from_google_event(calendar_id, event)
                self.event_repo.save(calendar_event)

        except Exception as e:
            logger.error(f"Failed to process calendar list: {str(e)}")
            logger.exception("Full traceback:")

    async def _handle_single_event_update(
        self, calendar_id: str, event_id: str
    ) -> None:
        """Handle single event update."""
        logger.info(f"Event {event_id} changed in calendar {calendar_id}")
        try:
            event = self.calendar_client.get_event(calendar_id, event_id)
            logger.debug(f"Fetched event: {event.get('summary', 'Untitled')}")
            calendar_event = CalendarEvent.from_google_event(calendar_id, event)
            self.event_repo.save(calendar_event)
        except Exception as e:
            logger.error(f"Failed to process event update: {str(e)}")
            logger.exception("Full traceback:")

    async def _handle_calendar_delete(self, headers: Dict[str, str]) -> None:
        """Handle calendar delete notification."""
        resource_uri = next(
            (v for k, v in headers.items() if k.lower() == "x-goog-resource-uri"),
            None,
        )
        if not resource_uri:
            return

        try:
            path_parts = [p for p in resource_uri.split("/") if p]
            if len(path_parts) >= 5 and path_parts[-2] == "events":
                calendar_id = path_parts[-3]
                event_id = path_parts[-1]
                self.event_repo.delete(event_id, calendar_id)
                logger.info(f"Deleted event {event_id}")
        except Exception as e:
            logger.error(f"Failed to delete event: {str(e)}")
            logger.exception("Full traceback:")


async def handle_webhook(
    request: Request,
    response: Response,
    calendar_client: GoogleCalendarClient = Depends(get_calendar_client),
) -> Response:
    """Handle Google Calendar webhook notifications."""
    logger.debug("Received Google Calendar webhook request")
    logger.debug(f"Headers: {dict(request.headers)}")

    try:
        body = await request.json() if await request.body() else None
        logger.debug(f"Request body: {body}")

        handler = GoogleCalendarHandler(calendar_client)
        await handler.handle_notification(dict(request.headers), body)

        logger.debug("Successfully processed Google Calendar webhook notification")
        return Response(status_code=200)

    except Exception as e:
        logger.error(f"Error processing Google Calendar webhook notification: {str(e)}")
        logger.exception("Full traceback:")
        return Response(status_code=200)
