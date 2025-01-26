"""Unified webhook server for handling notifications from various services."""

import uuid
from datetime import datetime, timedelta
from distutils.command.build import build

from fastapi import FastAPI
from googleapiclient.discovery import build as google_client_builder
from loguru import logger

from aerith_ingestion.config import load_config
from aerith_ingestion.services.google_calendar.auth import create_credentials
from aerith_ingestion.services.google_calendar.webhook_handler import (
    handle_webhook as handle_gcal_webhook,
)
from aerith_ingestion.services.todoist.webhook_handler import (
    handle_webhook as handle_todoist_webhook,
)

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    """Create webhook channel on startup."""
    try:
        config = load_config()
        credentials = create_credentials(config.api.google_calendar)
        service = google_client_builder("calendar", "v3", credentials=credentials)

        # Create webhook channel
        channel_id = str(uuid.uuid4())
        expiration = int((datetime.now() + timedelta(days=7)).timestamp() * 1000)
        webhook_url = f"{config.api.webhook_base_url}/webhook/google-calendar"

        body = {
            "id": channel_id,
            "type": "web_hook",
            "address": webhook_url,
            "expiration": expiration,
        }

        service.events().watch(calendarId="primary", body=body).execute()
        logger.info(f"Created webhook channel {channel_id} for primary calendar")

    except Exception as e:
        logger.error(f"Failed to create webhook channel: {str(e)}")
        logger.exception("Full traceback:")


# Register webhook endpoints
app.post("/webhook/google-calendar")(handle_gcal_webhook)
app.post("/webhook/todoist")(handle_todoist_webhook)
