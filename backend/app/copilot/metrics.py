"""
PRAHARI Copilot Observability & Latency Metrics
Tracks real-time system metrics, latency percentiles, and operational counters.
"""
import time
import numpy as np
from typing import Dict, Any, List
from collections import deque


class CopilotMetricsTracker:
    """In-memory low-overhead operational metrics collector."""

    def __init__(self, max_samples: int = 1000):
        self.total_requests: int = 0
        self.fast_path_requests: int = 0
        self.llm_path_requests: int = 0
        self.offline_fallback_requests: int = 0
        self.error_count: int = 0
        self.timeout_count: int = 0

        self.latencies: deque = deque(maxlen=max_samples)
        self.tool_latencies: Dict[str, deque] = {}
        self.tool_call_counts: Dict[str, int] = {}
        self.retrieval_latencies: deque = deque(maxlen=max_samples)
        self.llm_latencies: deque = deque(maxlen=max_samples)
        self.ttft_latencies: deque = deque(maxlen=max_samples)

    def record_request(
        self,
        latency_ms: float,
        is_fast_path: bool = False,
        is_llm: bool = False,
        is_fallback: bool = False,
        is_error: bool = False,
        is_timeout: bool = False
    ):
        self.total_requests += 1
        if is_fast_path:
            self.fast_path_requests += 1
        if is_llm:
            self.llm_path_requests += 1
        if is_fallback:
            self.offline_fallback_requests += 1
        if is_error:
            self.error_count += 1
        if is_timeout:
            self.timeout_count += 1

        self.latencies.append(latency_ms)

    def record_tool_call(self, tool_name: str, latency_ms: float):
        self.tool_call_counts[tool_name] = self.tool_call_counts.get(tool_name, 0) + 1
        if tool_name not in self.tool_latencies:
            self.tool_latencies[tool_name] = deque(maxlen=200)
        self.tool_latencies[tool_name].append(latency_ms)

    def record_retrieval(self, latency_ms: float):
        self.retrieval_latencies.append(latency_ms)

    def record_llm(self, latency_ms: float, ttft_ms: float = 0.0):
        self.llm_latencies.append(latency_ms)
        if ttft_ms > 0:
            self.ttft_latencies.append(ttft_ms)

    def get_summary(self, cache_hits: int = 0) -> Dict[str, Any]:
        l_list = list(self.latencies)
        if l_list:
            avg_lat = float(np.mean(l_list))
            p50 = float(np.percentile(l_list, 50))
            p95 = float(np.percentile(l_list, 95))
            p99 = float(np.percentile(l_list, 99))
        else:
            avg_lat, p50, p95, p99 = 0.0, 0.0, 0.0, 0.0

        return {
            "total_requests": self.total_requests,
            "fast_path_requests": self.fast_path_requests,
            "llm_path_requests": self.llm_path_requests,
            "offline_fallback_requests": self.offline_fallback_requests,
            "error_count": self.error_count,
            "timeout_count": self.timeout_count,
            "avg_latency_ms": round(avg_lat, 2),
            "p50_latency_ms": round(p50, 2),
            "p95_latency_ms": round(p95, 2),
            "p99_latency_ms": round(p99, 2),
            "cache_hits": cache_hits,
            "tool_call_counts": dict(self.tool_call_counts)
        }


copilot_metrics = CopilotMetricsTracker()
