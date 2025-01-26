"""
Society of Mind (SoM) implementation.
"""

from typing import Any, Dict, List

from .base import BaseAgent


class SubAgent(BaseAgent):
    """A specialized agent that focuses on a specific aspect of problem-solving."""

    def __init__(self, name: str, specialty: str):
        super().__init__(name)
        self.specialty = specialty
        self.confidence_threshold = 0.7

    def think(self, input_data: Dict[str, Any]) -> List[str]:
        """Generate thoughts related to this agent's specialty."""
        thoughts = [
            f"Analyzing from {self.specialty} perspective:",
            self._analyze_specialty(input_data),
        ]
        return thoughts

    def act(self, thoughts: List[str]) -> Dict[str, Any]:
        """Provide specialized recommendations based on thoughts."""
        return {
            "specialty": self.specialty,
            "recommendation": (thoughts[-1] if thoughts else "No recommendation"),
            "confidence": self._calculate_confidence(thoughts),
        }

    def _analyze_specialty(self, input_data: Dict[str, Any]) -> str:
        """Analyze the input from this agent's specialized perspective."""
        # In practice, this would contain specialized logic for each type of agent
        return f"Based on {self.specialty}, I recommend: {input_data}"

    def _calculate_confidence(self, thoughts: List[str]) -> float:
        """Calculate confidence in the recommendation."""
        # Simple confidence calculation
        return 0.8 if thoughts else 0.0


class SocietyOfMindAgent(BaseAgent):
    """
    An agent that implements the Society of Mind approach by coordinating
    multiple specialized sub-agents to solve complex problems.
    """

    def __init__(self, name: str = "SoM Agent"):
        super().__init__(name)
        self.sub_agents: List[SubAgent] = []
        self._initialize_society()

    def _initialize_society(self):
        """Initialize the society with various specialized agents."""
        specialties = [
            "logical_reasoning",
            "emotional_intelligence",
            "pattern_recognition",
            "creative_thinking",
            "risk_assessment",
        ]

        for specialty in specialties:
            agent = SubAgent(f"{specialty}_agent", specialty)
            self.sub_agents.append(agent)

    def add_sub_agent(self, agent: SubAgent):
        """Add a new sub-agent to the society."""
        self.sub_agents.append(agent)

    def think(self, input_data: Dict[str, Any]) -> List[str]:
        """
        Coordinate thinking across all sub-agents and synthesize their thoughts.
        """
        thoughts = [f"Processing input with {len(self.sub_agents)} sub-agents"]

        # Collect thoughts from all sub-agents
        agent_thoughts = {}
        for agent in self.sub_agents:
            agent_thoughts[agent.specialty] = agent.think(input_data)

        # Synthesize thoughts
        synthesis = self._synthesize_thoughts(agent_thoughts)
        thoughts.extend(synthesis)

        return thoughts

    def act(self, thoughts: List[str]) -> Dict[str, Any]:
        """
        Coordinate actions based on collective thinking of sub-agents.
        """
        # Collect recommendations from all sub-agents
        recommendations = []
        for agent in self.sub_agents:
            result = agent.act(agent.think({"thoughts": thoughts}))
            if result["confidence"] >= agent.confidence_threshold:
                recommendations.append(result)

        # Synthesize recommendations into final action
        final_action = self._synthesize_recommendations(recommendations)

        return {
            "collective_action": final_action,
            "individual_recommendations": recommendations,
            "confidence": self._calculate_collective_confidence(recommendations),
        }

    def _synthesize_thoughts(self, agent_thoughts: Dict[str, List[str]]) -> List[str]:
        """Synthesize thoughts from all sub-agents."""
        synthesis = []

        # Combine thoughts from each specialty
        for specialty, thoughts in agent_thoughts.items():
            synthesis.append(f"From {specialty} perspective:")
            synthesis.extend([f"  - {thought}" for thought in thoughts])

        # Add overall synthesis
        synthesis.append("Overall synthesis:")
        synthesis.append(self._create_overall_synthesis(agent_thoughts))

        return synthesis

    def _synthesize_recommendations(self, recommendations: List[Dict[str, Any]]) -> str:
        """Synthesize individual recommendations into a collective action."""
        if not recommendations:
            return "No confident recommendations available"

        # Sort by confidence
        recommendations.sort(key=lambda x: x["confidence"], reverse=True)

        # Combine top recommendations
        top_recommendations = recommendations[:3]
        synthesis = "Collective action based on: "
        synthesis += ", ".join(
            f"{r['specialty']} ({r['confidence']:.2f})" for r in top_recommendations
        )

        return synthesis

    def _calculate_collective_confidence(
        self, recommendations: List[Dict[str, Any]]
    ) -> float:
        """Calculate overall confidence based on individual recommendations."""
        if not recommendations:
            return 0.0

        # Average confidence of top 3 recommendations
        top_confidences = sorted(
            [r["confidence"] for r in recommendations], reverse=True
        )[:3]
        return sum(top_confidences) / len(top_confidences) if top_confidences else 0.0

    def _create_overall_synthesis(self, agent_thoughts: Dict[str, List[str]]) -> str:
        """Create an overall synthesis of all agent thoughts."""
        # Count common themes/recommendations
        themes = {}
        for thoughts in agent_thoughts.values():
            for thought in thoughts:
                themes[thought] = themes.get(thought, 0) + 1

        # Find most common themes
        common_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)

        if not common_themes:
            return "No common themes found"

        return (
            f"Most common theme: {common_themes[0][0]} "
            f"(mentioned by {common_themes[0][1]} agents)"
        )
