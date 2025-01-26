"""Authentication utilities for Google Calendar."""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from loguru import logger

from aerith_ingestion.config.api import GoogleCalendarApiConfig


def create_credentials(config: GoogleCalendarApiConfig) -> Credentials:
    """Create Google OAuth2 credentials from config.

    Args:
        config: Google Calendar API configuration

    Returns:
        Google OAuth2 credentials
    """
    logger.debug("Creating Google Calendar credentials")

    # Default values
    token_uri = "https://oauth2.googleapis.com/token"
    scopes = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/calendar.events",
    ]

    try:
        credentials = Credentials(
            None,  # No token, will use refresh token
            refresh_token=config.refresh_token,
            token_uri=token_uri,
            client_id=config.client_id,
            client_secret=config.client_secret,
            scopes=scopes,
        )

        # Force token refresh with request object
        request = Request()
        credentials.refresh(request)
        logger.debug("Successfully refreshed Google Calendar credentials")

        return credentials
    except Exception as e:
        logger.error(f"Failed to create Google Calendar credentials: {str(e)}")
        raise


def run_oauth_flow(
    client_id: str, client_secret: str, scopes: list[str] = None
) -> dict:
    """Run OAuth2 flow to obtain refresh token.

    This will open a browser window for the user to authenticate and authorize the application.
    Make sure to configure http://localhost:8080 as an authorized redirect URI in Google Cloud Console.

    Args:
        client_id: Google OAuth2 client ID
        client_secret: Google OAuth2 client secret
        scopes: List of OAuth scopes to request

    Returns:
        Dictionary containing refresh token and other credentials
    """
    if scopes is None:
        scopes = [
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/calendar.events",
        ]

    logger.info("Starting OAuth2 flow")

    # Create client config
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": ["http://localhost:8080"],  # Use consistent port
        }
    }

    try:
        # Create and run flow
        flow = InstalledAppFlow.from_client_config(client_config, scopes=scopes)

        # Run the flow with specific port
        credentials = flow.run_local_server(port=8080)

        # Extract relevant information
        creds_dict = {
            "refresh_token": credentials.refresh_token,
            "token": credentials.token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
        }

        logger.info("Successfully obtained OAuth2 credentials")
        return creds_dict

    except Exception as e:
        logger.error(f"Failed to run OAuth2 flow: {str(e)}")
        raise
