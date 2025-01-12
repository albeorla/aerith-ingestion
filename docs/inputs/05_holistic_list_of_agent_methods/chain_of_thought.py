"""
Chain of Thought (CoT) Reasoning Implementation

This module implements a basic Chain-of-Thought (CoT) reasoning mechanism that breaks down
complex problems into manageable components for better problem decomposition and logical reasoning.
"""

from typing import List


class ChainOfThoughtAgent:
    """
    A Chain-of-Thought (CoT) reasoning agent that decomposes complex problems into smaller steps,
    then methodically resolves each step to build up a final answer.
    """

    def __init__(self, name: str = "CoTAgent"):
        self.name = name
        self.thought_chain: List[str] = []

    def reason(self, question: str) -> str:
        """
        Main public method that triggers a chain-of-thought reasoning process.

        Args:
            question (str): The complex question or task for the agent to solve.

        Returns:
            str: The final answer derived via step-by-step reasoning.
        """
        # Clear previous thought chain
        self.thought_chain.clear()

        # Step 1: Break down the question
        subproblems = self._decompose_question(question)
        self.thought_chain.append(f"Breaking down question: {question}")

        # Step 2: Solve each subproblem step-by-step
        solutions = []
        for step_index, sp in enumerate(subproblems, 1):
            thought = self._solve_subproblem(sp, step_index)
            self.thought_chain.append(f"Step {step_index}: {thought}")
            solutions.append(thought)

        # Step 3: Combine the solutions into a final answer
        final_answer = self._combine_solutions(solutions)
        self.thought_chain.append(f"Final answer: {final_answer}")

        return self._format_response()

    def _decompose_question(self, question: str) -> List[str]:
        """
        Splits the question into smaller subproblems.

        Args:
            question (str): The input question to decompose.

        Returns:
            List[str]: List of subproblems.
        """
        # Example heuristic: split by punctuation or keywords
        return [q.strip() for q in question.split(".") if q.strip()]

    def _solve_subproblem(self, subproblem: str, step_index: int) -> str:
        """
        Solves an individual subproblem.

        Args:
            subproblem (str): The subproblem to solve.
            step_index (int): The current step number.

        Returns:
            str: Solution to the subproblem.
        """
        return f"Solving '{subproblem}': Intermediate solution for step {step_index}"

    def _combine_solutions(self, solutions: List[str]) -> str:
        """
        Merges individual subproblem solutions into a single coherent answer.

        Args:
            solutions (List[str]): List of solutions to combine.

        Returns:
            str: Combined solution.
        """
        return " Therefore, ".join(solutions)

    def _format_response(self) -> str:
        """
        Formats the complete thought chain and final answer into a readable response.

        Returns:
            str: Formatted response with thought chain and final answer.
        """
        return "\n".join(self.thought_chain)


if __name__ == "__main__":
    # Example usage
    agent = ChainOfThoughtAgent()
    question = "How many prime numbers are there under 20? Also, which are they?"
    print("Question:", question)
    print("\nReasoning Process:")
    answer = agent.reason(question)
    print(answer)
