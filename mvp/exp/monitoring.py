"""Monitoring and metrics collection."""

import time
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ServiceMetrics:
    """Container for service-level metrics."""

    request_count: int = 0
    cache_hits: int = 0
    error_count: int = 0
    avg_processing_time: float = 0.0
    active_requests: int = 0
    throughput_1min: float = 0.0


class MonitoringDashboard:
    """Real-time monitoring dashboard."""

    def __init__(self):
        self.metrics: Dict[str, ServiceMetrics] = {
            "gemini_service": ServiceMetrics(),
            "request_manager": ServiceMetrics(),
            "gtd_processor": ServiceMetrics(),
            "data_storage": ServiceMetrics(),
            "todoist_service": ServiceMetrics(),
        }
        self.start_time = time.monotonic()

    def log_request(self, service: str):
        self.metrics[service].request_count += 1

    def log_cache_hit(self, service: str):
        self.metrics[service].cache_hits += 1

    def log_error(self, service: str):
        self.metrics[service].error_count += 1

    def update_processing_time(self, service: str, duration: float):
        metrics = self.metrics[service]
        metrics.avg_processing_time = (
            metrics.avg_processing_time * (metrics.request_count - 1) + duration
        ) / metrics.request_count

    def update_throughput(self):
        """Calculate throughput for all services"""
        for service, metrics in self.metrics.items():
            # Simple EWMA calculation for throughput
            metrics.throughput_1min = (
                0.8 * metrics.throughput_1min + 0.2 * metrics.request_count
            )

    def get_metrics_report(self) -> str:
        """Generate formatted metrics report."""
        report = []
        for service, metrics in self.metrics.items():
            cache_hit_rate = (
                (metrics.cache_hits / metrics.request_count * 100)
                if metrics.request_count > 0
                else 0
            )
            report.append(
                f"{service.upper()} METRICS:\n"
                f"• Active Requests: {metrics.active_requests}\n"
                f"• Throughput (1m): {metrics.throughput_1min:.1f}/min\n"
                f"• Requests: {metrics.request_count}\n"
                f"• Cache Hit Rate: {cache_hit_rate:.1f}%\n"
                f"• Errors: {metrics.error_count}\n"
                f"• Avg Processing Time: {metrics.avg_processing_time:.2f}s"
            )
        return "\n\n".join(report)

    def check_alert_conditions(self) -> List[str]:
        alerts = []
        for service, metrics in self.metrics.items():
            if metrics.error_count / metrics.request_count > 0.05:
                alerts.append(f"{service} error rate >5%")
            if metrics.avg_processing_time > 5:
                alerts.append(f"{service} avg processing time >5s")
        return alerts
