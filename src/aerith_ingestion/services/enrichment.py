from typing import Any, Dict, List

from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from aerith_ingestion.domain.models import Task


class TaskEnrichmentService:
    """Service for enriching tasks using LangChain and OpenAI"""

    def __init__(self, openai_api_key: str):
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.llm = ChatOpenAI(
            model="gpt-4o-mini", openai_api_key=openai_api_key, temperature=0
        )

        # Create a chain for task analysis
        self.analysis_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "You are an AI assistant that analyzes individual tasks and "
                        "provides insights. Analyze the task and provide:\n"
                        "1. Task category/type\n"
                        "2. Estimated complexity (low/medium/high)\n"
                        "3. Key themes or topics\n"
                        "4. Any potential dependencies or prerequisites\n"
                        "5. Suggested next actions or subtasks\n"
                        "Format the response as a JSON object."
                    ),
                ),
                (
                    "human",
                    "Task: {task_content}\nDescription: {task_description}",
                ),
            ]
        )
        self.analysis_chain = self.analysis_prompt | self.llm | StrOutputParser()

    def get_embeddings(self, text: str) -> List[float]:
        """Generate embeddings for the given text"""
        return self.embeddings.embed_query(text)

    def analyze_task(self, task: Task) -> Dict[str, Any]:
        """Perform deep analysis of the task using LLM"""
        task_text = f"{task.content}\n{task.description}"
        analysis_result = self.analysis_chain.invoke(
            {
                "task_content": task.content,
                "task_description": task.description,
            }
        )

        # Generate embeddings for the task
        embeddings = self.get_embeddings(task_text)

        return {
            "llm_analysis": analysis_result,
            "embeddings": embeddings,
            "embedding_model": "text-embedding-3-large",
        }
