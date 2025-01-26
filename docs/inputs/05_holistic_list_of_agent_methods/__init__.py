"""
Agent Methods Package

This package contains implementations of various agent methods and frameworks
for enhanced problem-solving and reasoning.
"""

from .chain_of_thought import ChainOfThoughtAgent
from .react_agent import ReActAgent
from .society_of_mind import SocietyOfMind, SubAgent
from .somine_prompt import SoMinEPrompt
from .tool_use_agent import ToolRegistry, ToolUseAgent

__all__ = [
    "ChainOfThoughtAgent",
    "ReActAgent",
    "SocietyOfMind",
    "SubAgent",
    "SoMinEPrompt",
    "ToolUseAgent",
    "ToolRegistry",
]
