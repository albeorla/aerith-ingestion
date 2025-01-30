"""
Centralized prompt templates for the GeminiService and related GTD processing.
"""

# GTD Level Definitions
import json
from typing import Any, Dict, Optional

GTD_LEVEL_DEFINITIONS = """
**GTD Levels of Work:**

1. **Purpose and Principles (Horizon 5):** Ultimate intention and success standards
2. **Vision (Horizon 4):** Long-term outcomes and ideal scenarios
3. **Goals and Objectives (Horizon 3):** Specific 12-24 month accomplishments
4. **Areas of Focus (Horizon 2):** Key areas requiring ongoing maintenance
5. **Projects (Horizon 1):** Multi-step outcomes achievable within a year
6. **Next Actions (Ground):** Immediate, physical, visible next steps

Choose the most appropriate single level for the task.
"""


# Function to generate the task categorization prompt
def get_task_categorization_prompt(task_content: str, gtd_definitions: str) -> str:
    """Generate a prompt for categorizing a task into GTD levels."""
    return f"""Analyze this task and provide GTD categorization with enriched metadata:

Task: "{task_content}"

{gtd_definitions}

Respond with a JSON object containing:
1. GTD level (required)
2. Estimated duration
3. Energy level required (High/Medium/Low)
4. Context tags (e.g., @home, @computer, @phone)
5. Brief reason for categorization

Example response:
{{
    "gtd_level": "Projects",
    "estimated_duration": "2-3 hours",
    "energy_level": "High",
    "context_tags": ["@computer", "@focus"],
    "categorization_reason": "Multi-step research task requiring sustained attention"
}}

Respond with ONLY the JSON object. No other text."""


# Function to generate the function call prompt
def get_function_call_prompt(
    contents: str, function_name: str, parameters: dict
) -> str:
    """Generate a prompt for creating a structured function call."""
    return f"""Generate a function call based on the following information.

Context: {contents}
Function: {function_name}
Parameters: {json.dumps(parameters, indent=2)}

Respond with ONLY a JSON object representing the function call. No explanation or additional text.
"""


def parse_gemini_json_response(response_text: str) -> Optional[Dict[str, Any]]:
    """Clean and parse JSON from Gemini response."""
    if not isinstance(response_text, str):
        return None

    try:
        # Remove markdown code blocks and json labels
        text = response_text.strip()
        if text.startswith("```"):
            # Find the first and last backtick groups
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                text = text[start:end]

        # Clean any remaining markdown or labels
        text = text.replace("```json", "").replace("```", "").strip()

        # Parse the cleaned JSON
        return json.loads(text)

    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error parsing JSON: {e}")
        print(f"Problematic text: {text}")
        return None


def get_content_processing_prompt(content: str) -> str:
    """Generate a prompt for processing task content."""
    return f"""Analyze and improve this task content while preserving its core meaning:

Content: "{content}"

Provide a JSON response with:
1. Processed content (fix spelling, grammar, clarity)
2. List of changes made
3. Original content preserved

Example response:
{{
    "processed_content": "Research techniques for creating energy through mindset practices.",
    "original_content": "Research techniques for creating energy through mindset",
    "changes": {{
        "spelling_fixes": [],
        "grammar_fixes": ["Added period", "Added clarifying word 'practices'"],
        "formatting_fixes": ["Capitalized first word"],
        "content_changes": ["Improved clarity while preserving meaning"]
    }}
}}

Respond with ONLY the JSON object. No other text."""


def get_task_prioritization_prompt(task_content: str, gtd_level: str) -> str:
    """Generate a prompt for determining task priority and timeframe."""
    return f"""Analyze this task and determine its priority and timeframe:

Task: "{task_content}"
GTD Level: {gtd_level}

Consider:
1. Urgency (time-sensitive vs flexible)
2. Impact (high value vs low value)
3. Dependencies (blocking other tasks vs independent)
4. Effort required (quick win vs major undertaking)

Provide a JSON response with:
1. Priority level (1-4, where 4 is highest)
2. Timeframe (Now, Next, Soon, Later)
3. Reasoning for the prioritization
4. Dependencies or blockers
5. Suggested deadline if applicable

Example response:
{{
    "priority": 4,
    "timeframe": "Now",
    "reasoning": "High-impact task that blocks other work, requires immediate attention",
    "dependencies": ["Research phase must complete first"],
    "suggested_deadline": "2024-02-15",
    "effort_level": "Medium",
    "impact_assessment": "High value - enables multiple downstream tasks"
}}

Respond with ONLY the JSON object. No other text."""


def get_task_organization_prompt(tasks: list[dict]) -> str:
    """Generate a prompt for organizing multiple tasks."""
    tasks_str = "\n".join(
        [
            f"- {t['content']} (GTD Level: {t['gtd_level']}, Priority: {t.get('priority', 'unset')})"
            for t in tasks
        ]
    )

    return f"""Analyze these tasks and suggest optimal organization:

Tasks:
{tasks_str}

Provide a JSON response with:
1. Task groupings by theme/context
2. Suggested workflow order
3. Parallel execution opportunities
4. Resource allocation suggestions
5. Time blocking recommendations

Example response:
{{
    "task_groups": [
        {{
            "theme": "Research & Planning",
            "tasks": ["Task1", "Task3"],
            "context": "@focus",
            "suggested_time_block": "Morning"
        }}
    ],
    "workflow_order": [
        {{
            "phase": "Initial Research",
            "tasks": ["Task1"],
            "dependencies": []
        }}
    ],
    "parallel_opportunities": [
        {{
            "group": "Independent Tasks",
            "tasks": ["Task2", "Task4"]
        }}
    ],
    "resource_recommendations": {{
        "time_allocation": "60% research, 40% implementation",
        "focus_periods": "2-3 hour blocks"
    }}
}}

Respond with ONLY the JSON object. No other text."""
