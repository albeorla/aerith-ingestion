from typing import Any, Dict, List

from ai_reasoning_algorithms import (
    ActorCriticAlgorithm,
    AIReasoningAlgorithm,
    MultiArmedBanditAlgorithm,
)
from mental_models import MentalModel


class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        self.mental_models: List[MentalModel] = []
        self.ai_algorithms: List[AIReasoningAlgorithm] = []

    def add_mental_model(self, model: MentalModel):
        self.mental_models.append(model)

    def add_ai_algorithm(self, algo: AIReasoningAlgorithm):
        self.ai_algorithms.append(algo)

    def process_request(self, request: Dict[str, Any]) -> Dict[str, str]:
        results = {}
        for model in self.mental_models:
            results[model.name] = model.apply(request)
        for algo in self.ai_algorithms:
            results[algo.name] = algo.reason(request)
        return results


class ActorCriticAgent(BaseAgent):
    def __init__(self, name: str):
        super().__init__(name)
        self.add_ai_algorithm(ActorCriticAlgorithm())


class BanditAgent(BaseAgent):
    def __init__(self, name: str, method: str = "epsilon-greedy", epsilon: float = 0.1):
        super().__init__(name)
        self.add_ai_algorithm(MultiArmedBanditAlgorithm(method=method, epsilon=epsilon))
