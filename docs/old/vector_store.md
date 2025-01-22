# Vector Store Integration

## Overview
The vector store integration enables semantic search and similarity matching for tasks by maintaining an up-to-date vector database that reflects the current state of tasks in Todoist. The system is designed to efficiently handle task updates while minimizing unnecessary vector recalculations.

## Architecture

### Components

1. **VectorMetadata**
   - Tracks the state of each task's vector representation
   - Contains:
     - `doc_id`: Unique identifier in the vector store
     - `embedding_model`: Model used for embeddings
     - `last_updated`: Timestamp of last vector update
     - `content_hash`: Hash of task content when vectorized

2. **VectorStoreService**
   - Manages vector database operations
   - Handles atomic updates (delete old + insert new)
   - Uses LlamaIndex for vector storage and retrieval

3. **TaskProcessor**
   - Coordinates task processing and vector updates
   - Implements change detection
   - Manages enrichment and vector storage lifecycle

## Change Detection

The system uses a content-based hashing approach to detect meaningful changes:

```python
def get_content_hash(self) -> str:
    content = f"{self.content}|{self.description}|{self.priority}|{self.due.date if self.due else ''}"
    return hashlib.sha256(content.encode()).hexdigest()
```

Changes are detected by comparing the content hash of the new task state with the previous state.

## Vector Update Flow

1. **Change Detection**
   ```python
   if previous_task and task.get_content_hash() == previous_task.task.get_content_hash():
       return None  # No changes, skip update
   ```

2. **Vector Creation**
   - Task content and description are combined
   - Metadata is attached for retrieval
   - Document is created in LlamaIndex format

3. **Atomic Update**
   ```python
   # Delete old vector if exists
   if enriched_task.vector_metadata:
       self.index.delete(enriched_task.vector_metadata.doc_id)
   
   # Insert new vector
   doc = self._create_document(enriched_task.task)
   self.index.insert(doc)
   ```

## Metadata Storage

Each vector includes metadata for efficient retrieval:
```python
metadata = {
    "task_id": task.id,
    "project_id": task.project_id,
    "priority": task.priority,
    "due_date": task.due.date if task.due else None,
    "is_completed": task.is_completed
}
```

## Best Practices

1. **Change Detection**
   - Always check for changes before updating vectors
   - Use content hash to detect meaningful changes
   - Skip updates when content hasn't changed

2. **Atomic Updates**
   - Delete old vector before inserting new one
   - Maintain vector metadata for tracking
   - Handle errors to prevent inconsistent state

3. **Vector Storage**
   - Store relevant metadata with vectors
   - Use appropriate embedding model
   - Maintain timestamps for tracking

## Example Usage

```python
# Process a task update
enriched_task = task_processor.process_task(task, project, previous_task)

if enriched_task:  # Task was changed and updated
    print(f"Task {task.id} updated in vector store")
    print(f"Vector ID: {enriched_task.vector_metadata.doc_id}")
    print(f"Last Updated: {enriched_task.vector_metadata.last_updated}")
else:
    print(f"Task {task.id} unchanged, no update needed")
```

## Querying Tasks

The vector store enables semantic search and similarity matching for tasks. Here are common query patterns:

### Semantic Search
```python
# Search for similar tasks
query_text = "tasks related to machine learning projects"
query_results = vector_store.index.query(
    query_text,
    similarity_top_k=5  # Return top 5 similar tasks
)

# Process results
for node in query_results.nodes:
    task_id = node.metadata["task_id"]
    score = node.score
    print(f"Task {task_id} matched with score {score}")
```

### Filtered Search
```python
# Search with metadata filters
query_results = vector_store.index.query(
    "high priority tasks",
    filters={
        "priority": 4,  # High priority only
        "is_completed": False  # Incomplete tasks
    },
    similarity_top_k=10
)
```

### Task Clustering
```python
# Find tasks similar to a specific task
task_text = f"Task: {target_task.content}\nDescription: {target_task.description}"
similar_tasks = vector_store.index.query(
    task_text,
    similarity_top_k=5,
    filters={"project_id": target_task.project_id}  # Same project only
)
```

## Performance Considerations

1. **Index Size**
   - Monitor the size of your vector index
   - Consider periodic cleanup of completed tasks
   - Archive old tasks if needed

2. **Query Optimization**
   - Use metadata filters to reduce search space
   - Adjust `similarity_top_k` based on needs
   - Cache frequent queries if possible

3. **Update Frequency**
   - Batch updates when possible
   - Use change detection to minimize updates
   - Consider async updates for large batches 