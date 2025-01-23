import click
from loguru import logger

from aerith_ingestion.config import load_config
from aerith_ingestion.persistence.database import Database
from aerith_ingestion.persistence.webhook_channel import SQLiteWebhookChannelRepository
from aerith_ingestion.services.google_calendar.auth import (
    create_credentials,
    run_oauth_flow,
)
from aerith_ingestion.services.google_calendar.client import GoogleCalendarClient


@click.group()
def calendar():
    """Google Calendar commands."""
    pass


@calendar.group()
def db():
    """Database management commands."""
    pass


@db.command()
def stats():
    """Show calendar database statistics."""
    config = load_config()
    db = Database(config.database.sqlite.database_path)
    
    logger.info("Calendar Database Statistics:")
    logger.info("----------------------------")
    
    # Total events and basic stats
    total_events = db.fetch_one("SELECT COUNT(*) FROM calendar_events")[0]
    logger.info(f"Total events: {total_events}")
    
    # Events by status
    status_counts = db.fetch_all(
        "SELECT status, COUNT(*) as count FROM calendar_events GROUP BY status"
    )
    logger.info("\nEvents by status:")
    for status, count in status_counts:
        logger.info(f"  {status}: {count}")
    
    # Recurring vs non-recurring
    recurring = db.fetch_one(
        "SELECT COUNT(*) FROM calendar_events WHERE is_recurring = 1"
    )[0]
    logger.info(f"\nRecurring events: {recurring}")
    logger.info(f"Non-recurring events: {total_events - recurring}")
    
    # Events by month
    logger.info("\nEvents by month:")
    month_counts = db.fetch_all("""
        SELECT strftime('%Y-%m', start_time) as month, 
               COUNT(*) as count 
        FROM calendar_events 
        GROUP BY month 
        ORDER BY month DESC 
        LIMIT 12
    """)
    for month, count in month_counts:
        logger.info(f"  {month}: {count}")
    
    # Events with location/conference data
    with_location = db.fetch_one(
        "SELECT COUNT(*) FROM calendar_events WHERE location IS NOT NULL"
    )[0]
    with_conference = db.fetch_one(
        "SELECT COUNT(*) FROM calendar_events WHERE conference_data IS NOT NULL"
    )[0]
    logger.info(f"\nEvents with location: {with_location}")
    logger.info(f"Events with conference data: {with_conference}")
    
    # Most common event types (based on summary)
    logger.info("\nTop 10 event types:")
    event_types = db.fetch_all("""
        SELECT summary, COUNT(*) as count 
        FROM calendar_events 
        GROUP BY summary 
        ORDER BY count DESC 
        LIMIT 10
    """)
    for summary, count in event_types:
        logger.info(f"  {summary}: {count}")
    
    # History statistics
    history_count = db.fetch_one("SELECT COUNT(*) FROM calendar_event_history")[0]
    logger.info(f"\nHistory entries: {history_count}")
    
    if history_count > 0:
        history_types = db.fetch_all("""
            SELECT change_type, COUNT(*) as count 
            FROM calendar_event_history 
            GROUP BY change_type
        """)
        logger.info("Changes by type:")
        for change_type, count in history_types:
            logger.info(f"  {change_type}: {count}")


@db.command()
def truncate():
    """Truncate all calendar event tables."""
    config = load_config()
    db = Database(config.database.sqlite.database_path)
    
    # Show database statistics before truncating
    logger.info("Current database statistics:")
    
    # Total events
    total_events = db.fetch_one("SELECT COUNT(*) FROM calendar_events")[0]
    logger.info(f"Total events: {total_events}")
    
    # Events by status
    status_counts = db.fetch_all(
        "SELECT status, COUNT(*) as count FROM calendar_events GROUP BY status"
    )
    logger.info("Events by status:")
    for status, count in status_counts:
        logger.info(f"  {status}: {count}")
    
    # Recurring vs non-recurring
    recurring = db.fetch_one(
        "SELECT COUNT(*) FROM calendar_events WHERE is_recurring = 1"
    )[0]
    logger.info(f"Recurring events: {recurring}")
    logger.info(f"Non-recurring events: {total_events - recurring}")
    
    # History entries
    history_count = db.fetch_one("SELECT COUNT(*) FROM calendar_event_history")[0]
    logger.info(f"History entries: {history_count}")
    
    # Proceed with truncation
    logger.info("Truncating tables...")
    
    # Truncate tables in correct order due to foreign key constraints
    db.truncate_table("calendar_event_history")
    db.truncate_table("calendar_events")
    
    logger.info("Successfully truncated calendar event tables")


@calendar.group()
def auth():
    """Authentication commands."""
    pass


@auth.command()
@click.option("--client-id", envvar="GOOGLE_CLIENT_ID", help="Google OAuth client ID")
@click.option(
    "--client-secret", envvar="GOOGLE_CLIENT_SECRET", help="Google OAuth client secret"
)
@click.option("--env-file", default=".env", help="Environment file to update")
def setup(client_id: str, client_secret: str, env_file: str):
    """Set up Google Calendar OAuth2 credentials."""
    if not client_id or not client_secret:
        logger.error("Both client_id and client_secret are required")
        return

    try:
        # Run the OAuth2 flow
        logger.info("Starting OAuth2 flow...")
        credentials = run_oauth_flow(client_id, client_secret)

        # Update the .env file
        from dotenv import load_dotenv, set_key

        load_dotenv(env_file)

        set_key(env_file, "GOOGLE_CLIENT_ID", client_id)
        set_key(env_file, "GOOGLE_CLIENT_SECRET", client_secret)
        set_key(env_file, "GOOGLE_REFRESH_TOKEN", credentials["refresh_token"])

        logger.info(f"Successfully saved OAuth2 credentials to {env_file}")

    except Exception as e:
        logger.error(f"Failed to set up OAuth2: {str(e)}")
        logger.exception("Full traceback:")


@calendar.group()
def webhook():
    """Webhook management commands."""
    pass


@webhook.command()
def serve():
    """Start the webhook server."""
    import uvicorn

    uvicorn.run(
        "aerith_ingestion.services.google_calendar.webhook:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


@webhook.command()
def list():
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
