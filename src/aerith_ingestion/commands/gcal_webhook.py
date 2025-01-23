"""Command for running the Google Calendar webhook server."""

import os
from datetime import datetime, timedelta

import click
import uvicorn
from loguru import logger

from aerith_ingestion.cli import pass_context
from aerith_ingestion.persistence.database import Database
from aerith_ingestion.persistence.webhook_channel import (
    SQLiteWebhookChannelRepository,
    WebhookChannel,
)
from aerith_ingestion.services.google_calendar.auth import (
    create_credentials,
    run_oauth_flow,
)
from aerith_ingestion.services.google_calendar.client import GoogleCalendarClient
from aerith_ingestion.services.google_calendar.config import GoogleCalendarSettings
from aerith_ingestion.services.google_calendar.webhook import WebhookHandler, app


def get_calendar_client(ctx) -> GoogleCalendarClient:
    """Create an authenticated Google Calendar client.

    Args:
        ctx: CLI context with configuration

    Returns:
        Authenticated Google Calendar client
    """
    credentials = create_credentials(ctx.config.api.google_calendar)
    return GoogleCalendarClient(credentials)


@click.group()
def gcal_webhook():
    """Manage Google Calendar webhook server."""
    pass


@gcal_webhook.group()
def auth():
    """Manage Google Calendar authentication."""
    pass


@auth.command()
@click.option(
    "--client-id", envvar="GOOGLE_CALENDAR_CLIENT_ID", help="Google OAuth2 client ID"
)
@click.option(
    "--client-secret",
    envvar="GOOGLE_CALENDAR_CLIENT_SECRET",
    help="Google OAuth2 client secret",
)
@click.option(
    "--env-file",
    type=click.Path(exists=False),
    default=".env",
    help="Path to .env file to update",
)
@pass_context
def setup(ctx, client_id: str, client_secret: str, env_file: str):
    """Set up Google Calendar OAuth2 credentials."""
    try:
        if not client_id or not client_secret:
            raise click.ClickException(
                "Please provide client_id and client_secret via options or environment variables"
            )

        logger.info("Starting Google Calendar OAuth2 setup")

        # Run OAuth flow
        creds = run_oauth_flow(client_id, client_secret)

        # Update .env file
        env_vars = {
            "GOOGLE_CALENDAR_CLIENT_ID": client_id,
            "GOOGLE_CALENDAR_CLIENT_SECRET": client_secret,
            "GOOGLE_CALENDAR_REFRESH_TOKEN": creds["refresh_token"],
        }

        # Read existing .env
        existing_vars = {}
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                for line in f:
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        existing_vars[key] = value

        # Update with new values
        existing_vars.update(env_vars)

        # Write back to .env
        with open(env_file, "w") as f:
            for key, value in sorted(existing_vars.items()):
                f.write(f"{key}={value}\n")

        logger.info(f"Updated {env_file} with Google Calendar credentials")
        logger.info("OAuth2 setup complete!")

    except Exception as e:
        logger.exception("Failed to set up OAuth2")
        raise click.ClickException(str(e))


@gcal_webhook.command()
@click.option("--host", default="0.0.0.0", help="Host to bind the webhook server to")
@click.option("--port", default=8000, type=int, help="Port to run the webhook server on")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
@click.option("--calendar-id", default="primary", help="Calendar ID to watch for changes")
@pass_context
def serve(ctx, host: str, port: int, reload: bool, calendar_id: str):
    """Run the webhook server to receive Google Calendar notifications."""
    try:
        # Load settings and initialize repositories
        settings = GoogleCalendarSettings()
        db = Database(ctx.config.database.sqlite.database_path)
        channel_repo = SQLiteWebhookChannelRepository(db)

        # Check for existing active channel
        channel = channel_repo.get_active_channel(calendar_id)

        # Create new channel if needed
        if not channel:
            logger.info(f"No active webhook channel found for calendar {calendar_id}")
            client = get_calendar_client(ctx)

            # Calculate expiration (7 days from now)
            expiration = int((datetime.now() + timedelta(days=7)).timestamp() * 1000)

            # Create webhook channel
            response = client.create_webhook_channel(
                calendar_id=calendar_id,
                webhook_url=settings.webhook_url,
                token=settings.webhook_token,
                expiration=expiration,
            )

            # Save channel details
            channel = WebhookChannel(
                channel_id=response["id"],
                resource_id=response["resourceId"],
                calendar_id=calendar_id,
                created_at=datetime.now(),
                expires_at=datetime.fromtimestamp(expiration / 1000),
            )
            channel_repo.save(channel)
            logger.info(f"Created new webhook channel {channel.channel_id}")
        else:
            logger.info(f"Using existing webhook channel {channel.channel_id}")

            # Check if channel is close to expiration
            if channel.expires_at:
                days_until_expiry = (channel.expires_at - datetime.now()).days
                if days_until_expiry < 1:
                    logger.warning(
                        f"Channel {channel.channel_id} expires in less than a day"
                    )

        logger.info(f"Starting webhook server at {host}:{port}")

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


@gcal_webhook.command()
@click.argument("calendar_id")
@pass_context
def list(ctx, calendar_id: str):
    """List active webhook channels."""
    try:
        # Get webhook channels
        repo = get_channel_repo()
        channels = repo.get_all_channels()

        if not channels:
            logger.info("No active webhook channels found")
            return

        # Display channel info
        logger.info(f"Found {len(channels)} active channels:")
        for channel in channels:
            logger.info(f"Channel ID: {channel.channel_id}")
            logger.info(f"Resource ID: {channel.resource_id}")
            logger.info(f"Expiration: {channel.expiration}")
            logger.info("---")

    except Exception as e:
        logger.error(f"Failed to list webhook channels: {str(e)}")
        logger.exception("Full traceback:") 