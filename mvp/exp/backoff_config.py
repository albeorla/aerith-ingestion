"""Centralized backoff configuration and utilities."""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Any, Callable, Optional, Type, Union

import backoff

# TODO: Implement circuit breaker pattern for API failure protection
# TODO: Add request result caching for similar requests
# TODO: Add failure state tracking and persistence
# TODO: Implement smart retry strategies based on error types


class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    HALF_OPEN = "half_open"  # Testing if service recovered
    OPEN = "open"  # Circuit is open, fail fast


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker pattern."""

    failure_threshold: int = 5  # Number of failures before opening
    reset_timeout: float = 60.0  # Seconds to wait before half-open
    half_open_max_calls: int = 3  # Max calls in half-open state


class CircuitBreaker:
    """Circuit breaker implementation."""

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = 0
        self.half_open_calls = 0
        self.lock = asyncio.Lock()

    async def record_success(self):
        """Record a successful call."""
        async with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failures = 0
                self.half_open_calls = 0

    async def record_failure(self):
        """Record a failed call."""
        async with self.lock:
            self.failures += 1
            self.last_failure_time = time.time()

            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
            elif (
                self.state == CircuitState.CLOSED
                and self.failures >= self.config.failure_threshold
            ):
                self.state = CircuitState.OPEN

    async def allow_request(self) -> bool:
        """Check if request should be allowed."""
        async with self.lock:
            if self.state == CircuitState.CLOSED:
                return True

            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time >= self.config.reset_timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_calls = 0
                    return True
                return False

            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_calls < self.config.half_open_max_calls:
                    self.half_open_calls += 1
                    return True
                return False

            return False


class BackoffConfig:
    """Retry configuration with circuit breaker pattern."""

    # Default settings
    DEFAULT_MAX_TRIES = 5
    DEFAULT_INITIAL_WAIT = 30.0
    DEFAULT_MAX_WAIT = 300.0
    DEFAULT_FACTOR = 2.0

    def __init__(self):
        self.circuit_breaker = CircuitBreaker(CircuitBreakerConfig())

    @classmethod
    def exponential_backoff(
        cls,
        rate_limiter=None,
        max_tries: int = DEFAULT_MAX_TRIES,
        initial_wait: float = DEFAULT_INITIAL_WAIT,
        max_wait: float = DEFAULT_MAX_WAIT,
        max_time: Optional[float] = None,
        logger: Optional[Any] = None,
    ) -> Callable:
        """Exponential backoff with circuit breaker and rate limiting."""
        instance = cls()

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                if not await instance.circuit_breaker.allow_request():
                    raise Exception("Circuit breaker is open")

                if rate_limiter:
                    await rate_limiter.wait_for_capacity()

                last_error = None
                start_time = time.time()
                for attempt in range(max_tries):
                    try:
                        result = await func(*args, **kwargs)
                        await instance.circuit_breaker.record_success()
                        return result
                    except Exception as e:
                        last_error = e
                        await instance.circuit_breaker.record_failure()

                        error_str = str(e).lower()
                        if "429" in error_str and rate_limiter:
                            rate_limiter.start_cooldown()

                        if attempt == max_tries - 1:
                            if logger:
                                logger.error(f"Failed after {max_tries} attempts: {e}")
                            raise

                        wait = min(
                            initial_wait * (cls.DEFAULT_FACTOR**attempt), max_wait
                        )

                        if logger:
                            logger.warning(
                                f"Attempt {attempt + 1}/{max_tries} failed: {e}. "
                                f"Waiting {wait:.1f}s before retry"
                            )

                        await asyncio.sleep(wait)

                        if max_time and (time.time() - start_time) > max_time:
                            if logger:
                                logger.error(
                                    f"Exceeded maximum retry time of {max_time} seconds."
                                )
                            raise

                raise last_error

            return wrapper

        return decorator

    @classmethod
    def get_rate_limit_wait(cls, error_str: str) -> float:
        """Get wait time based on error type."""
        if "429" in error_str or "rate limit" in error_str:
            return cls.DEFAULT_INITIAL_WAIT
        elif "quota" in error_str:
            return cls.DEFAULT_MAX_WAIT
        return cls.DEFAULT_INITIAL_WAIT / 2

    @staticmethod
    def is_retryable_error(e: Exception) -> bool:
        """Determine if an error should trigger a retry."""
        error_str = str(e).lower()

        # Rate limits and quota issues
        if any(
            term in error_str
            for term in ["429", "rate limit", "quota", "resource exhausted"]
        ):
            return True

        # Server errors
        if any(code in error_str for code in ["500", "502", "503", "504"]):
            return True

        # Network/timeout/availability issues
        if any(
            term in error_str
            for term in [
                "timeout",
                "connection",
                "network",
                "server error",
                "unavailable",
                "overloaded",
            ]
        ):
            return True

        return False

    @classmethod
    def exponential_backoff_old(
        cls,
        rate_limiter=None,  # Optional RateLimiter instance
        max_tries: int = DEFAULT_MAX_TRIES,
        max_time: int = 1800,  # 30 minutes
        factor: float = DEFAULT_FACTOR,
        initial_wait: float = DEFAULT_INITIAL_WAIT,
        max_wait: float = DEFAULT_MAX_WAIT,
        jitter: Optional[Union[bool, Callable]] = backoff.full_jitter,
        logger: Optional[Any] = None,
    ) -> Callable:
        """Decorator for exponential backoff with rate limiting."""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            @backoff.on_exception(
                wait_gen=backoff.expo,
                exception=Exception,
                max_tries=max_tries,
                max_time=max_time,
                base=initial_wait,
                factor=factor,
                max_value=max_wait,
                jitter=jitter,
                giveup=lambda e: not cls.is_retryable_error(e),
                on_backoff=lambda details: cls._handle_backoff(
                    details, rate_limiter, logger
                ),
                on_giveup=lambda details: cls._log_giveup(details, logger),
            )
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                if rate_limiter:
                    # Wait for rate limiter before making request
                    await rate_limiter.wait_for_capacity()
                return await func(*args, **kwargs)

            return wrapper

        return decorator

    @classmethod
    def _handle_backoff(
        cls, details: dict, rate_limiter: Optional[Any], logger: Optional[Any]
    ) -> None:
        """Handle backoff with rate limiting."""
        error = details.get("exception")
        error_str = str(error).lower() if error else ""
        wait = details["wait"]
        tries = details["tries"]
        target = details["target"].__name__

        # Update rate limiter if provided
        if rate_limiter and "429" in error_str:
            rate_limiter.record_rate_limit()

        if logger:
            logger.warning(
                f"Backing off {target} for {wait:.1f}s "
                f"after {tries} tries. "
                f"Error: {error}"
            )

    @staticmethod
    def _log_backoff(details: dict, logger: Optional[Any]) -> None:
        """Log backoff attempts."""
        if logger:
            wait = details["wait"]
            tries = details["tries"]
            target = details["target"].__name__
            logger.warning(
                f"Backing off {target} for {wait:.1f}s "
                f"after {tries} tries. "
                f"Error: {details.get('exception')}"
            )

    @staticmethod
    def _log_giveup(details: dict, logger: Optional[Any]) -> None:
        """Log when giving up retries."""
        if logger:
            target = details["target"].__name__
            logger.error(
                f"Giving up on {target} after "
                f"{details['tries']} tries. "
                f"Last error: {details.get('exception')}"
            )
