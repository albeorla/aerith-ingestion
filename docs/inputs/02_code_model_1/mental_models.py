from abc import ABC, abstractmethod
from typing import Any, Dict


class MentalModel(ABC):
    """
    Base class for all mental models.
    """

    def __init__(
        self,
        name: str,
        model_type: str,
        description: str,
        typical_applications: str,
    ):
        self.name = name
        self.model_type = model_type
        self.description = description
        self.typical_applications = typical_applications

    @abstractmethod
    def apply(self, context: Dict[str, Any]) -> str:
        """
        Stubbed method for applying the mental model.
        """
        pass


class EisenhowerMatrix(MentalModel):
    def __init__(self):
        super().__init__(
            name="Eisenhower Matrix",
            model_type="Prioritization",
            description="Categorize tasks by urgency and importance.",
            typical_applications="Task management, productivity enhancement.",
        )

    def apply(self, context: Dict[str, Any]) -> str:
        tasks = context.get("tasks", [])
        urgent_tasks = [task for task in tasks if "urgent" in task]
        important_tasks = [task for task in tasks if "important" in task]
        return (
            f"[{self.name}] Prioritized tasks: {len(urgent_tasks)} urgent, "
            f"{len(important_tasks)} important."
        )


class SecondOrderThinking(MentalModel):
    def __init__(self):
        super().__init__(
            name="Second-Order Thinking",
            model_type="Strategic Thinking",
            description="Considers long-term consequences of decisions.",
            typical_applications="Strategic planning, risk assessment.",
        )

    def apply(self, context: Dict[str, Any]) -> str:
        decision = context.get("decision", "No decision")
        return f"[{self.name}] Analyzed long-term consequences for '{decision}'."
