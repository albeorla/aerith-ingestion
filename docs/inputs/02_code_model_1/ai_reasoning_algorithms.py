import random
from abc import ABC, abstractmethod
from typing import Any, Dict


class AIReasoningAlgorithm(ABC):
    """
    Base class for AI reasoning algorithms.
    """

    def __init__(self, name: str, description: str, typical_applications: str):
        self.name = name
        self.description = description
        self.typical_applications = typical_applications

    @abstractmethod
    def reason(self, context: Dict[str, Any]) -> str:
        """
        Returns a textual reasoning trace or conclusion.
        """
        pass


class ReActAlgorithm(AIReasoningAlgorithm):
    def __init__(self):
        super().__init__(
            name="ReAct (Reasoning + Acting)",
            description="Combines reasoning traces with actions in external tools/env.",
            typical_applications="Interactive decision-making, complex task solving.",
        )

    def reason(self, context: Dict[str, Any]) -> str:
        decision_point = context.get("decision_point", "N/A")
        return f"[{self.name}] Reasoned about '{decision_point}' and performed actions."


class ChainOfThoughtAlgorithm(AIReasoningAlgorithm):
    def __init__(self):
        super().__init__(
            name="Chain-of-Thought (CoT) Prompting",
            description="Step-by-step reasoning before final answer.",
            typical_applications="Complex problem-solving, mathematical reasoning.",
        )

    def reason(self, context: Dict[str, Any]) -> str:
        problem_statement = context.get("problem_statement", "N/A")
        steps = [
            "Step 1: Analyze problem.",
            "Step 2: Identify constraints.",
            "Step 3: Solve.",
        ]
        return f"[{self.name}] Generated reasoning chain for '{problem_statement}': {', '.join(steps)}."


class ActorCriticAlgorithm(AIReasoningAlgorithm):
    def __init__(self):
        super().__init__(
            name="Actor-Critic Algorithm",
            description="Combines policy-based (Actor) and value-based (Critic) methods.",
            typical_applications="Robotics, game AI, real-time decision-making.",
        )
        self.actor_policy = {}
        self.critic_values = {}

    def reason(self, context: Dict[str, Any]) -> str:
        state = context.get("environment_state", "No state provided")
        action = random.choice(["ActionA", "ActionB", "ActionC"])
        reward = random.uniform(0, 1)  ## Simulated reward
        self.critic_values[state] = reward
        return f"[{self.name}] Chose action '{action}' in state '{state}' with reward {reward:.2f}."


class MultiArmedBanditAlgorithm(AIReasoningAlgorithm):
    def __init__(self, method: str = "epsilon-greedy", epsilon: float = 0.1):
        super().__init__(
            name="Multi-Armed Bandit",
            description=f"Bandit approach using {method} method.",
            typical_applications="Online advertising, recommendation systems, A/B testing.",
        )
        self.method = method
        self.epsilon = epsilon
        self.arm_rewards = {}

    def reason(self, context: Dict[str, Any]) -> str:
        arms = context.get("bandit_arms", [])
        if self.method == "epsilon-greedy":
            if random.random() < self.epsilon:
                chosen_arm = random.choice(arms)
            else:
                chosen_arm = max(
                    self.arm_rewards,
                    key=self.arm_rewards.get,
                    default=random.choice(arms),
                )
        else:
            chosen_arm = random.choice(arms)
        reward = random.uniform(0, 1)  ## Simulated reward
        self.arm_rewards[chosen_arm] = self.arm_rewards.get(chosen_arm, 0) + reward
        return f"[{self.name}] Selected arm '{chosen_arm}' with reward {reward:.2f}."
