"""
Logging aspects for the application using decorator pattern.
"""

import functools
import inspect
import time
from typing import Any, Callable, ParamSpec, TypeVar

from loguru import logger

T = TypeVar("T", bound=Callable[..., Any])
P = ParamSpec("P")
R = TypeVar("R")


def LogMethod(level: str = "TRACE") -> Callable[[T], T]:
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
