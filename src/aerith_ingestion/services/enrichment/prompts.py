"""
LLM prompts for task analysis.

This module contains the prompt templates used for task analysis.
"""

TASK_ANALYSIS_PROMPT = """
Analyze the following task:
Content: {task_content}
Description: {task_description}

Please provide a structured analysis including:
- Category (e.g. Development, Research, Planning)
- Complexity (High, Medium, Low)
- Key themes/topics
- Required dependencies/prerequisites
"""

TASK_RECOMMENDATIONS_PROMPT = """
Based on this task:
Content: {task_content}

And its analysis:
{task_analysis}

Please provide actionable next steps and recommendations.
"""
