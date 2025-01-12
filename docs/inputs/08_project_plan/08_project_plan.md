# Project Plan

This project integrates Todoist and Google Calendar with RAG-powered agents to create a smart task and calendar management system.

## Features

- Bidirectional sync between Todoist and Google Calendar
- RAG-powered intelligent agents for task management
- Multiple specialized agents (Productivity, Scheduling)
- Modern Next.js frontend with RBAC

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and credentials
```

3. Set up Google Calendar API:
- Go to Google Cloud Console
- Create a new project
- Enable Google Calendar API
- Create OAuth 2.0 credentials
- Download credentials.json and place in project root

4. Set up Todoist API:
- Go to Todoist Developer settings
- Create a new app
- Get API token
- Add to .env file

## Development

1. Run the backend:
```bash
poetry run uvicorn main:app --reload
```

2. Run tests:
```bash
poetry run pytest
```

3. Format code:
```bash
poetry run black .
poetry run isort .
```

## Project Structure

```
project_plan/
├── calendar_api.py     # Google Calendar integration
├── todoist_api.py      # Todoist integration
├── task_manager.py     # Sync logic
├── rag_api.py         # RAG integration
├── agent_library.py   # Agent definitions
├── main.py           # FastAPI application
└── tests/           # Test suite
```

## Architecture

1. Backend Services:
   - FastAPI backend
   - Google Calendar API integration
   - Todoist API integration
   - RAG-powered agents

2. Frontend:
   - Next.js dashboard
   - RBAC implementation
   - Real-time updates

3. Deployment:
   - Docker containerization
   - AWS ECS deployment
   - Terraform infrastructure

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT 