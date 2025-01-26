# Features & Development Tracking

## High Priority (p0)

| Feature                                     | Status       | Epic       | User Story                                                                                                                                                              | Dependencies                                  | Rationale                                                                                                 | Requirements Traceability |
| :------------------------------------------ | :----------- | :--------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------- | :-------------------------------------------------------------------------------------------------------- | :------------------------ |
| SoMinE Core Logic Implementation            | Not Started  | Core Agent | **As an AI engineer,** I want to embed the SoMinE (Socratic & Minimally-Elicited) four-step approach, so that each request proceeds through (1) Socratic Inquiry, (2) Minimal Instruction, (3) Reflection, (4) Final Answer. | None                                          | Core differentiator, enables advanced agent capabilities.                                             | FR-06, FR-07              |
| Base Agent & Society-of-Mind                | Not Started  | Core Agent | **As a developer,** I want a `BaseAgent` class plus sub-agents that can collaborate (Society of Mind), so that specialized agents can share information and handle complex tasks. | None                                          | Enables modularity, extensibility, and complex task handling.                                          | FR-07                     |
| Google Calendar Integration                 | Not Started  | External   | **As a user,** I want the system to read from and write to Google Calendar, so that tasks and events remain up-to-date in one place.                                    | None                                          | Key user requirement, enhances task management capabilities.                                            | FR-01, FR-04              |
| Next.js Dashboard                           | Not Started  | UI         | **As a user,** I want a web-based dashboard to interact with the system, so that I can easily view and manage tasks.                                                     | D2, D4 (Stable API endpoints)                 | Improves user experience, provides a visual interface for task management.                               | N/A                       |
| Comprehensive Testing (Unit & Integration) | In Progress | Testing    | **As a developer,** I want comprehensive unit and integration tests, so that I can ensure code quality and prevent regressions.                                        | B1, B2, D2                                    | Improves code quality, reduces bugs, and ensures stability.                                             | NFR-01, NFR-02            |
| Enhanced Error Handling                     | Not Started  | Technical Debt | **As a developer,** I want a robust error handling strategy, so that the system can gracefully handle unexpected situations and provide informative error messages. | None                                          | Improves system reliability and user experience.                                                       | NFR-04                    |

## Medium Priority (p1)

| Feature                               | Status       | Epic          | User Story                                                                                                                                 | Dependencies          | Rationale                                                                       | Requirements Traceability |
| :------------------------------------ | :----------- | :------------ | :----------------------------------------------------------------------------------------------------------------------------------------- | :-------------------- | :------------------------------------------------------------------------------ | :------------------------ |
| Tree of Thoughts Implementation       | Not Started  | Core Agent    | **As an AI engineer,** I want to implement the Tree of Thoughts algorithm, so that the agent can explore multiple reasoning paths.          | B1, B2                | Enhances agent reasoning capabilities, improves decision-making.                | FR-06                     |
| Enhanced Reflection System            | Not Started  | Core Agent    | **As an AI engineer,** I want to enhance the agent's reflection capabilities, so that it can better learn from its experiences.             | B1, B2                | Improves agent learning and adaptation.                                         | FR-06                     |
| Chain-of-Thought Agent                | Not Started  | Method        | **As an AI engineer,** I want to implement a Chain-of-Thought agent, so that the agent can reason through a series of steps.                | None                  | Provides a structured approach to reasoning.                                    | FR-06                     |
| ReAct Agent                           | Not Started  | Method        | **As an AI engineer,** I want to implement a ReAct agent, so that the agent can combine reasoning and acting.                             | None                  | Enables the agent to interact with the environment and take actions.             | FR-06                     |
| Multi-Armed Bandit Integration        | Not Started  | Method        | **As an AI engineer,** I want to integrate the Multi-Armed Bandit algorithm, so that the agent can optimize its actions over time.         | At least two agents | Enables the agent to learn and adapt its behavior based on rewards.             | FR-06                     |
| RAG API Implementation                | Not Started  | External      | **As a developer,** I want to implement a RAG API, so that the agent can access and retrieve information from external knowledge sources. | D2, D3 (Stable APIs) | Enhances agent knowledge and reasoning capabilities.                            | N/A                       |
| Agent Management UI                   | Not Started  | UI            | **As a user,** I want to be able to manage the agents, so that I can configure their behavior and monitor their performance.                | B1, B2                | Improves user experience, provides control over agent behavior.                 | N/A                       |
| Task/Event Editing Interface          | Not Started  | UI            | **As a user,** I want to be able to edit tasks and events, so that I can update their details and manage them effectively.                 | D4, E1                | Improves user experience, provides more control over task and event management. | N/A                       |
| Enhanced Documentation                | Not Started  | Technical Debt | **As a developer,** I want comprehensive documentation, so that I can easily understand and use the system.                               | None                  | Improves code maintainability and developer onboarding.                          | N/A                       |

## ✅ Completed Features (Sorted by Component)

### Data Management

-   [x] **Task Ingestion & Validation**
    -   [x] JSON schema validation
    -   [x] Local storage implementation
    -   [x] Task manager
    -   [x] Ingestion pipeline

### DevOps & Infrastructure

-   [x] **AWS ECS Deployment**
-   [x] **CI/CD Pipeline**
-   [x] **Docker & Terraform Setup**
-   [x] **GitHub Actions Workflow**
-   [x] **Environment Management**
-   [x] **Project Structure & Poetry Dependencies**
-   [x] **Basic Repository Layout**

### External APIs

-   [x] **Todoist Integration (One-way)**
    -   [x] API client
    -   [x] Task model implementation
    -   [x] Sync functionality

## Deprecated Features

-   Bi-directional Sync (Moved to Parking Lot due to complexity and lower priority) 