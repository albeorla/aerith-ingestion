"""
Tool-Use Enhanced Agent Implementation

This module implements a Tool-Use Enhanced Agent that can dynamically select and use
various tools (e.g., calculators, search engines, APIs) to solve tasks more effectively.
"""

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional


class ToolCategory(Enum):
    """Categories of available tools."""

    CALCULATOR = auto()
    SEARCH = auto()
    API = auto()
    DATABASE = auto()
    FILE_SYSTEM = auto()


@dataclass
class Tool:
    """Represents a tool that can be used by the agent."""

    name: str
    category: ToolCategory
    description: str
    func: Callable[..., Any]
    required_params: List[str]


class ToolRegistry:
    """
    A registry of available tools that can be used by the agent.
    Tools are organized by category and can be accessed by name.
    """

    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.usage_stats: Dict[str, int] = {}

    def register_tool(self, tool: Tool):
        """
        Registers a new tool in the registry.

        Args:
            tool (Tool): The tool to register.
        """
        self.tools[tool.name] = tool
        self.usage_stats[tool.name] = 0

    def get_tool(self, name: str) -> Optional[Tool]:
        """
        Retrieves a tool by name.

        Args:
            name (str): The name of the tool to retrieve.

        Returns:
            Optional[Tool]: The requested tool, if found.
        """
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        """
        Lists all available tools.

        Returns:
            List[str]: Names of all registered tools.
        """
        return list(self.tools.keys())

    def get_tools_by_category(self, category: ToolCategory) -> List[Tool]:
        """
        Retrieves all tools in a specific category.

        Args:
            category (ToolCategory): The category to filter by.

        Returns:
            List[Tool]: Tools in the specified category.
        """
        return [tool for tool in self.tools.values() if tool.category == category]


class ToolUseAgent:
    """
    An agent that can use various tools to solve tasks more effectively.
    The agent can select appropriate tools based on the task and combine
    their outputs for comprehensive solutions.
    """

    def __init__(self, name: str, registry: ToolRegistry):
        self.name = name
        self.registry = registry
        self.execution_history: List[str] = []

    def solve_task(self, task: str, **kwargs: Any) -> str:
        """
        Solves a task using available tools.

        Args:
            task (str): The task to solve.
            **kwargs: Additional parameters that might be needed by tools.

        Returns:
            str: The solution to the task.
        """
        self.execution_history.clear()
        self._log(f"Received task: {task}")

        # Identify required tools
        required_tools = self._identify_required_tools(task)
        if not required_tools:
            return f"No suitable tools found for task: {task}"

        # Execute tools in sequence
        results = []
        for tool_name in required_tools:
            tool = self.registry.get_tool(tool_name)
            if tool:
                try:
                    result = self._execute_tool(tool, task, **kwargs)
                    results.append(result)
                    self._log(f"Tool '{tool_name}' output: {result}")
                except Exception as e:
                    self._log(f"Error using tool '{tool_name}': {str(e)}")

        # Combine results
        final_result = self._combine_results(results)
        self._log(f"Final combined result: {final_result}")

        return self._format_response()

    def _identify_required_tools(self, task: str) -> List[str]:
        """
        Determines which tools are needed for a given task.

        Args:
            task (str): The task to analyze.

        Returns:
            List[str]: Names of required tools.
        """
        required_tools = []

        # Example pattern matching - in practice, use more sophisticated NLP
        patterns = {
            "calculator": r"calculate|compute|sum|multiply|divide",
            "search": r"search|find|lookup|query",
            "api": r"api|fetch|request|call",
            "database": r"database|db|store|retrieve",
            "file": r"file|read|write|save",
        }

        for tool_name, pattern in patterns.items():
            if re.search(pattern, task.lower()):
                required_tools.append(tool_name)

        return required_tools

    def _execute_tool(self, tool: Tool, task: str, **kwargs: Any) -> Any:
        """
        Executes a specific tool with given parameters.

        Args:
            tool (Tool): The tool to execute.
            task (str): The current task.
            **kwargs: Additional parameters for the tool.

        Returns:
            Any: The tool's output.
        """
        # Extract required parameters from kwargs
        tool_params = {
            param: kwargs.get(param)
            for param in tool.required_params
            if param in kwargs
        }

        return tool.func(task, **tool_params)

    def _combine_results(self, results: List[Any]) -> str:
        """
        Combines multiple tool outputs into a final result.

        Args:
            results (List[Any]): Individual tool results to combine.

        Returns:
            str: Combined result.
        """
        # Simple combination - in practice, use more sophisticated methods
        return "\n".join(str(result) for result in results)

    def _log(self, message: str):
        """Records a step in the execution history."""
        self.execution_history.append(message)

    def _format_response(self) -> str:
        """
        Formats the complete execution history into a readable response.

        Returns:
            str: Formatted execution history.
        """
        return "\n".join(self.execution_history)


def example_calculator(task: str, **kwargs: Any) -> str:
    """Example calculator tool implementation."""
    return f"Calculated result for: {task}"


def example_search(task: str, **kwargs: Any) -> str:
    """Example search tool implementation."""
    return f"Search results for: {task}"


def example_api_call(task: str, **kwargs: Any) -> str:
    """Example API tool implementation."""
    return f"API response for: {task}"


if __name__ == "__main__":
    # Create and populate registry
    registry = ToolRegistry()

    # Register some example tools
    calculator_tool = Tool(
        name="calculator",
        category=ToolCategory.CALCULATOR,
        description="Performs mathematical calculations",
        func=example_calculator,
        required_params=["expression"],
    )

    search_tool = Tool(
        name="search",
        category=ToolCategory.SEARCH,
        description="Searches for information",
        func=example_search,
        required_params=["query"],
    )

    api_tool = Tool(
        name="api",
        category=ToolCategory.API,
        description="Makes API calls",
        func=example_api_call,
        required_params=["endpoint", "method"],
    )

    registry.register_tool(calculator_tool)
    registry.register_tool(search_tool)
    registry.register_tool(api_tool)

    # Create agent and test
    agent = ToolUseAgent("ToolMaster", registry)
    task = "Calculate the sum of 5 and 3, then search for information about the result"
    print(f"Task: {task}\n")
    result = agent.solve_task(
        task,
        expression="5 + 3",
        query="number 8",
        endpoint="/data",
        method="GET",
    )
    print("\nExecution Process:")
    print(result)
