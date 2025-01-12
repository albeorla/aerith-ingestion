"""
Base class providing automatic method tracing for derived classes.
"""

import inspect
from typing import Callable, Generic, ParamSpec, Type, TypeVar

from loguru import logger

from aerith_ingestion.core.logging_aspect import LogMethod

T = TypeVar("T", bound="TracedClass")
P = ParamSpec("P")
R = TypeVar("R")


def _wrap_method(method: Callable, level: str = "TRACE") -> Callable:
    """Wrap a method with the log_method decorator if not already wrapped."""
    if hasattr(method, "_logged"):
        return method

    wrapped = LogMethod(level=level)(method)
    wrapped._logged = True  # type: ignore
    return wrapped


class TracedClass:
    """Base class that automatically applies method tracing to all methods.

    Any class inheriting from this will automatically get method tracing on all
    its methods (except those starting with '_' unless explicitly decorated).

    Example:
        ```python
        class MyService(TracedClass):
            def process_data(self, data: dict) -> None:
                # This method will be automatically traced
                pass

            def _internal_helper(self) -> None:
                # This method will NOT be automatically traced
                # unless explicitly decorated with @log_method
                pass
        ```
    """

    def __init_subclass__(cls: Type[T]) -> None:
        """
        Automatically apply method tracing to all public methods of subclasses.

        This is called whenever a class inherits from TracedClass.
        """
        super().__init_subclass__()

        # Get all methods that aren't already logged
        for name, method in cls.__dict__.items():
            # Skip special methods, private methods (starting with '_'),
            # and already logged methods
            if (
                not name.startswith("_")
                and callable(method)
                and not hasattr(method, "_logged")
            ):

                # Wrap the method with logging
                setattr(cls, name, _wrap_method(method))

        logger.trace(f"Initialized traced class: {cls.__name__}")


class BaseService(Generic[P, R]):
    """
    Base class for all services.
    """

    def __init__(self, func: Callable[P, R]) -> None:
        self.func = func
        self.signature = inspect.signature(func)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        bound_arguments = self.signature.bind(*args, **kwargs)
        bound_arguments.apply_defaults()
        return self.func(*bound_arguments.args, **bound_arguments.kwargs)
