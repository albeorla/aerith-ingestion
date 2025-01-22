"""
ReAct (Reasoning + Acting) implementation.
"""

from typing import Any, Dict, List, Tuple

from .base import BaseAgent, Tool


class ReActAgent(BaseAgent):
    """
    An agent that implements the ReAct pattern by alternating between
    reasoning about the current state and taking actions.
    """

    def __init__(self, name: str = "ReAct Agent"):
        super().__init__(name)
        self.max_steps = 10  # Maximum number of think-act cycles
        self.available_tools: Dict[str, Tool] = {}

    def add_tool(self, tool: Tool):
        """Add a tool that the agent can use."""
        self.available_tools[tool.name] = tool

    def think(self, input_data: Dict[str, Any]) -> List[str]:
        """
        Generate thoughts about the current state and potential actions.
        """
        thoughts = []
        current_state = input_data.get("state", {})
        goal = input_data.get("goal", "")

        # Initial thought about the goal
        thoughts.append(f"Goal: {goal}")
        thoughts.append(f"Current state: {current_state}")

        # Consider available tools
        tool_thoughts = self._think_about_tools()
        thoughts.extend(tool_thoughts)

        # Plan next action
        action_plan = self._plan_next_action(current_state, goal)
        thoughts.append(f"Planned action: {action_plan}")

        return thoughts

    def act(self, thoughts: List[str]) -> Dict[str, Any]:
        """
        Take action based on the reasoning process.
        """
        # Extract the planned action from thoughts
        action_thought = thoughts[-1]

        # Parse the action and execute it
        tool_name, params = self._parse_action(action_thought)

        if tool_name in self.available_tools:
            tool = self.available_tools[tool_name]
            try:
                result = tool.execute(params)
                success = True
            except Exception as e:
                result = str(e)
                success = False
        else:
            result = f"Tool {tool_name} not found"
            success = False

        return {
            "action_taken": action_thought,
            "result": result,
            "success": success,
            "thoughts": thoughts,
        }

    def _think_about_tools(self) -> List[str]:
        """Generate thoughts about available tools and their applicability."""
        thoughts = []
        if not self.available_tools:
            thoughts.append("No tools available")
            return thoughts

        thoughts.append("Available tools:")
        for name, tool in self.available_tools.items():
            thoughts.append(f"- {name}: {tool.description}")

        return thoughts

    def _plan_next_action(self, state: Dict[str, Any], goal: str) -> str:
        """Plan the next action based on current state and goal."""
        # In practice, this would involve more sophisticated planning,
        # possibly using LLMs or other planning algorithms
        if not self.available_tools:
            return "No actions available"

        # Simple planning: pick the first available tool
        tool_name = next(iter(self.available_tools))
        return f"Use {tool_name} to progress toward goal: {goal}"

    def _parse_action(self, action_thought: str) -> Tuple[str, Dict[str, Any]]:
        """Parse an action thought into tool name and parameters."""
        # Simple parsing - in practice, this would be more sophisticated
        parts = action_thought.split()
        if len(parts) < 2 or parts[0] != "Use":
            return "no_tool", {}

        tool_name = parts[1]
        # Extract parameters from the rest of the thought
        params = {"goal": " ".join(parts[4:])}

        return tool_name, params

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Override the base process method to implement the ReAct loop.
        """
        results = []
        state = input_data.copy()

        for step in range(self.max_steps):
            # Think
            thoughts = self.think(state)

            # Act
            action_result = self.act(thoughts)
            results.append(action_result)

            # Update state
            state["previous_action"] = action_result

            # Check if goal is achieved
            if self._check_goal_achieved(state, input_data.get("goal", "")):
                break

        return {
            "steps": results,
            "final_state": state,
            "num_steps": len(results),
        }

    def _check_goal_achieved(self, state: Dict[str, Any], goal: str) -> bool:
        """Check if the goal has been achieved."""
        # In practice, this would involve more sophisticated goal checking
        return state.get("previous_action", {}).get("success", False)
