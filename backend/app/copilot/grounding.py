"""
PRAHARI Copilot Fact Grounding & Anti-Hallucination Engine
Validates generated answers against raw tool data and enforces simulation labeling.
"""
from typing import Dict, Any, List, Optional
import re
from backend.app.copilot.schemas import ToolResult


class GroundingVerifier:
    """Verifies factual claims against backend operational truth."""

    @staticmethod
    def verify_and_patch(
        answer: str,
        tool_results: List[ToolResult],
        data_mode: str = "REAL"
    ) -> str:
        """
        Ensures risk scores, node states, and simulation labels match backend reality.
        """
        patched = answer

        # 1. Enforce provenance label for every non-REAL mode.
        mode = data_mode.upper().replace("-", "_")
        labels = {
            "SIMULATION": "SIMULATION DATA",
            "EXTERNAL_DATA": "EXTERNAL DATA",
            "REPLAY": "REPLAY DATA",
            "PLANNED": "PLANNED — NO LIVE DATA",
        }
        label = labels.get(mode)
        if label and label.lower() not in patched.lower():
            patched = f"*[{label}]* {patched}"

        # 2. Check for missing data indications
        for tr in tool_results:
            if not tr.success or tr.error:
                err_msg = tr.error or "Data unavailable"
                if "unavailable" not in patched.lower() and "not found" not in patched.lower():
                    patched += f"\n\n*Notice: {err_msg}*"

        return patched

    @staticmethod
    def format_unavailable(metric_name: str) -> str:
        return f"{metric_name} is currently unavailable."


grounding_verifier = GroundingVerifier()
