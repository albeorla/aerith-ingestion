"""
SoMinE (Society of Mind-Inspired Engineering) Prompt Implementation

This module implements the SoMinE Prompt framework that incorporates sub-processes
for inquiry, elicitation, reflection, and integration.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional


class PromptPhase(Enum):
    """Defines the different phases of the SoMinE process."""

    SOCRATIC_INQUIRY = auto()
    MINIMAL_ELICITATION = auto()
    REFLECTION = auto()
    FINAL_ANSWER = auto()


@dataclass
class PromptStep:
    """Represents a single step in the SoMinE process."""

    phase: PromptPhase
    content: str


class SoMinEPrompt:
    """
    Implements the SoMinE Prompt framework with four main phases:
    1. Socratic Inquiry: Asking clarifying questions
    2. Minimal Elicitation: Concise instructions based on context
    3. Reflection: Analytical review
    4. Final Answer: Comprehensive solution
    """

    def __init__(self, context: str):
        self.context = context
        self.steps: List[PromptStep] = []
        self._current_phase: Optional[PromptPhase] = None

    def process(self) -> str:
        """
        Executes the complete SoMinE process on the given context.

        Returns:
            str: The final processed result.
        """
        self.steps.clear()

        # Phase 1: Socratic Inquiry
        self._current_phase = PromptPhase.SOCRATIC_INQUIRY
        questions = self._generate_socratic_questions()
        self._add_step(f"Socratic Questions:\n{questions}")

        # Phase 2: Minimal Elicitation
        self._current_phase = PromptPhase.MINIMAL_ELICITATION
        instructions = self._generate_minimal_instructions()
        self._add_step(f"Minimal Instructions:\n{instructions}")

        # Phase 3: Reflection
        self._current_phase = PromptPhase.REFLECTION
        reflection = self._reflect_on_process()
        self._add_step(f"Reflection:\n{reflection}")

        # Phase 4: Final Answer
        self._current_phase = PromptPhase.FINAL_ANSWER
        final_answer = self._generate_final_answer()
        self._add_step(f"Final Answer:\n{final_answer}")

        return self._format_response()

    def _generate_socratic_questions(self) -> str:
        """
        Generates clarifying questions about the context.

        Returns:
            str: A set of relevant questions.
        """
        questions = [
            f"What are the key assumptions in '{self.context}'?",
            "What information might be missing?",
            "What constraints should we consider?",
            "What are the potential edge cases?",
        ]
        return "\n".join(f"- {q}" for q in questions)

    def _generate_minimal_instructions(self) -> str:
        """
        Creates concise instructions based on the context.

        Returns:
            str: Minimal set of instructions.
        """
        return (
            f"1. Parse the context: '{self.context}'\n"
            "2. Identify core requirements\n"
            "3. Plan minimal steps needed\n"
            "4. Execute with precision"
        )

    def _reflect_on_process(self) -> str:
        """
        Reviews the process and identifies insights or challenges.

        Returns:
            str: Reflection on the process.
        """
        return (
            "Analysis of approach:\n"
            "- Questions raised key considerations\n"
            "- Instructions focused on core needs\n"
            "- Process remained minimal yet thorough"
        )

    def _generate_final_answer(self) -> str:
        """
        Synthesizes all steps into a comprehensive solution.

        Returns:
            str: The final answer.
        """
        return (
            f"Based on the analysis of '{self.context}':\n"
            "1. Key insights were identified through questioning\n"
            "2. Core requirements were distilled\n"
            "3. Process was reviewed for completeness\n"
            "4. Solution addresses all major points"
        )

    def _add_step(self, content: str):
        """
        Adds a new step to the process history.

        Args:
            content (str): The content of the step.
        """
        if self._current_phase:
            self.steps.append(PromptStep(self._current_phase, content))

    def _format_response(self) -> str:
        """
        Formats the complete process into a readable response.

        Returns:
            str: Formatted response showing the SoMinE process.
        """
        formatted_steps = []
        for step in self.steps:
            phase_name = step.phase.name.replace("_", " ").title()
            formatted_steps.append(f"\n=== {phase_name} ===\n{step.content}")

        return "\n".join(formatted_steps)


if __name__ == "__main__":
    # Example usage
    context = "Design a user authentication system for a web application"
    prompt = SoMinEPrompt(context)
    print(f"Context: {context}\n")
    result = prompt.process()
    print("SoMinE Process:")
    print(result)
