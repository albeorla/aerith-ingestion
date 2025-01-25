"""
Tool-Use Enhanced Agent implementation.
"""

from typing import Any, Dict, List, Optional

from .base import BaseAgent, Tool


class ToolRegistry:
    """Registry for managing available tools."""

    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        """Register a new tool."""
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        """List all available tool names."""
        return list(self.tools.keys())

    def get_descriptions(self) -> Dict[str, str]:
        """Get descriptions of all tools."""
        return {name: tool.description for name, tool in self.tools.items()}


class ToolEnhancedAgent(BaseAgent):
    """
    An agent that can use various tools to enhance its capabilities.
    """

    def __init__(self, name: str = "Tool-Enhanced Agent"):
        super().__init__(name)
        self.tool_registry = ToolRegistry()
        self.max_tool_attempts = 3
        self.tool_history: List[Dict[str, Any]] = []

    def register_tool(self, tool: Tool):
        """Register a new tool for the agent to use."""
        self.tool_registry.register(tool)

    def think(self, input_data: Dict[str, Any]) -> List[str]:
        """
        Generate thoughts about which tools to use and how to use them.
        """
        thoughts = []

        # Understand the task
        task = input_data.get("task", "")
        thoughts.append(f"Understanding task: {task}")

        # Consider available tools
        tools = self.tool_registry.get_descriptions()
        thoughts.append("Available tools:")
        for name, description in tools.items():
            thoughts.append(f"- {name}: {description}")

        # Plan tool usage
        tool_plan = self._plan_tool_usage(task, tools)
        thoughts.extend(tool_plan)

        return thoughts

    def act(self, thoughts: List[str]) -> Dict[str, Any]:
        """
        Execute the tool usage plan.
        """
        results = []
        success = True
        error = None

        try:
            # Extract tool usage plan from thoughts
            tool_sequence = self._extract_tool_sequence(thoughts)

            # Execute each tool in sequence
            for tool_name, params in tool_sequence:
                tool = self.tool_registry.get_tool(tool_name)
                if tool:
                    result = self._execute_tool_safely(tool, params)
                    results.append(
                        {"tool": tool_name, "params": params, "result": result}
                    )
                else:
                    success = False
                    error = f"Tool not found: {tool_name}"
                    break

        except Exception as e:
            success = False
            error = str(e)

        # Record tool usage history
        self.tool_history.extend(results)

        return {
            "success": success,
            "results": results,
            "error": error,
            "thoughts": thoughts,
        }

    def _plan_tool_usage(self, task: str, tools: Dict[str, str]) -> List[str]:
        """Plan how to use available tools to accomplish the task."""
        thoughts = []

        # Analyze task requirements
        thoughts.append("Analyzing task requirements...")

        # Match tools to requirements
        thoughts.append("Matching tools to requirements:")
        for name, description in tools.items():
            relevance = self._assess_tool_relevance(task, name, description)
            thoughts.append(f"- {name}: Relevance = {relevance}")

        # Create execution plan
        thoughts.append("Tool execution plan:")
        plan = self._create_tool_execution_plan(task, tools)
        thoughts.extend([f"  {step}" for step in plan])

        return thoughts

    def _assess_tool_relevance(
        self, task: str, tool_name: str, tool_description: str
    ) -> float:
        """Assess how relevant a tool is for the given task."""
        # In practice, this would use more sophisticated relevance assessment
        # possibly using semantic similarity or ML-based matching
        if any(word in tool_description.lower() for word in task.lower().split()):
            return 0.8
        return 0.2

    def _create_tool_execution_plan(
        self, task: str, tools: Dict[str, str]
    ) -> List[str]:
        """Create a plan for tool execution."""
        # In practice, this would use more sophisticated planning
        plan = []
        for name in tools:
            plan.append(f"Step: Use {name} to process task")
        return plan

    def _extract_tool_sequence(
        self, thoughts: List[str]
    ) -> List[tuple[str, Dict[str, Any]]]:
        """Extract tool sequence from thoughts."""
        sequence = []
        for thought in thoughts:
            if thought.startswith("Step: Use"):
                # Parse tool name and create basic parameters
                parts = thought.split()
                tool_name = parts[2]
                sequence.append((tool_name, {"task": " ".join(parts[4:])}))
        return sequence

    def _execute_tool_safely(self, tool: Tool, params: Dict[str, Any]) -> Any:
        """Execute a tool with safety checks and retries."""
        attempts = 0
        last_error = None

        while attempts < self.max_tool_attempts:
            try:
                return tool.execute(params)
            except Exception as e:
                last_error = e
                attempts += 1

        raise Exception(
            f"Tool execution failed after {attempts} attempts: {last_error}"
        )


# Example tool implementations


class WebSearchTool(Tool):
    """A tool for performing web searches."""

    def __init__(self):
        super().__init__(
            name="web_search",
            description="Perform web searches to gather information",
        )

    def execute(self, params: Dict[str, Any]) -> Any:
        # Implement actual web search logic
        query = params.get("query", "")
        return f"Web search results for: {query}"


class CalculatorTool(Tool):
    """A tool for performing calculations."""

    def __init__(self):
        super().__init__(
            name="calculator", description="Perform mathematical calculations"
        )

    def execute(self, params: Dict[str, Any]) -> Any:
        # Implement actual calculation logic
        expression = params.get("expression", "")
        try:
            return eval(expression)  # Note: eval is used for demonstration only
        except Exception as e:
            return f"Error calculating {expression}: {str(e)}"
