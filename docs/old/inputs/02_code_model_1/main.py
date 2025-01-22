from agent_framework import ActorCriticAgent, BanditAgent, BaseAgent
from ai_reasoning_algorithms import ChainOfThoughtAlgorithm, ReActAlgorithm
from mental_models import EisenhowerMatrix, SecondOrderThinking


def main():
    ## Create agents
    agentA = BaseAgent("GenericAgent")
    agentA.add_mental_model(EisenhowerMatrix())
    agentA.add_mental_model(SecondOrderThinking())
    agentA.add_ai_algorithm(ReActAlgorithm())

    ac_agent = ActorCriticAgent(name="ActorCriticAgent")
    bandit_agent = BanditAgent(name="BanditAgent", method="epsilon-greedy", epsilon=0.1)

    ## Create a sample request
    request = {
        "bandit_arms": ["ArmA", "ArmB", "ArmC"],
        "environment_state": "State1",
        "tasks": ["urgent task", "important task"],
        "decision": "Expand facilities?",
    }

    ## Process requests
    print("Results from GenericAgent:", agentA.process_request(request))
    print("Results from ActorCriticAgent:", ac_agent.process_request(request))
    print("Results from BanditAgent:", bandit_agent.process_request(request))


if __name__ == "__main__":
    main()
