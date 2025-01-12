from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseAgent(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def process(self, context: Dict[str, Any], query: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        pass


class ProductivityAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Productivity Assistant",
            description="Helps optimize task management and time allocation",
        )

    async def process(self, context: Dict[str, Any], query: str) -> Dict[str, Any]:
        system_prompt = self.get_system_prompt()
        # Implementation for productivity-specific processing
        return {"response": "Productivity agent response", "suggestions": []}

    def get_system_prompt(self) -> str:
        return """You are a productivity assistant focused on helping users optimize their task management and time allocation.
Your goal is to analyze their current tasks and schedule to provide actionable suggestions."""


class SchedulingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Scheduling Assistant",
            description="Helps manage calendar and scheduling conflicts",
        )

    async def process(self, context: Dict[str, Any], query: str) -> Dict[str, Any]:
        system_prompt = self.get_system_prompt()
        # Implementation for scheduling-specific processing
        return {"response": "Scheduling agent response", "suggested_times": []}

    def get_system_prompt(self) -> str:
        return """You are a scheduling assistant focused on helping users manage their calendar effectively.
Your goal is to find optimal meeting times and resolve scheduling conflicts."""


class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        self._register_default_agents()

    def _register_default_agents(self):
        """Register the default set of agents."""
        self.register_agent("productivity", ProductivityAgent())
        self.register_agent("scheduling", SchedulingAgent())

    def register_agent(self, agent_id: str, agent: BaseAgent):
        """Register a new agent."""
        self._agents[agent_id] = agent

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID."""
        return self._agents.get(agent_id)

    def list_agents(self) -> List[Dict[str, str]]:
        """List all registered agents."""
        return [
            {
                "id": agent_id,
                "name": agent.name,
                "description": agent.description,
            }
            for agent_id, agent in self._agents.items()
        ]
