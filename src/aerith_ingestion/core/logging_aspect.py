"""
Logging aspects for the application using decorator pattern.
"""

import functools
import inspect
import time
from datetime import datetime
from typing import Any, Callable, ParamSpec, TypeVar

from loguru import logger

T = TypeVar("T", bound=Callable[..., Any])
P = ParamSpec("P")
R = TypeVar("R")


def log_trace(level: str = "DEBUG") -> Callable[[T], T]:
    """
    Decorator for tracing function calls with parameters and execution time.

    Args:
        level: The logging level to use. Defaults to "DEBUG".

    Returns:
        Decorated function with logging.
    """

    def decorator(func: T) -> T:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Get function signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Format arguments for logging
            args_str = ", ".join(
                f"{k}={repr(v)}" for k, v in bound_args.arguments.items()
            )

            # Log entry
            logger.opt(depth=1).log(level, f"Entering {func.__name__}({args_str})")

            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                elapsed = time.perf_counter() - start_time

                # Log success
                logger.opt(depth=1).log(
                    level,
                    f"Exiting {func.__name__} - Completed in {elapsed:.4f}s - "
                    f"Result: {repr(result)[:100]}",
                )
                return result
            except Exception as e:
                elapsed = time.perf_counter() - start_time

                # Log error
                logger.opt(depth=1).log(
                    level,
                    f"Error in {func.__name__} after {elapsed:.4f}s - "
                    f"Exception: {type(e).__name__}: {str(e)}",
                )
                raise

        return wrapper  # type: ignore

    return decorator


def LogMethod(level: str = "DEBUG") -> Callable[[T], T]:
    """
    Decorator for class methods, handling 'self' parameter.

    Args:
        level: The logging level to use. Defaults to "DEBUG".

    Returns:
        Decorated method with logging.
    """

    def decorator(func: T) -> T:
        @functools.wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            class_name = self.__class__.__name__
            method_name = func.__name__

            # Get method signature excluding 'self'
            sig = inspect.signature(func)
            bound_args = sig.bind(self, *args, **kwargs)
            bound_args.apply_defaults()

            # Format arguments for logging (excluding self)
            args_dict = dict(bound_args.arguments)
            args_dict.pop("self", None)
            args_str = ", ".join(f"{k}={repr(v)}" for k, v in args_dict.items())

            # Log entry
            logger.opt(depth=1).log(
                level, f"Entering {class_name}.{method_name}({args_str})"
            )

            start_time = time.perf_counter()
            try:
                result = func(self, *args, **kwargs)
                elapsed = time.perf_counter() - start_time

                # Log success
                success_msg = (
                    f"Exiting {class_name}.{method_name} - "
                    f"Completed in {elapsed:.4f}s - "
                    f"Result: {repr(result)[:100]}"
                )
                logger.opt(depth=1).log(level, success_msg)
                return result
            except Exception as e:
                elapsed = time.perf_counter() - start_time

                # Log error
                error_msg = (
                    f"Error in {class_name}.{method_name} "
                    f"after {elapsed:.4f}s - "
                    f"Exception: {type(e).__name__}: {str(e)}"
                )
                logger.opt(depth=1).log(level, error_msg)
                raise

        return wrapper  # type: ignore

    return decorator


class LoggingAspect:
    def __init__(self, func: Callable[P, R]) -> None:
        self.func = func
        self.signature = inspect.signature(func)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        bound_arguments = self.signature.bind(*args, **kwargs)
        bound_arguments.apply_defaults()

        log_params = {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "message": f"Calling {self.func.__name__}",
            "parameters": {
                k: v for k, v in bound_arguments.arguments.items() if k != "self"
            },
        }

        logger.bind(**log_params).info(log_params["message"])

        try:
            result = self.func(*bound_arguments.args, **bound_arguments.kwargs)
            logger.bind(
                return_value=result,
                execution_time=(
                    datetime.now() - datetime.fromisoformat(log_params["timestamp"])
                ).total_seconds(),
            ).info(f"Finished {self.func.__name__}")
            return result
        except Exception as e:
            logger.bind(exception=str(e)).error(f"Error in {self.func.__name__}")
            raise
