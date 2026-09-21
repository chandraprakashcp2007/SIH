"""
PRAHARI Copilot Tool Executor
Executes tools concurrently with timeouts, caching, metrics recording, and structured responses.
"""
import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.copilot.schemas import ToolResult, ToolCallRecord
from backend.app.copilot.tool_registry import tool_registry, ToolDefinition
from backend.app.copilot.cache import copilot_cache
from backend.app.copilot.metrics import copilot_metrics
from gateway.simulator import prahari_sim
from backend.app.core.config import settings


class ToolExecutor:
    """Safely executes internal tools with parallel execution and circuit-breaking."""

    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        db: Optional[AsyncSession] = None,
        use_cache: bool = True
    ) -> ToolResult:
        t_def = tool_registry.get(tool_name)
        if not t_def:
            return ToolResult(
                success=False,
                tool=tool_name,
                error=f"Tool '{tool_name}' not registered."
            )

        # Check in-memory cache
        cache_key = f"tool:{tool_name}:{str(sorted(arguments.items()))}"
        if use_cache and settings.COPILOT_CACHE_ENABLED:
            cached_val = copilot_cache.get(cache_key)
            if cached_val is not None:
                return cached_val

        start_time = time.perf_counter()
        data_mode = "SIMULATION" if prahari_sim.active_scenario != "REAL_HARDWARE" else "REAL"

        try:
            # Prepare arguments
            call_kwargs = dict(arguments)
            if t_def.requires_db:
                call_kwargs["db"] = db

            timeout_sec = float(settings.COPILOT_TOOL_TIMEOUT_MS) / 1000.0
            raw_result = await asyncio.wait_for(
                t_def.handler(**call_kwargs),
                timeout=timeout_sec
            )

            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            copilot_metrics.record_tool_call(tool_name, latency_ms)

            # Check if raw_result indicated an error
            err = None
            if isinstance(raw_result, dict) and "error" in raw_result:
                err = raw_result.get("error")

            result = ToolResult(
                success=err is None,
                tool=tool_name,
                data_mode=data_mode,
                timestamp=datetime.now(timezone.utc).isoformat(),
                data=raw_result if isinstance(raw_result, (dict, list)) else {"value": raw_result},
                error=err
            )

            # Store in cache if successful
            if result.success and use_cache and settings.COPILOT_CACHE_ENABLED:
                copilot_cache.set(cache_key, result, ttl_seconds=t_def.cache_ttl_sec)

            return result

        except asyncio.TimeoutError:
            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            copilot_metrics.record_tool_call(tool_name, latency_ms)
            return ToolResult(
                success=False,
                tool=tool_name,
                data_mode=data_mode,
                error=f"Tool '{tool_name}' timed out after {settings.COPILOT_TOOL_TIMEOUT_MS}ms."
            )
        except Exception as e:
            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            copilot_metrics.record_tool_call(tool_name, latency_ms)
            return ToolResult(
                success=False,
                tool=tool_name,
                data_mode=data_mode,
                error=f"Execution error in '{tool_name}': {str(e)}"
            )

    async def execute_parallel(
        self,
        tool_invocations: List[Dict[str, Any]],
        db: Optional[AsyncSession] = None
    ) -> List[ToolResult]:
        """Runs multiple independent tools concurrently via asyncio.gather."""
        tasks = [
            self.execute_tool(
                tool_name=inv["name"],
                arguments=inv.get("arguments", {}),
                db=db
            )
            for inv in tool_invocations
        ]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        return list(results)


tool_executor = ToolExecutor()
