"""
Vector store for managing task embeddings and similarity search.

This module provides:
1. Vector embedding generation using OpenAI's text-embedding-ada-002
2. Vector storage and retrieval using FAISS
3. Similarity search functionality
"""

import os
from typing import List, Optional

import faiss
import numpy as np
from openai import OpenAI

from aerith_ingestion.domain.task import VectorMetadata


class VectorStore:
    """Manages vector embeddings and similarity search."""

    def __init__(self, openai_client: OpenAI, index_path: Optional[str] = None):
        self.openai_client = openai_client
        self.index_path = index_path
        self.index = self._load_or_create_index()
        self.task_ids: List[str] = []
        self.contents: List[str] = []

    def generate_embedding(self, text: str) -> List[float]:
        """Generate vector embedding for text using OpenAI."""
        response = self.openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=text,
        )
        return response.data[0].embedding

    def add_vector(self, metadata: VectorMetadata) -> None:
        """Add a vector to the index."""
        vector = np.array([metadata.vector], dtype=np.float32)
        self.index.add(vector)
        self.task_ids.append(metadata.task_id)
        self.contents.append(metadata.content)

    def search_similar(self, query_text: str, k: int = 5) -> List[VectorMetadata]:
        """Search for similar vectors using the query text."""
        query_vector = self.generate_embedding(query_text)
        query_vector = np.array([query_vector], dtype=np.float32)

        # Search index
        distances, indices = self.index.search(query_vector, k)

        # Convert results to VectorMetadata
        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1:  # FAISS returns -1 for empty slots
                continue
            results.append(
                VectorMetadata(
                    task_id=self.task_ids[idx],
                    vector=self.index.reconstruct(idx).tolist(),
                    content=self.contents[idx],
                )
            )
        return results

    def _load_or_create_index(self) -> faiss.Index:
        """Load existing index or create new one."""
        if self.index_path and os.path.exists(self.index_path):
            return faiss.read_index(self.index_path)
        return faiss.IndexFlatL2(1536)  # OpenAI ada-002 dimension

    def save(self) -> None:
        """Save index to disk if path specified."""
        if self.index_path:
            faiss.write_index(self.index, self.index_path)


def create_vector_store(
    openai_client: OpenAI, index_path: Optional[str] = None
) -> VectorStore:
    """Create a new vector store instance."""
    return VectorStore(openai_client, index_path)
