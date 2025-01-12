from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, NamedTuple, Optional, Sequence

import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.storage import StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore

from ..domain.models import EnrichedTask, Task, VectorMetadata


@dataclass
class VectorStoreConfig:
    """Configuration for vector store

    Attributes:
        collection_name: str  # Name of the ChromaDB collection
        embedding_model: str  # Sentence transformer model to use for embeddings:
            # - all-MiniLM-L6-v2: Fast, efficient model good for short texts (default)
            # - all-mpnet-base-v2: Better quality but slower
            # - paraphrase-multilingual-MiniLM-L12-v2: Multi-language support
        batch_size: int  # Number of tasks to process at once
        similarity_top_k: int  # Number of similar tasks to return in searches
        persist_directory: Optional[str]
        chroma_settings: Optional[Dict[str, Any]]  # Additional ChromaDB settings
    """

    collection_name: str = "todoist_tasks"
    embedding_model: str = "all-MiniLM-L6-v2"
    batch_size: int = 100
    similarity_top_k: int = 5
    persist_directory: Optional[str] = None
    chroma_settings: Optional[Dict[str, Any]] = None


class TaskSearchResult(NamedTuple):
    """Result from a task search query"""

    task_id: str
    score: float
    metadata: Dict[str, Any]


class VectorStoreService:
    """Service for managing task vectors in the database

    Uses ChromaDB with sentence-transformers for efficient similarity search.
    The default embedding model (all-MiniLM-L6-v2) is optimized for short text
    like task titles and descriptions, providing a good balance of speed and quality.
    """

    def __init__(self, config: Optional[VectorStoreConfig] = None):
        """Initialize the vector store service

        Args:
            config: Vector store configuration. If None, uses defaults optimized
                   for task management (all-MiniLM-L6-v2 embeddings, in-memory store)
        """
        self.config = config or VectorStoreConfig()

        # Initialize embedding function with sentence transformers
        # This is more efficient than the BGE models for short texts
        self.embedding_function = SentenceTransformerEmbeddingFunction(
            model_name=self.config.embedding_model
        )

        # Initialize Chroma client with settings
        chroma_settings = ChromaSettings(
            **(self.config.chroma_settings or {}), anonymized_telemetry=False
        )

        if self.config.persist_directory:
            self.chroma_client = chromadb.PersistentClient(
                path=self.config.persist_directory, settings=chroma_settings
            )
        else:
            self.chroma_client = chromadb.Client(settings=chroma_settings)

        # Create collection for tasks with the embedding function
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.config.collection_name,
            embedding_function=self.embedding_function,
        )

        # Set up vector store
        vector_store = ChromaVectorStore(chroma_collection=self.collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # Create the index
        self.index = VectorStoreIndex([], storage_context=storage_context)

    def _create_document(self, task: Task) -> Document:
        """Create a document from a task for vector storage"""
        # Combine task content for embedding
        text = f"Task: {task.content}\nDescription: {task.description}"

        # Create metadata for retrieval
        metadata = {
            "task_id": task.id,
            "project_id": task.project_id,
            "priority": task.priority,
            "due_date": task.due.date if task.due else None,
            "is_completed": task.is_completed,
            "content_hash": task.get_content_hash(),
        }

        return Document(text=text, metadata=metadata)

    def upsert_tasks(self, tasks: Sequence[EnrichedTask]) -> List[VectorMetadata]:
        """Batch update or insert tasks in the vector store"""
        results = []

        # Process in batches
        for i in range(0, len(tasks), self.config.batch_size):
            batch = tasks[i : i + self.config.batch_size]

            # Delete old vectors if they exist
            doc_ids_to_delete = []
            for task in batch:
                if task.vector_metadata:
                    doc_ids_to_delete.append(task.vector_metadata.doc_id)

            if doc_ids_to_delete:
                self.collection.delete(ids=doc_ids_to_delete)

            # Create and insert new documents
            docs = [self._create_document(task.task) for task in batch]
            self.index.insert_nodes(docs)

            # Create metadata for each task
            for task, doc in zip(batch, docs):
                metadata = VectorMetadata(
                    doc_id=doc.doc_id,
                    embedding_model=self.config.embedding_model,
                    last_updated=datetime.now(),
                    content_hash=task.task.get_content_hash(),
                )
                results.append(metadata)

        return results

    def upsert_task(self, enriched_task: EnrichedTask) -> VectorMetadata:
        """Update or insert a single task in the vector store"""
        results = self.upsert_tasks([enriched_task])
        return results[0]

    def delete_tasks(self, task_ids: List[str]) -> None:
        """Batch delete tasks from the vector store"""
        # Find all document IDs for the tasks
        doc_ids = []
        for task_id in task_ids:
            for node_id, node_info in self.index.ref_doc_info.items():
                if node_info.metadata.get("task_id") == task_id:
                    doc_ids.append(node_id)
                    break

        # Delete in batches
        for i in range(0, len(doc_ids), self.config.batch_size):
            batch = doc_ids[i : i + self.config.batch_size]
            self.collection.delete(ids=batch)

    def delete_task(self, task_id: str) -> None:
        """Delete a single task from the vector store"""
        self.delete_tasks([task_id])

    def search_tasks(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: Optional[int] = None,
    ) -> List[TaskSearchResult]:
        """Search for tasks using semantic similarity"""
        # Use configured top_k if not specified
        top_k = top_k or self.config.similarity_top_k

        # Execute query
        query_results = self.index.query(query, similarity_top_k=top_k, filters=filters)

        # Convert to TaskSearchResult objects
        results = []
        for node in query_results.nodes:
            result = TaskSearchResult(
                task_id=node.metadata["task_id"],
                score=node.score,
                metadata=node.metadata,
            )
            results.append(result)

        return results

    def find_similar_tasks(
        self,
        task: Task,
        project_id: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> List[TaskSearchResult]:
        """Find tasks similar to the given task"""
        # Create query text
        query_text = f"Task: {task.content}\nDescription: {task.description}"

        # Set up filters
        filters = {
            "task_id": {"$ne": task.id},  # Exclude the task itself
            "content_hash": {"$ne": task.get_content_hash()},  # Exclude exact matches
        }
        if project_id:
            filters["project_id"] = project_id

        # Execute search
        return self.search_tasks(query_text, filters=filters, top_k=top_k)
