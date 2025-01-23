from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from loguru import logger

from aerith_ingestion.config import load_config
from aerith_ingestion.persistence.calendar_event import (
    CalendarEvent,
    SQLiteCalendarEventRepository,
)
from aerith_ingestion.persistence.database import Database
from aerith_ingestion.persistence.webhook_channel import SQLiteWebhookChannelRepository
from aerith_ingestion.services.google_calendar.auth import create_credentials
from aerith_ingestion.services.google_calendar.client import GoogleCalendarClient

app = FastAPI()


def get_calendar_client() -> GoogleCalendarClient:
    """Get an authenticated Google Calendar client.

    Returns:
        Authenticated Google Calendar client
    """
    config = load_config()
    credentials = create_credentials(config.api.google_calendar)
    return GoogleCalendarClient(credentials)


def get_channel_repo() -> SQLiteWebhookChannelRepository:
    """Get a webhook channel repository.

    Returns:
        Webhook channel repository
    """
    config = load_config()
    db = Database(config.database.sqlite.database_path)
    return SQLiteWebhookChannelRepository(db)


class WebhookHandler:
    """Handler for Google Calendar webhook notifications."""

    def __init__(self, calendar_client: GoogleCalendarClient):
        """Initialize the webhook handler.

        Args:
            calendar_client: Initialized Google Calendar client
        """
        logger.debug("Initializing Google Calendar webhook handler")
        self.calendar_client = calendar_client

        # Initialize event repository
        config = load_config()
        db = Database(config.database.sqlite.database_path)
        self.event_repo = SQLiteCalendarEventRepository(db)

    async def handle_notification(
        self, headers: Dict[str, str], body: Optional[Dict[str, Any]] = None
    ) -> None:
        """Handle an incoming webhook notification.

        Args:
            headers: Request headers containing notification metadata
            body: Optional request body
        """
        # Extract headers with case-insensitive lookup
        channel_id = next(
            (v for k, v in headers.items() if k.lower() == "x-goog-channel-id"), None
        )
        resource_id = next(
            (v for k, v in headers.items() if k.lower() == "x-goog-resource-id"), None
        )
        resource_state = next(
            (v for k, v in headers.items() if k.lower() == "x-goog-resource-state"),
            None,
        )
        message_number = next(
            (v for k, v in headers.items() if k.lower() == "x-goog-message-number"),
            None,
        )

        logger.debug(
            f"Processing notification: Channel={channel_id}, State={resource_state}, Message={message_number}"
        )

        # Handle sync message
        if resource_state == "sync":
            logger.info(f"Channel {channel_id} synchronized")
            return

        # Handle resource state changes
        if resource_state == "exists":
            # Resource was created or modified
            logger.info(f"Resource {resource_id} changed")
            resource_uri = next(
                (v for k, v in headers.items() if k.lower() == "x-goog-resource-uri"),
                None,
            )
            logger.debug(f"Resource URI: {resource_uri}")

            if not resource_uri:
                logger.warning("Missing resource URI in notification")
                return

            try:
                # Parse the resource URI to determine the type of change
                parsed = urlparse(resource_uri)
                path_parts = [p for p in parsed.path.split("/") if p]
                logger.debug(f"Path parts: {path_parts}")

                # Check if this is a calendar list notification
                query_params = parse_qs(parsed.query)
                logger.debug(f"Query params: {query_params}")

                # Calendar list format: /calendar/v3/calendars/primary/events?alt=json
                # Single event format: /calendar/v3/calendars/{calendarId}/events/{eventId}
                if path_parts[-1] == "events" and "alt" in query_params:
                    # This is a calendar list notification
                    calendar_id = path_parts[-2]  # 'primary' or calendar ID
                    logger.info(f"Calendar list changed for calendar {calendar_id}")

                    try:
                        # Get the latest sync token or timestamp from the database
                        latest_event = self.event_repo.get_latest_event(calendar_id)
                        updated_min = latest_event.updated_at if latest_event else None

                        # Fetch only updated events
                        events = self.calendar_client.list_events(
                            calendar_id, updated_min=updated_min
                        )
                        logger.info(
                            f"Fetched {len(events)} updated events from calendar {calendar_id}"
                        )

                        # Process each event
                        for event in events:
                            logger.debug(
                                f"Processing event: {event.get('summary', 'Untitled')}"
                            )
                            calendar_event = CalendarEvent.from_google_event(
                                calendar_id, event
                            )
                            self.event_repo.save(calendar_event)

                        logger.info("Successfully processed calendar list update")
                    except Exception as e:
                        logger.error(f"Failed to process calendar list: {str(e)}")
                        logger.exception("Full traceback:")

                elif path_parts[-2] == "events":
                    # This is a single event notification
                    calendar_id = path_parts[-3]
                    event_id = path_parts[-1]

                    logger.info(f"Event {event_id} changed in calendar {calendar_id}")

                    # Fetch event details
                    event = self.calendar_client.get_event(calendar_id, event_id)
                    logger.info(f"Fetched event: {event.get('summary', 'Untitled')}")
                    logger.debug(f"Event details: {event}")

                    # Store the event
                    calendar_event = CalendarEvent.from_google_event(calendar_id, event)
                    self.event_repo.save(calendar_event)
                    logger.info("Successfully processed event update")

                else:
                    logger.warning(f"Unknown resource URI format: {resource_uri}")
                    return

            except Exception as e:
                logger.error(f"Failed to process event: {str(e)}")
                logger.exception("Full traceback:")

        elif resource_state == "not_exists":
            # Resource was deleted
            logger.info(f"Resource {resource_id} deleted")

            # Try to extract event ID from resource URI
            resource_uri = next(
                (v for k, v in headers.items() if k.lower() == "x-goog-resource-uri"),
                None,
            )
            if resource_uri:
                try:
                    path_parts = [p for p in resource_uri.split("/") if p]
                    if len(path_parts) >= 5 and path_parts[-2] == "events":
                        calendar_id = path_parts[-3]
                        event_id = path_parts[-1]
                        self.event_repo.delete(event_id, calendar_id)
                        logger.info(f"Deleted event {event_id} from database")
                except Exception as e:
                    logger.error(f"Failed to delete event: {str(e)}")
                    logger.exception("Full traceback:")

        else:
            logger.warning(f"Unknown resource state: {resource_state}")
            return


@app.post("/webhook/google-calendar")
async def webhook_endpoint(
    request: Request,
    response: Response,
    calendar_client: GoogleCalendarClient = Depends(get_calendar_client),
):
    """FastAPI endpoint for receiving Google Calendar webhooks."""
    logger.debug("Received Google Calendar webhook request")
    logger.debug(f"Headers: {dict(request.headers)}")

    # Log all headers for debugging
    headers = dict(request.headers)
    for key, value in headers.items():
        logger.debug(f"Header {key}: {value}")

    # Check for sync verification request
    if headers.get("x-goog-resource-state") == "sync":
        logger.info("Received sync verification request")
        return Response(status_code=200)

    # Process the notification
    try:
        body = await request.json() if await request.body() else None
        logger.debug(f"Request body: {body}")

        handler = WebhookHandler(calendar_client)
        await handler.handle_notification(headers, body)

        logger.debug("Successfully processed webhook notification")
        return Response(status_code=200)

    except Exception as e:
        logger.error(f"Error processing webhook notification: {str(e)}")
        # Don't raise HTTP exception, just log and return 200
        # This prevents Google from retrying failed requests
        return Response(status_code=200)
