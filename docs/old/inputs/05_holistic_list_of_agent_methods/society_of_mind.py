"""
Society of Mind Implementation

This module implements a simplified version of Marvin Minsky's Society of Mind concept,
where multiple specialized sub-agents work together to solve complex tasks.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, List


class Specialty(Enum):
    """Defines different types of agent specialties."""

    MATH = auto()
    LANGUAGE = auto()
    LOGIC = auto()
    MEMORY = auto()
    PLANNING = auto()


@dataclass
class SubAgent:
    """
    Represents a specialized agent within the society.
    Each sub-agent has a specific capability and role.
    """

    name: str
    specialty: Specialty
    solve_func: Callable[[str], str]
    confidence_threshold: float = 0.7

    def can_handle(self, task: str) -> bool:
        """
        Determines if this sub-agent can handle a given task.

        Args:
            task (str): The task to evaluate.

        Returns:
            bool: True if the agent can handle the task.
        """
        # Example implementation - in practice, this would be more sophisticated
        specialty_keywords = {
            Specialty.MATH: ["calculate", "compute", "solve", "number"],
            Specialty.LANGUAGE: ["explain", "describe", "write", "translate"],
            Specialty.LOGIC: ["reason", "deduce", "analyze", "if", "then"],
            Specialty.MEMORY: ["recall", "remember", "store", "retrieve"],
            Specialty.PLANNING: ["plan", "organize", "schedule", "arrange"],
        }

        keywords = specialty_keywords[self.specialty]
        return any(keyword in task.lower() for keyword in keywords)

    def solve(self, task: str) -> str:
        """
        Attempts to solve the given task using the agent's specialty.

        Args:
            task (str): The task to solve.

        Returns:
            str: The solution or response from this sub-agent.
        """
        if not self.can_handle(task):
            return f"[{self.name}] Cannot confidently handle: {task}"
        return self.solve_func(task)


class SocietyOfMind:
    """
    Manages a collection of specialized sub-agents that work together
    to solve complex problems through collaboration.
    """

    def __init__(self, name: str = "SoMManager"):
        self.name = name
        self.subagents: List[SubAgent] = []
        self.solution_history: List[str] = []

    def add_subagent(self, subagent: SubAgent):
        """
        Adds a new sub-agent to the society.

        Args:
            subagent (SubAgent): The sub-agent to add.
        """
        self.subagents.append(subagent)

    def solve_complex_task(self, task: str) -> str:
        """
        Orchestrates sub-agents to solve a complex task cooperatively.

        Args:
            task (str): The complex task to solve.

        Returns:
            str: The combined solution from all relevant sub-agents.
        """
        self.solution_history.clear()
        self._log(f"Received task: {task}")

        # Find capable agents
        capable_agents = [agent for agent in self.subagents if agent.can_handle(task)]

        if not capable_agents:
            return f"No agents available to handle task: {task}"

        # Collect solutions from capable agents
        solutions = []
        for agent in capable_agents:
            solution = agent.solve(task)
            self._log(f"Agent {agent.name} ({agent.specialty.name}): {solution}")
            solutions.append(solution)

        # Combine solutions
        final_solution = self._synthesize_solutions(solutions)
        self._log(f"Final synthesized solution: {final_solution}")

        return self._format_response()

    def _synthesize_solutions(self, solutions: List[str]) -> str:
        """
        Combines multiple solutions into a coherent final answer.

        Args:
            solutions (List[str]): Individual solutions to combine.

        Returns:
            str: Synthesized solution.
        """
        return " | ".join(solutions)

    def _log(self, message: str):
        """Records a step in the solution process."""
        self.solution_history.append(message)

    def _format_response(self) -> str:
        """
        Formats the complete solution history into a readable response.

        Returns:
            str: Formatted solution history.
        """
        return "\n".join(self.solution_history)


def example_math_solver(task: str) -> str:
    return f"Math solution for: {task}"


def example_language_solver(task: str) -> str:
    return f"Language analysis of: {task}"


def example_logic_solver(task: str) -> str:
    return f"Logical deduction for: {task}"


if __name__ == "__main__":
    # Create example sub-agents
    math_agent = SubAgent(
        name="MathMaster",
        specialty=Specialty.MATH,
        solve_func=example_math_solver,
    )

    language_agent = SubAgent(
        name="LanguageExpert",
        specialty=Specialty.LANGUAGE,
        solve_func=example_language_solver,
    )

    logic_agent = SubAgent(
        name="LogicMaster",
        specialty=Specialty.LOGIC,
        solve_func=example_logic_solver,
    )

    # Create society and add agents
    society = SocietyOfMind()
    society.add_subagent(math_agent)
    society.add_subagent(language_agent)
    society.add_subagent(logic_agent)

    # Test with a complex task
    task = "Calculate the area of a circle and explain the formula in simple terms"
    print(f"Complex Task: {task}\n")
    result = society.solve_complex_task(task)
    print("\nSolution Process:")
    print(result)
