"""Command for running the Todoist webhook server."""

import click
import uvicorn
from loguru import logger

from aerith_ingestion.cli import pass_context
from aerith_ingestion.services.todoist.webhook import app


@click.group()
def todoist_webhook():
    """Manage Todoist webhook server."""
    pass


@todoist_webhook.command()
@click.option("--host", default="0.0.0.0", help="Host to bind the webhook server to")
@click.option("--port", default=8001, type=int, help="Port to run the webhook server on")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
@pass_context
def serve(ctx, host: str, port: int, reload: bool):
    """Run the webhook server to receive Todoist notifications.

    This command:
    1. Initializes the webhook server
    2. Starts listening for notifications
    """
    try:
        logger.info(f"Starting Todoist webhook server at {host}:{port}")

        # Configure ASGI application
        config = uvicorn.Config(
            app=app, host=host, port=port, reload=reload, log_level="info"
        )

        # Run the server
        server = uvicorn.Server(config)
        server.run()

    except Exception as e:
        logger.exception("Failed to start webhook server")
        raise click.ClickException(str(e)) 