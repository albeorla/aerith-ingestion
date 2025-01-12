"""
Self-Reflective Agent implementation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List

from .base import BaseAgent


@dataclass
class Experience:
    """A record of an agent's experience."""

    timestamp: datetime
    action: str
    context: Dict[str, Any]
    outcome: Dict[str, Any]
    reflection: str = ""
    lessons_learned: List[str] = field(default_factory=list)


class ExperienceMemory:
    """A memory system for storing and retrieving experiences."""

    def __init__(self, max_size: int = 1000):
        self.experiences: List[Experience] = []
        self.max_size = max_size

    def add(self, experience: Experience):
        """Add a new experience to memory."""
        self.experiences.append(experience)
        if len(self.experiences) > self.max_size:
            self.experiences.pop(0)

    def get_similar_experiences(
        self, context: Dict[str, Any], limit: int = 5
    ) -> List[Experience]:
        """Retrieve experiences similar to the given context."""
        # In practice, this would use more sophisticated similarity matching
        # For now, we'll just return the most recent experiences
        return sorted(self.experiences, key=lambda x: x.timestamp, reverse=True)[:limit]

    def get_lessons_learned(self) -> List[str]:
        """Get all unique lessons learned from experiences."""
        lessons = set()
        for exp in self.experiences:
            lessons.update(exp.lessons_learned)
        return list(lessons)


class SelfReflectiveAgent(BaseAgent):
    """
    An agent that can reflect on its actions and learn from experience.
    """

    def __init__(self, name: str = "Self-Reflective Agent"):
        super().__init__(name)
        self.memory = ExperienceMemory()
        self.reflection_threshold = 0.7  # Confidence threshold for reflection

    def think(self, input_data: Dict[str, Any]) -> List[str]:
        """
        Generate thoughts, incorporating past experiences and reflections.
        """
        thoughts = []

        # Consider the current situation
        thoughts.append(f"Current situation: {input_data}")

        # Recall similar experiences
        similar_experiences = self.memory.get_similar_experiences(input_data)
        if similar_experiences:
            thoughts.append("Relevant past experiences:")
            for exp in similar_experiences:
                thoughts.append(f"- {exp.action}: {exp.reflection}")

        # Review lessons learned
        lessons = self.memory.get_lessons_learned()
        if lessons:
            thoughts.append("Applicable lessons learned:")
            for lesson in lessons:
                thoughts.append(f"- {lesson}")

        # Plan action considering past experiences
        action_plan = self._plan_action(input_data, similar_experiences)
        thoughts.append(f"Planned action: {action_plan}")

        return thoughts

    def act(self, thoughts: List[str]) -> Dict[str, Any]:
        """
        Take action and record the experience.
        """
        # Extract planned action from thoughts
        action = thoughts[-1].replace("Planned action: ", "")

        try:
            # Execute the action
            result = self._execute_action(action)
            success = True
        except Exception as e:
            result = str(e)
            success = False

        # Record the experience
        experience = Experience(
            timestamp=datetime.now(),
            action=action,
            context={"thoughts": thoughts},
            outcome={"success": success, "result": result},
        )

        # Reflect on the experience
        self._reflect_on_experience(experience)

        # Store in memory
        self.memory.add(experience)

        return {
            "action": action,
            "result": result,
            "success": success,
            "reflection": experience.reflection,
            "lessons_learned": experience.lessons_learned,
        }

    def _plan_action(
        self, input_data: Dict[str, Any], similar_experiences: List[Experience]
    ) -> str:
        """Plan action based on current input and past experiences."""
        if not similar_experiences:
            return f"New approach for: {input_data}"

        # Analyze outcomes of similar experiences
        successful_actions = [
            exp.action
            for exp in similar_experiences
            if exp.outcome.get("success", False)
        ]

        if successful_actions:
            # Adapt most successful past action
            return f"Adapted from successful experience: {successful_actions[0]}"
        else:
            # Try a different approach
            return (
                f"New approach (after {len(similar_experiences)} unsuccessful attempts)"
            )

    def _execute_action(self, action: str) -> Any:
        """Execute the planned action."""
        # In practice, this would contain actual action execution logic
        return f"Executed: {action}"

    def _reflect_on_experience(self, experience: Experience):
        """Reflect on an experience and extract lessons learned."""
        # Analyze the outcome
        success = experience.outcome.get("success", False)

        if success:
            experience.reflection = self._reflect_on_success(experience)
        else:
            experience.reflection = self._reflect_on_failure(experience)

        # Extract lessons learned
        experience.lessons_learned = self._extract_lessons(experience)

    def _reflect_on_success(self, experience: Experience) -> str:
        """Reflect on a successful experience."""
        return (
            f"Success in executing '{experience.action}'. "
            f"This approach worked well in this context."
        )

    def _reflect_on_failure(self, experience: Experience) -> str:
        """Reflect on a failed experience."""
        return (
            f"Failed to execute '{experience.action}'. "
            f"Need to analyze what went wrong and adjust approach."
        )

    def _extract_lessons(self, experience: Experience) -> List[str]:
        """Extract lessons learned from an experience."""
        lessons = []

        # Analyze success/failure patterns
        if experience.outcome.get("success", False):
            lessons.append(
                f"Successful approach: {experience.action} "
                f"in context: {experience.context}"
            )
        else:
            lessons.append(
                f"Approach to avoid: {experience.action} "
                f"in context: {experience.context}"
            )

        return lessons

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get metrics about the agent's performance over time."""
        total_experiences = len(self.memory.experiences)
        if total_experiences == 0:
            return {"error": "No experiences recorded"}

        successful_experiences = sum(
            1 for exp in self.memory.experiences if exp.outcome.get("success", False)
        )

        return {
            "total_experiences": total_experiences,
            "successful_experiences": successful_experiences,
            "success_rate": successful_experiences / total_experiences,
            "unique_lessons_learned": len(self.memory.get_lessons_learned()),
        }
