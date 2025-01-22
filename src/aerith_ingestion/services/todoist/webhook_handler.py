"""Handler for Todoist webhook notifications."""

from typing import Any, Dict, Optional

from fastapi import Request, Response
from loguru import logger

from aerith_ingestion.config import load_config
from aerith_ingestion.persistence.database import Database


class TodoistHandler:
    """Handler for Todoist webhook notifications."""

    def __init__(self):
        """Initialize the handler."""
        logger.debug("Initializing Todoist webhook handler")
        config = load_config()
        self.db = Database(config.database.sqlite.database_path)

    async def handle_notification(
        self, headers: Dict[str, str], body: Optional[Dict[str, Any]] = None
    ) -> None:
        """Handle an incoming webhook notification.

        Args:
            headers: Request headers containing notification metadata
            body: Request body containing event data
        """
        if not body:
            logger.warning("Received empty notification body")
            return

        event_name = body.get("event_name")
        event_data = body.get("event_data", {})

        logger.info(f"Received Todoist {event_name} event")
        logger.debug(f"Event data: {event_data}")

        try:
            if event_name == "item:added":
                await self._handle_item_added(event_data)
            elif event_name == "item:completed":
                await self._handle_item_completed(event_data)
            elif event_name == "item:updated":
                await self._handle_item_updated(event_data)
            elif event_name == "project:added":
                await self._handle_project_added(event_data)
            elif event_name == "project:updated":
                await self._handle_project_updated(event_data)
            else:
                logger.warning(f"Unhandled event type: {event_name}")

        except Exception as e:
            logger.error(f"Failed to process {event_name} event: {str(e)}")
            logger.exception("Full traceback:")

    async def _handle_item_added(self, data: Dict[str, Any]) -> None:
        """Handle item:added event."""
        logger.debug("Processing item:added event")
        # TODO: Implement item creation logic

    async def _handle_item_completed(self, data: Dict[str, Any]) -> None:
        """Handle item:completed event."""
        logger.debug("Processing item:completed event")
        # TODO: Implement item completion logic

    async def _handle_item_updated(self, data: Dict[str, Any]) -> None:
        """Handle item:updated event."""
        logger.debug("Processing item:updated event")
        # TODO: Implement item update logic

    async def _handle_project_added(self, data: Dict[str, Any]) -> None:
        """Handle project:added event."""
        logger.debug("Processing project:added event")
        # TODO: Implement project creation logic

    async def _handle_project_updated(self, data: Dict[str, Any]) -> None:
        """Handle project:updated event."""
        logger.debug("Processing project:updated event")
        # TODO: Implement project update logic


async def handle_webhook(request: Request) -> Response:
    """Handle Todoist webhook notifications."""
    logger.debug("Received Todoist webhook request")
    logger.debug(f"Headers: {dict(request.headers)}")

    try:
        body = await request.json() if await request.body() else None
        logger.debug(f"Request body: {body}")

        handler = TodoistHandler()
        await handler.handle_notification(dict(request.headers), body)

        logger.debug("Successfully processed Todoist webhook notification")
        return Response(status_code=200)

    except Exception as e:
        logger.error(f"Error processing Todoist webhook notification: {str(e)}")
        logger.exception("Full traceback:")
        return Response(status_code=200)
