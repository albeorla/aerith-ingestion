"""Centralized error handling and recovery."""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ErrorSeverity(Enum):
    """Error severity levels."""

    LOW = "low"  # Non-critical errors that don't affect core functionality
    MEDIUM = "medium"  # Errors that affect some functionality but system can continue
    HIGH = "high"  # Critical errors that require immediate attention
    FATAL = "fatal"  # System cannot continue operation


@dataclass
class ErrorContext:
    """Context information for error tracking."""

    timestamp: float = field(default_factory=time.time)
    service: str = ""
    operation: str = ""
    request_id: str = ""
    user_id: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorRecord:
    """Complete error record for tracking and analysis."""

    error: Exception
    severity: ErrorSeverity
    context: ErrorContext
    stack_trace: str
    recovery_attempts: int = 0
    resolved: bool = False
    resolution_time: Optional[float] = None


class ErrorStore:
    """Storage and retrieval of error records."""

    def __init__(self, max_records: int = 1000):
        self.max_records = max_records
        self.records: List[ErrorRecord] = []
        self.lock = asyncio.Lock()

    async def add_record(self, record: ErrorRecord):
        """Add new error record with rotation."""
        async with self.lock:
            self.records.append(record)
            if len(self.records) > self.max_records:
                self.records.pop(0)

    async def mark_resolved(self, record: ErrorRecord, resolution_time: float):
        """Mark an error record as resolved."""
        async with self.lock:
            record.resolved = True
            record.resolution_time = resolution_time

    def get_unresolved_errors(
        self, severity: Optional[ErrorSeverity] = None
    ) -> List[ErrorRecord]:
        """Get unresolved errors, optionally filtered by severity."""
        return [
            r
            for r in self.records
            if not r.resolved and (severity is None or r.severity == severity)
        ]

    def export_to_json(self, filepath: str):
        """Export error records to JSON file."""
        with open(filepath, "w") as f:
            json.dump(
                [
                    {
                        "error": str(r.error),
                        "severity": r.severity.value,
                        "context": {
                            "timestamp": r.context.timestamp,
                            "service": r.context.service,
                            "operation": r.context.operation,
                            "request_id": r.context.request_id,
                            "user_id": r.context.user_id,
                            "additional_data": r.context.additional_data,
                        },
                        "stack_trace": r.stack_trace,
                        "recovery_attempts": r.recovery_attempts,
                        "resolved": r.resolved,
                        "resolution_time": r.resolution_time,
                    }
                    for r in self.records
                ],
                f,
                indent=2,
            )


class ErrorHandler:
    """Centralized error handling and recovery."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.error_store = ErrorStore()

    async def handle_error(
        self,
        error: Exception,
        context: ErrorContext,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    ) -> ErrorRecord:
        """Handle an error with full context."""
        import traceback

        # Create error record
        record = ErrorRecord(
            error=error,
            severity=severity,
            context=context,
            stack_trace=traceback.format_exc(),
        )

        # Log error with context
        self.logger.error(
            f"Error in {context.service}.{context.operation}: {error}",
            extra={
                "error_context": context.__dict__,
                "severity": severity.value,
                "stack_trace": record.stack_trace,
            },
        )

        # Store error record
        await self.error_store.add_record(record)

        # Handle based on severity
        if severity == ErrorSeverity.FATAL:
            self.logger.critical(
                "Fatal error encountered - system shutdown may be required"
            )
            # Implement system shutdown logic if needed

        return record

    async def attempt_recovery(
        self, record: ErrorRecord, recovery_func: Optional[callable] = None
    ) -> bool:
        """Attempt to recover from an error."""
        record.recovery_attempts += 1

        try:
            if recovery_func:
                await recovery_func()

            await self.error_store.mark_resolved(record, time.time())
            self.logger.info(
                f"Successfully recovered from error in "
                f"{record.context.service}.{record.context.operation}"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Recovery attempt failed for error in "
                f"{record.context.service}.{record.context.operation}: {e}"
            )
            return False

    def export_error_report(self, filepath: str):
        """Export error records to file."""
        self.error_store.export_to_json(filepath)
        self.logger.info(f"Exported error report to {filepath}")
