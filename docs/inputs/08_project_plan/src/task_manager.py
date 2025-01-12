from datetime import datetime
from typing import Any, Dict, Optional

from .calendar_api import GoogleCalendarAPI
from .todoist_api import TodoistAPI


class TaskManager:
    def __init__(self):
        self.calendar_api = GoogleCalendarAPI()
        self.todoist_api = TodoistAPI()

    def sync_task_to_calendar(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Sync a Todoist task to Google Calendar."""
        event_data = self._convert_task_to_event(task)
        try:
            return self.calendar_api.create_event(event_data)
        except Exception as e:
            print(f"Error syncing task to calendar: {e}")
            return None

    def sync_event_to_todoist(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Sync a Google Calendar event to Todoist."""
        task_data = self._convert_event_to_task(event)
        try:
            return self.todoist_api.create_task(task_data)
        except Exception as e:
            print(f"Error syncing event to Todoist: {e}")
            return None

    def _convert_task_to_event(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Todoist task format to Google Calendar event format."""
        return {
            "summary": task.get("content"),
            "description": task.get("description", ""),
            "start": {
                "dateTime": task.get("due", {}).get("date"),
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": task.get("due", {}).get("date"),
                "timeZone": "UTC",
            },
        }

    def _convert_event_to_task(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Google Calendar event format to Todoist task format."""
        return {
            "content": event.get("summary", ""),
            "description": event.get("description", ""),
            "due_datetime": event.get("start", {}).get("dateTime"),
        }

    def resolve_conflict(
        self, task: Dict[str, Any], event: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve conflicts between Todoist task and Google Calendar event."""
        task_updated = datetime.fromisoformat(task.get("date_modified", ""))
        event_updated = datetime.fromisoformat(event.get("updated", ""))

        return task if task_updated > event_updated else event

    def sync_all(self):
        """Perform a full sync between Todoist and Google Calendar."""
        tasks = self.todoist_api.get_tasks()
        events = self.calendar_api.fetch_events()

        # Create a mapping of linked items
        task_event_map = {}

        # Sync new tasks to calendar
        for task in tasks:
            if not task.get("calendar_event_id"):
                event = self.sync_task_to_calendar(task)
                if event:
                    task_event_map[task["id"]] = event["id"]

        # Sync new events to Todoist
        for event in events:
            if not event.get("todoist_task_id"):
                task = self.sync_event_to_todoist(event)
                if task:
                    task_event_map[event["id"]] = task["id"]
