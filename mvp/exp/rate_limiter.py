"""Simple rate limiting and quota management."""

import asyncio
import logging
import time
from dataclasses import dataclass
from threading import Lock
from typing import Any, Optional

# TODO: Implement dynamic quota adjustments based on API response headers
# TODO: Add request deduplication logic to avoid redundant API calls
# TODO: Implement request priority queue for better throughput management
# TODO: Add metrics collection for rate limit monitoring


@dataclass
class QuotaConfig:
    """Configuration for API quota management."""

    # Basic rate limiting
    requests_per_minute: int = 30
    min_delay_between_requests: float = 2.0
    cooldown_duration: float = 30.0

    # Enhanced controls
    max_concurrent_requests: int = 5
    max_request_size_bytes: int = 1024 * 1024  # 1MB
    max_content_length: int = 10000  # characters

    # Priority and deduplication
    priority_levels: dict = None  # Maps priority level to quota allocation
    dedup_window_seconds: float = 300.0  # 5 minutes

    # Quota distribution
    endpoint_quotas: dict = None  # Maps endpoint to specific quota limits

    def __post_init__(self):
        if self.priority_levels is None:
            self.priority_levels = {
                "high": 0.5,  # 50% of quota
                "medium": 0.3,  # 30% of quota
                "low": 0.2,  # 20% of quota
            }
        if self.endpoint_quotas is None:
            self.endpoint_quotas = {}  # Default to no endpoint-specific quotas


class RateLimiter:
    """Advanced rate limiting with deduplication and priority queues."""

    def __init__(self, quota_config: QuotaConfig):
        self.config = quota_config
        self.lock = Lock()
        self.request_timestamps = []
        self.last_request_time = 0.0
        self.cooldown_until = 0.0
        self.logger = logging.getLogger(__name__)

        # Request deduplication
        self.recent_requests = {}  # hash -> (timestamp, result)

        # Concurrent request tracking
        self.active_requests = 0
        self.request_semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)

        # Priority queues
        self.priority_queues = {
            priority: asyncio.Queue() for priority in self.config.priority_levels.keys()
        }

    def _hash_request(self, endpoint: str, params: dict) -> str:
        """Create a hash for request deduplication."""
        import hashlib
        import json

        key = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key.encode()).hexdigest()

    def _clean_old_requests(self):
        """Remove expired entries from deduplication cache."""
        now = time.time()
        self.recent_requests = {
            k: v
            for k, v in self.recent_requests.items()
            if now - v[0] < self.config.dedup_window_seconds
        }

    async def check_dedup(self, endpoint: str, params: dict) -> Optional[Any]:
        """Check if request can be deduplicated."""
        req_hash = self._hash_request(endpoint, params)
        with self.lock:
            self._clean_old_requests()
            if req_hash in self.recent_requests:
                timestamp, result = self.recent_requests[req_hash]
                if time.time() - timestamp < self.config.dedup_window_seconds:
                    self.logger.info(f"Request deduplicated: {endpoint}")
                    return result
        return None

    def cache_response(self, endpoint: str, params: dict, result: Any):
        """Cache response for deduplication."""
        req_hash = self._hash_request(endpoint, params)
        with self.lock:
            self.recent_requests[req_hash] = (time.time(), result)

    async def wait_for_capacity(self, priority: str = "medium") -> bool:
        """Wait until capacity is available, respecting priority."""
        if priority not in self.config.priority_levels:
            raise ValueError(f"Invalid priority level: {priority}")

        # Wait for concurrent request slot
        async with self.request_semaphore:
            with self.lock:
                self.active_requests += 1

            try:
                while True:
                    with self.lock:
                        now = time.time()

                        # Handle cooldown
                        if now < self.cooldown_until:
                            wait_time = self.cooldown_until - now
                            self.logger.warning(
                                f"In cooldown. Waiting {wait_time:.1f}s"
                            )
                            await asyncio.sleep(wait_time)
                            continue

                        # Clean old timestamps
                        self.request_timestamps = [
                            ts for ts in self.request_timestamps if now - ts < 60
                        ]

                        # Check priority-based quota
                        quota_share = self.config.priority_levels[priority]
                        max_requests = int(
                            self.config.requests_per_minute * quota_share
                        )
                        priority_requests = len(
                            [
                                ts
                                for ts in self.request_timestamps[-max_requests:]
                                if now - ts < 60
                            ]
                        )

                        if priority_requests >= max_requests:
                            wait_time = 60 - (
                                now - self.request_timestamps[-max_requests]
                            )
                            self.logger.info(
                                f"Priority {priority} quota reached. "
                                f"Waiting {wait_time:.1f}s"
                            )
                            await asyncio.sleep(wait_time)
                            continue

                        # Enforce minimum delay
                        if (
                            now - self.last_request_time
                            < self.config.min_delay_between_requests
                        ):
                            await asyncio.sleep(self.config.min_delay_between_requests)
                            continue

                        # Record request
                        self.request_timestamps.append(now)
                        self.last_request_time = now
                        return True
            finally:
                with self.lock:
                    self.active_requests -= 1

    def start_cooldown(self, duration: Optional[float] = None):
        """Enter cooldown after rate limit hit."""
        with self.lock:
            self.cooldown_until = time.time() + (
                duration or self.config.cooldown_duration
            )
            self.logger.warning(
                f"Entering cooldown for {duration or self.config.cooldown_duration:.1f}s"
            )
