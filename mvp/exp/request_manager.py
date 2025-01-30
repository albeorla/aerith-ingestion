"""Request management with smart batching and deduplication."""

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar

from monitoring import MonitoringDashboard

T = TypeVar("T")  # Type for request payload
R = TypeVar("R")  # Type for response


class RequestPriority(Enum):
    """Priority levels for requests."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class BatchConfig:
    """Configuration for smart batching."""

    max_batch_size: int = 50
    max_wait_time: float = 2.0  # seconds
    min_batch_size: int = 5
    max_token_limit: int = 8000  # Adjust based on API limits


@dataclass
class Request(Generic[T]):
    """Request container with metadata."""

    payload: T
    priority: RequestPriority
    timestamp: float = field(default_factory=time.time)
    request_id: str = field(
        default_factory=lambda: hashlib.md5(str(time.time()).encode()).hexdigest()
    )
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RequestBatch(Generic[T]):
    """Batch of requests."""

    requests: List[Request[T]]
    total_tokens: int = 0
    batch_id: str = field(
        default_factory=lambda: hashlib.md5(str(time.time()).encode()).hexdigest()
    )


class RequestCache:
    """Cache for request deduplication."""

    def __init__(self, ttl: float = 300.0):  # 5 minutes default TTL
        self.cache: Dict[str, Any] = {}
        self.ttl = ttl
        self.lock = asyncio.Lock()

    def _generate_cache_key(self, request: Request) -> str:
        """Enhanced cache key with method-specific parameters"""
        key_data = {
            "method": (
                request.payload.get("method")
                if isinstance(request.payload, dict)
                else None
            ),
            "payload": request.payload,
            "metadata": {
                "priority": request.priority.value,
                "source": request.metadata.get("source", "unknown"),
            },
        }

        # Include method-specific parameters
        if key_data["method"] == "categorize_gtd_level":
            key_data["content_hash"] = hashlib.md5(
                request.payload.get("task_content", "").encode()
            ).hexdigest()

        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()

    async def get(self, request: Request) -> Optional[Any]:
        """Get cached response if exists and not expired."""
        async with self.lock:
            key = self._generate_cache_key(request)
            if key in self.cache:
                timestamp, response = self.cache[key]
                if time.time() - timestamp <= self.ttl:
                    return response
                del self.cache[key]
        return None

    async def set(self, request: Request, response: Any):
        """Cache response with timestamp."""
        async with self.lock:
            key = self._generate_cache_key(request)
            self.cache[key] = (time.time(), response)

    async def cleanup(self):
        """Remove expired entries."""
        async with self.lock:
            now = time.time()
            self.cache = {k: v for k, v in self.cache.items() if now - v[0] <= self.ttl}


class RequestManager(Generic[T, R]):
    """Manages request batching, deduplication, and processing."""

    def __init__(
        self,
        batch_processor: Callable[[RequestBatch[T]], List[R]],
        batch_config: BatchConfig = BatchConfig(),
        logger: Optional[logging.Logger] = None,
        monitor: MonitoringDashboard = None,
    ):
        self.batch_processor = batch_processor
        self.config = batch_config
        self.logger = logger or logging.getLogger(__name__)
        self.cache = RequestCache()
        self.monitor = monitor

        # Separate queues for different priorities
        self.queues = {
            RequestPriority.HIGH: asyncio.Queue(),
            RequestPriority.MEDIUM: asyncio.Queue(),
            RequestPriority.LOW: asyncio.Queue(),
        }

        # Batch processing tasks
        self.processing_tasks = []
        self.is_running = False

    def _estimate_tokens(self, request: Request[T]) -> int:
        """Estimate token count for request. Override for specific implementations."""
        # Simple estimation - override for more accurate counting
        return len(str(request.payload)) // 4

    async def submit_request(self, request: Request[T]) -> R:
        """Submit a request for processing."""
        # Check cache first
        cached_response = await self.cache.get(request)
        if cached_response is not None:
            self.logger.debug(f"Cache hit for request {request.request_id}")
            return cached_response

        # Add to appropriate queue
        await self.queues[request.priority].put(request)
        self.logger.debug(
            f"Queued request {request.request_id} with priority {request.priority}"
        )

        # Ensure processing is running
        if not self.is_running:
            self.start_processing()

        # Wait for and return result
        # Note: In a real implementation, you'd want to implement a way to track
        # and return specific results to specific requests
        return await self._wait_for_result(request)

    async def _wait_for_result(self, request: Request[T]) -> R:
        """Wait for request processing. Implement result tracking/waiting logic."""
        # This is a simplified version - implement proper result tracking
        await asyncio.sleep(0.1)  # Simulated wait
        return None  # Replace with actual result tracking

    def start_processing(self):
        """Start batch processing tasks."""
        if not self.is_running:
            self.is_running = True
            for priority in RequestPriority:
                task = asyncio.create_task(self._process_batch_loop(priority))
                self.processing_tasks.append(task)

    async def stop_processing(self):
        """Stop batch processing."""
        self.is_running = False
        await asyncio.gather(*self.processing_tasks)
        self.processing_tasks.clear()

    async def _process_batch_loop(self, priority: RequestPriority):
        """Continuous batch processing for a priority level."""
        queue = self.queues[priority]

        while self.is_running:
            try:
                batch = await self._collect_batch(queue)
                if not batch.requests:
                    continue

                self.logger.debug(
                    f"Processing batch {batch.batch_id} with "
                    f"{len(batch.requests)} requests"
                )

                # Process batch
                results = await self.batch_processor(batch)

                # Cache results
                for request, result in zip(batch.requests, results):
                    await self.cache.set(request, result)

            except Exception as e:
                self.logger.error(f"Error processing batch: {e}")
                await asyncio.sleep(1)  # Prevent tight loop on errors

    async def _collect_batch(self, queue: asyncio.Queue) -> RequestBatch[T]:
        """Collect requests into a batch."""
        batch = RequestBatch(requests=[])

        try:
            # Dynamic batch size adjustment based on latency
            current_latency = 0.0
            if (
                self.monitor
                and self.monitor.metrics["gemini_service"].avg_processing_time
            ):
                current_latency = self.monitor.metrics[
                    "gemini_service"
                ].avg_processing_time

            # Define latency thresholds and batch size adjustments
            low_latency_threshold = 0.5  # seconds, example value
            high_latency_threshold = 2.0  # seconds, example value
            base_batch_size = self.config.max_batch_size  # Store base batch size

            if current_latency < low_latency_threshold:
                self.config.max_batch_size = int(
                    base_batch_size * 1.5
                )  # Increase batch size by 50%
                self.logger.debug(
                    f"Low latency ({current_latency:.2f}s), increasing batch size to {self.config.max_batch_size}"
                )
            elif current_latency > high_latency_threshold:
                self.config.max_batch_size = int(
                    base_batch_size * 0.75
                )  # Decrease batch size by 25%
                self.config.max_batch_size = max(
                    self.config.min_batch_size, self.config.max_batch_size
                )  # Ensure not smaller than min_batch_size
                self.logger.debug(
                    f"High latency ({current_latency:.2f}s), decreasing batch size to {self.config.max_batch_size}"
                )
            else:
                self.config.max_batch_size = base_batch_size  # Revert to base batch size if latency is within acceptable range

            # Get first request or wait
            first_request = await queue.get()
            batch.requests.append(first_request)
            batch.total_tokens += self._estimate_tokens(first_request)

            # Try to fill batch
            batch_start = time.time()
            while (
                len(batch.requests) < self.config.max_batch_size
                and batch.total_tokens < self.config.max_token_limit
                and time.time() - batch_start < self.config.max_wait_time
            ):
                try:
                    request = queue.get_nowait()
                    tokens = self._estimate_tokens(request)

                    if batch.total_tokens + tokens <= self.config.max_token_limit:
                        batch.requests.append(request)
                        batch.total_tokens += tokens
                    else:
                        # Put back if would exceed token limit
                        await queue.put(request)
                        break

                except asyncio.QueueEmpty:
                    if len(batch.requests) >= self.config.min_batch_size:
                        break
                    await asyncio.sleep(0.1)

        except Exception as e:
            self.logger.error(f"Error collecting batch: {e}")

        return batch
