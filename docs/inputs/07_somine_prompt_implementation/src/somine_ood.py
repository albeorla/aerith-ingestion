from abc import ABC, abstractmethod
from typing import Any, Dict


class SoMinEStep(ABC):
    """Abstract base class for SoMinE algorithm steps."""

    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """Execute the step and return its output."""
        pass


class SocraticInquiry(SoMinEStep):
    """Class for the Socratic Inquiry step."""

    def __init__(self, context: str):
        self.context = context

    def execute(self) -> Dict[str, Any]:
        """Ask clarifying questions to fully understand the problem."""
        questions = [
            "What specific details or background information are necessary to comprehend the issue at hand?",
            "Are there any assumptions or constraints that need to be clarified?",
            "What is the desired outcome of the solution?",
        ]
        return {"context": self.context, "questions": questions}


class MinimallyElicitedInstruction(SoMinEStep):
    """Class for the Minimally Elicited Instruction step."""

    def __init__(self, context_analysis: Dict[str, Any]):
        self.context_analysis = context_analysis

    def execute(self) -> Dict[str, Any]:
        """Provide concise and precise instructions to resolve the problem."""
        instructions = [
            "Identify the core elements of the problem.",
            "Outline a step-by-step approach to address the issue.",
            "Ensure the solution aligns with the desired outcome.",
        ]
        return {
            "context_analysis": self.context_analysis,
            "instructions": instructions,
        }


class Reflection(SoMinEStep):
    """Class for the Reflection step."""

    def __init__(self, context_instructions: Dict[str, Any]):
        self.context_instructions = context_instructions

    def execute(self) -> Dict[str, Any]:
        """Reflect on insights, challenges, and factors influencing the solution."""
        reflections = {
            "challenges": [
                "What potential obstacles might arise during implementation?",
                "Are there alternative approaches to consider?",
            ],
            "insights": "Prioritize the most effective and efficient approach to solve the problem.",
        }
        return {
            "context_instructions": self.context_instructions,
            "reflections": reflections,
        }


class FinalAnswer(SoMinEStep):
    """Class for the Final Answer step."""

    def __init__(self, reflection_output: Dict[str, Any]):
        self.reflection_output = reflection_output

    def execute(self) -> Dict[str, Any]:
        """Formulate a comprehensive solution based on all prior steps."""
        solution = {
            "summary": "Use the insights gained to implement the solution step-by-step.",
            "details": "Each step should be tested and validated to ensure correctness and feasibility.",
        }
        return {
            "reflection_output": self.reflection_output,
            "solution": solution,
        }


class SoMinEAlgorithm:
    """High-level orchestrator class to implement the SoMinE_Prompt workflow."""

    def __init__(self, context: str):
        self.context = context

    def execute(self) -> Dict[str, Any]:
        """Execute the complete SoMinE algorithm workflow."""
        # Step 1: Socratic Inquiry
        inquiry = SocraticInquiry(self.context)
        inquiry_output = inquiry.execute()

        # Step 2: Minimally Elicited Instruction
        instruction = MinimallyElicitedInstruction(inquiry_output)
        instruction_output = instruction.execute()

        # Step 3: Reflection
        reflection = Reflection(instruction_output)
        reflection_output = reflection.execute()

        # Step 4: Final Answer
        final_answer = FinalAnswer(reflection_output)
        solution = final_answer.execute()

        return solution
