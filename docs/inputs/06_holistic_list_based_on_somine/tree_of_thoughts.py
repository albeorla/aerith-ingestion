"""
Tree of Thoughts implementation for exploring multiple reasoning paths.
"""

from dataclasses import dataclass
from queue import PriorityQueue
from typing import List, Optional


@dataclass
class Thought:
    content: str
    score: float
    parent: Optional["Thought"] = None
    children: List["Thought"] = None

    def __init__(self, content: str, score: float, parent: Optional["Thought"] = None):
        self.content = content
        self.score = score
        self.parent = parent
        self.children = []

    def __lt__(self, other):
        return self.score > other.score  # Higher scores have priority


class TreeOfThoughts:
    def __init__(self, max_depth: int = 5, beam_width: int = 3):
        self.max_depth = max_depth
        self.beam_width = beam_width
        self.root = None

    def generate_thoughts(self, current_thought: Thought) -> List[Thought]:
        """Generate possible next thoughts from current thought."""
        # In a real implementation, this would use an LLM to generate diverse thoughts
        return [Thought(f"Thought branch {i}", 0.5, current_thought) for i in range(3)]

    def evaluate_thought(self, thought: Thought) -> float:
        """Evaluate the quality of a thought."""
        # In a real implementation, this would use an LLM or other metric
        return 0.7  # Mock score

    def get_path_to_root(self, thought: Thought) -> List[str]:
        """Get the sequence of thoughts from root to current thought."""
        path = []
        current = thought
        while current:
            path.append(current.content)
            current = current.parent
        return list(reversed(path))

    def solve(self, problem: str) -> List[str]:
        """
        Solve a problem using tree of thoughts approach.

        Args:
            problem: The problem statement to solve

        Returns:
            List of thoughts representing the best solution path
        """
        # Initialize root thought
        self.root = Thought(problem, 1.0)

        # Priority queue for beam search
        frontier = PriorityQueue()
        frontier.put(self.root)

        best_terminal_thought = None
        best_score = float("-inf")

        # Explore the tree up to max_depth
        for depth in range(self.max_depth):
            level_thoughts = []

            # Generate and evaluate thoughts for current level
            while not frontier.empty() and len(level_thoughts) < self.beam_width:
                current = frontier.get()

                # Generate possible next thoughts
                next_thoughts = self.generate_thoughts(current)

                # Evaluate and store new thoughts
                for thought in next_thoughts:
                    thought.score = self.evaluate_thought(thought)
                    current.children.append(thought)
                    level_thoughts.append(thought)

                    # Update best terminal thought if this is better
                    if thought.score > best_score:
                        best_terminal_thought = thought
                        best_score = thought.score

            # Add thoughts for next level exploration
            for thought in sorted(level_thoughts, key=lambda x: x.score)[
                : self.beam_width
            ]:
                frontier.put(thought)

        # Return the path of the best solution found
        return self.get_path_to_root(best_terminal_thought)
