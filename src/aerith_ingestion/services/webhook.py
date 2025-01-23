"""Unified webhook server for handling notifications from various services."""

from fastapi import Depends, FastAPI, Request, Response
from loguru import logger

from aerith_ingestion.services.google_calendar.webhook import WebhookHandler as GCalWebhookHandler
from aerith_ingestion.services.todoist.webhook import WebhookHandler as TodoistWebhookHandler
from aerith_ingestion.services.google_calendar.client import GoogleCalendarClient
from aerith_ingestion.config import load_config
from aerith_ingestion.services.google_calendar.auth import create_credentials

app = FastAPI()


def get_calendar_client() -> GoogleCalendarClient:
    """Get an authenticated Google Calendar client."""
    config = load_config()
    credentials = create_credentials(config.api.google_calendar)
    return GoogleCalendarClient(credentials)


@app.post("/webhook/google-calendar")
async def gcal_webhook_endpoint(
    request: Request,
    response: Response,
    calendar_client: GoogleCalendarClient = Depends(get_calendar_client),
):
    """Handle Google Calendar webhook notifications."""
    logger.debug("Received Google Calendar webhook request")
    logger.debug(f"Headers: {dict(request.headers)}")

    try:
        body = await request.json() if await request.body() else None
        logger.debug(f"Request body: {body}")

        handler = GCalWebhookHandler(calendar_client)
        await handler.handle_notification(dict(request.headers), body)

        logger.debug("Successfully processed Google Calendar webhook notification")
        return Response(status_code=200)

    except Exception as e:
        logger.error(f"Error processing Google Calendar webhook notification: {str(e)}")
        logger.exception("Full traceback:")
        return Response(status_code=200)


@app.post("/webhook/todoist")
async def todoist_webhook_endpoint(request: Request):
    """Handle Todoist webhook notifications."""
    logger.debug("Received Todoist webhook request")
    logger.debug(f"Headers: {dict(request.headers)}")

    try:
        body = await request.json() if await request.body() else None
        logger.debug(f"Request body: {body}")

        handler = TodoistWebhookHandler()
        await handler.handle_notification(dict(request.headers), body)

        logger.debug("Successfully processed Todoist webhook notification")
        return Response(status_code=200)

    except Exception as e:
        logger.error(f"Error processing Todoist webhook notification: {str(e)}")
        logger.exception("Full traceback:")
        return Response(status_code=200) 