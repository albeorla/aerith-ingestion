"""
ReAct (Reasoning + Acting) Agent Implementation

This module implements a ReAct agent that interleaves reasoning steps with actions,
allowing for dynamic decision-making based on real-time feedback.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List


class StepType(Enum):
    THOUGHT = auto()
    ACTION = auto()
    OBSERVATION = auto()


@dataclass
class Step:
    """Represents a single step in the ReAct process."""

    type: StepType
    content: str


class ReActAgent:
    """
    A ReAct agent that interleaves reasoning steps with actions.
    Each 'act' can be an API call, user interaction, or environment feedback.
    """

    def __init__(self, name: str = "ReActAgent"):
        self.name = name
        self.steps: List[Step] = []
        self.max_steps = 10  # Prevent infinite loops

    def engage(self, task: str) -> str:
        """
        Public method to engage with a task. The agent will alternate
        between reasoning about the task and taking actions.

        Args:
            task (str): The task to accomplish.

        Returns:
            str: The final result after completing the task.
        """
        self.steps.clear()

        # Initial thought about the task
        self._add_thought(f"Analyzing task: {task}")

        while not self._is_task_complete() and len(self.steps) < self.max_steps:
            # Think about what to do next
            next_action = self._plan_next_action(task)
            self._add_thought(f"Planning next action: {next_action}")

            # Take the action
            result = self._take_action(next_action)
            self._add_action(next_action)

            # Observe the result
            self._add_observation(f"Observed: {result}")

        return self._format_response()

    def _add_thought(self, thought: str):
        """Records a thinking step."""
        self.steps.append(Step(StepType.THOUGHT, thought))

    def _add_action(self, action: str):
        """Records an action step."""
        self.steps.append(Step(StepType.ACTION, action))

    def _add_observation(self, observation: str):
        """Records an observation step."""
        self.steps.append(Step(StepType.OBSERVATION, observation))

    def _is_task_complete(self) -> bool:
        """
        Determines if the task is complete based on the steps taken.

        Returns:
            bool: True if task is complete, False otherwise.
        """
        # Example implementation: complete if we have at least one of each step type
        step_types = {step.type for step in self.steps}
        return len(step_types) >= len(StepType)

    def _plan_next_action(self, task: str) -> str:
        """
        Plans the next action based on the current state and task.

        Args:
            task (str): The current task.

        Returns:
            str: Description of the next action to take.
        """
        # Example implementation
        if not self.steps:
            return "Initialize task processing"
        return "Continue task execution"

    def _take_action(self, action: str) -> str:
        """
        Executes the planned action and returns the result.

        Args:
            action (str): The action to take.

        Returns:
            str: Result of the action.
        """
        # Example implementation
        return f"Action '{action}' completed successfully"

    def _format_response(self) -> str:
        """
        Formats the complete sequence of steps into a readable response.

        Returns:
            str: Formatted response showing the ReAct process.
        """
        formatted_steps = []
        for step in self.steps:
            prefix = {
                StepType.THOUGHT: "🤔 Thought:",
                StepType.ACTION: "🎯 Action:",
                StepType.OBSERVATION: "👁 Observed:",
            }[step.type]
            formatted_steps.append(f"{prefix} {step.content}")

        return "\n".join(formatted_steps)


if __name__ == "__main__":
    # Example usage
    agent = ReActAgent()
    task = "Plan a trip to Paris"
    print(f"Task: {task}\n")
    result = agent.engage(task)
    print("\nReAct Process:")
    print(result)
