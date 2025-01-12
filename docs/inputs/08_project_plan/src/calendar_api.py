import os
import pickle
from typing import Any, Dict, List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class GoogleCalendarAPI:
    SCOPES = ["https://www.googleapis.com/auth/calendar"]

    def __init__(self):
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Handle Google Calendar authentication flow."""
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", self.SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            with open("token.pickle", "wb") as token:
                pickle.dump(self.creds, token)

        self.service = build("calendar", "v3", credentials=self.creds)

    def fetch_events(
        self, time_min=None, time_max=None, max_results=10
    ) -> List[Dict[str, Any]]:
        """Fetch events from Google Calendar."""
        events_result = (
            self.service.events()
            .list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return events_result.get("items", [])

    def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new event in Google Calendar."""
        return (
            self.service.events()
            .insert(calendarId="primary", body=event_data)
            .execute()
        )

    def update_event(self, event_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing event in Google Calendar."""
        return (
            self.service.events()
            .update(calendarId="primary", eventId=event_id, body=event_data)
            .execute()
        )

    def delete_event(self, event_id: str) -> None:
        """Delete an event from Google Calendar."""
        self.service.events().delete(calendarId="primary", eventId=event_id).execute()
