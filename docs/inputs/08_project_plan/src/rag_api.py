import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import openai


class RAGAPI:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key

    def fetch_context(
        self, tasks: List[Dict[str, Any]], events: List[Dict[str, Any]]
    ) -> str:
        """Gather context from tasks and events."""
        context = []

        # Add task context
        for task in tasks:
            context.append(f"Task: {task['content']}")
            if task.get("description"):
                context.append(f"Description: {task['description']}")
            if task.get("due"):
                context.append(f"Due: {task['due']}")

        # Add event context
        for event in events:
            context.append(f"Event: {event['summary']}")
            if event.get("description"):
                context.append(f"Description: {event['description']}")
            if event.get("start"):
                context.append(f"Start: {event['start']['dateTime']}")

        return "\n".join(context)

    async def get_completion(self, prompt: str, context: str) -> str:
        """Get completion from the RAG API."""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant with access to the user's tasks and calendar events.",
                    },
                    {
                        "role": "user",
                        "content": f"Context:\n{context}\n\nPrompt: {prompt}",
                    },
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error getting completion: {e}")
            return ""

    def process_agent_interaction(
        self, agent_type: str, prompt: str, context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process an agent interaction with the given type and prompt."""
        return {
            "agent_type": agent_type,
            "prompt": prompt,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "status": "processed",
        }
