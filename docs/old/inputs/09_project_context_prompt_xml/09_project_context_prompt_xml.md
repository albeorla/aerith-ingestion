# Project Context Prompt XML

This document outlines the project structure and context for the Todoist and Google Calendar Sync with Agent Integration project. The XML structure is stored in the `code/project_context.xml` file.

## Project Overview

- **Name**: Todoist and Google Calendar Sync with Agent Integration
- **Description**: A bidirectional sync system between Todoist, Google Calendar, and a custom agent library, featuring a Next.js UI for task and event management.

## Project Goals

1. Implement bidirectional sync between Todoist and Google Calendar
2. Integrate a remote RAG API for context-aware agent interactions
3. Build a library of agents with advanced configurations (e.g., SoMinE chain of thought)
4. Develop a Next.js UI for managing tasks, calendar events, and agent interactions

## Codebase Structure

### Backend (albeorla-aerith-aerith-ingestion)
- Core Python package for task management and API integration
- Docker and Terraform configurations for deployment
- GitHub Actions workflow for AWS ECS deployment

### Frontend (albeorla-rbac-dashboard)
- Next.js application with TypeScript
- Chakra UI and Tailwind CSS for styling
- Component-based architecture with role management

## Next Steps

1. **API Integration**
   - Integrate Todoist and Google Calendar APIs with the Next.js UI
   - Implement bidirectional sync logic in the backend

2. **Agent Integration**
   - Set up the RAG API for context-aware agent interactions
   - Build a library of agents with advanced configurations

3. **UI and Deployment**
   - Enhance the UI with real-time updates and notifications
   - Deploy the system using Docker and AWS ECS

## Technical Notes

- UI built using Next.js, Chakra UI, and Tailwind CSS
- Backend uses Python with Docker and Terraform for deployment
- State management store for users, roles, and permissions
- RAG API integration for context-aware agent responses

## Implementation Guide

To continue working on the project:
1. Add new features to the UI by editing the Next.js components
2. Enhance the backend sync logic by modifying the Python code
3. Integrate additional APIs or services as needed
4. Update the deployment configuration for AWS ECS

For the complete XML structure and detailed specifications, see `code/project_context.xml`.