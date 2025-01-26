"""
Base classes and interfaces for the agent implementation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class AgentContext:
    """Context object that holds the current state and environment information."""

    state: Dict[str, Any]
    memory: Dict[str, Any]
    tools: Dict[str, Any]

    def __init__(self):
        self.state = {}
        self.memory = {}
        self.tools = {}


class BaseAgent(ABC):
    """Base class for all agent implementations."""

    def __init__(self, name: str):
        self.name = name
        self.context = AgentContext()

    @abstractmethod
    def think(self, input_data: Dict[str, Any]) -> List[str]:
        """Generate thoughts/reasoning steps about the input."""
        pass

    @abstractmethod
    def act(self, thoughts: List[str]) -> Dict[str, Any]:
        """Take action based on thoughts."""
        pass

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing pipeline: think -> act."""
        thoughts = self.think(input_data)
        return self.act(thoughts)


class Tool:
    """Base class for tools that agents can use."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Any:
        """Execute the tool with given parameters."""
        pass
