from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .agent_library import AgentRegistry
from .calendar_api import GoogleCalendarAPI
from .rag_api import RAGAPI
from .task_manager import TaskManager
from .todoist_api import TodoistAPI

app = FastAPI(title="Task Management API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
calendar_api = GoogleCalendarAPI()
todoist_api = TodoistAPI()
task_manager = TaskManager()
rag_api = RAGAPI()
agent_registry = AgentRegistry()


class TaskCreate(BaseModel):
    content: str
    description: Optional[str] = None
    due_datetime: Optional[datetime] = None


class EventCreate(BaseModel):
    summary: str
    description: Optional[str] = None
    start_datetime: datetime
    end_datetime: datetime


class AgentQuery(BaseModel):
    agent_id: str
    query: str
    context: Optional[Dict[str, Any]] = None


@app.get("/tasks")
async def get_tasks() -> List[Dict[str, Any]]:
    """Get all tasks from Todoist."""
    try:
        return todoist_api.get_tasks()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tasks")
async def create_task(task: TaskCreate) -> Dict[str, Any]:
    """Create a new task in Todoist."""
    try:
        task_data = task.dict()
        created_task = todoist_api.create_task(task_data)
        # Sync to calendar if due date is set
        if task.due_datetime:
            task_manager.sync_task_to_calendar(created_task)
        return created_task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/events")
async def get_events() -> List[Dict[str, Any]]:
    """Get all events from Google Calendar."""
    try:
        return calendar_api.fetch_events()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/events")
async def create_event(event: EventCreate) -> Dict[str, Any]:
    """Create a new event in Google Calendar."""
    try:
        event_data = event.dict()
        created_event = calendar_api.create_event(event_data)
        # Sync to Todoist
        task_manager.sync_event_to_todoist(created_event)
        return created_event
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sync")
async def sync_all() -> Dict[str, str]:
    """Perform a full sync between Todoist and Google Calendar."""
    try:
        task_manager.sync_all()
        return {"status": "success", "message": "Sync completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents")
async def list_agents() -> List[Dict[str, str]]:
    """List all available agents."""
    return agent_registry.list_agents()


@app.post("/agents/query")
async def query_agent(query: AgentQuery) -> Dict[str, Any]:
    """Query a specific agent."""
    try:
        agent = agent_registry.get_agent(query.agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        # Get current context if not provided
        if not query.context:
            tasks = todoist_api.get_tasks()
            events = calendar_api.fetch_events()
            context = rag_api.fetch_context(tasks, events)
        else:
            context = query.context

        return await agent.process(context, query.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
