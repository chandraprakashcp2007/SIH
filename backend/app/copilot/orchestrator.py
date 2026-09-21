"""
PRAHARI Copilot Orchestrator
Master coordinator executing intent routing, fast-path shortcuts, concurrent tools,
RAG retrieval, LLM failover, grounding, and streaming.
"""
import time
import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.copilot.schemas import (
    ChatRequest,
    ChatResponse,
    StructuredComponent,
    ToolCallRecord,
    ToolResult
)
from backend.app.copilot.safety import safety_engine
from backend.app.copilot.validation import validate_user_query
from backend.app.copilot.memory import conversation_memory
from backend.app.copilot.intent import classify_intent, IntentMatch
from backend.app.copilot.planner import query_planner
from backend.app.copilot.tool_executor import tool_executor
from backend.app.copilot.retrieval import knowledge_retriever
from backend.app.copilot.context_builder import context_builder
from backend.app.copilot.grounding import grounding_verifier
from backend.app.copilot.citations import resolve_sources_from_tools
from backend.app.copilot.response_generator import response_generator
from backend.app.copilot.fallback import deterministic_fallback
from backend.app.copilot.session_store import session_store
from backend.app.copilot.metrics import copilot_metrics
from backend.app.copilot.cache import copilot_cache
from backend.app.copilot.providers import (
    LLMProvider,
    LocalEdgeAdapter,
    OpenAICompatibleAdapter
)
from backend.app.core.config import settings
from gateway.simulator import prahari_sim

logger = logging.getLogger("prahari.copilot.orchestrator")


class CopilotOrchestrator:
    """Orchestrates end-to-end grounded operational inquiries."""

    def __init__(self):
        self.local_provider = LocalEdgeAdapter(model_name="local-expert-v1")
        self.online_provider: Optional[LLMProvider] = None
        self._init_online_provider()

    def _init_online_provider(self):
        if settings.LLM_PROVIDER in ("OPENAI", "GEMINI", "OLLAMA") or settings.LLM_API_KEY:
            self.online_provider = OpenAICompatibleAdapter(
                api_key=settings.LLM_API_KEY,
                base_url=settings.LLM_BASE_URL,
                model=settings.LLM_MODEL,
                timeout_seconds=float(settings.LLM_TIMEOUT_SECONDS)
            )

    async def handle_query(
        self,
        db: AsyncSession,
        req: ChatRequest,
        user_id: str = "operator"
    ) -> ChatResponse:
        """Processes query through fast-path or LLM with guaranteed offline fallback."""
        start_time = time.perf_counter()
        req_id = f"REQ-{uuid.uuid4().hex[:8].upper()}"

        # 1. Validation & Safety Sanitization
        sanitized_text = validate_user_query(req.message)
        clean_text = safety_engine.sanitize_input(sanitized_text)

        # 2. Session Context & Memory
        session = await session_store.get_or_create_session(db, session_id=req.session_id, user_id=user_id)
        session_id = session.id

        resolved_query, last_node = conversation_memory.resolve_pronouns(clean_text, session_id)

        # 3. Fast Intent Classification
        intent_match = classify_intent(resolved_query, session_node=last_node)

        # Update memory context with detected entities
        detected_node = intent_match.entities.get("node_id")
        conversation_memory.get_or_create(session_id).update(
            node_id=detected_node,
            intent=intent_match.intent
        )

        # 4. Tool Planning
        tool_plan = query_planner.plan_tools_for_intent(intent_match)

        # 5. Concurrent Tool Execution
        tool_results = await tool_executor.execute_parallel(tool_plan, db=db)

        # Determine data mode: REAL or SIMULATION
        is_simulation = prahari_sim.active_scenario != "REAL_HARDWARE"
        data_mode = "SIMULATION" if is_simulation else "REAL"

        # 6. Source Attribution
        executed_tool_names = [tr.tool for tr in tool_results]
        sources = resolve_sources_from_tools(executed_tool_names, is_simulation=is_simulation)

        # 7. Fast-Path Deterministic Route vs LLM Route
        is_fast_path = (
            settings.COPILOT_FAST_PATH and
            intent_match.fast_path_eligible and
            not req.fast_path_only is False and
            (settings.COPILOT_MODE != "online_only")
        )

        answer_text = ""
        components: List[StructuredComponent] = []
        provider_used = "LOCAL_DETERMINISTIC"
        mode_used = "LOCAL_ASSISTANT"

        if is_fast_path or not self.online_provider or not self.online_provider.is_configured():
            # Fast-path deterministic response in <150ms!
            answer_text, components = deterministic_fallback.format_fallback_response(
                intent_match=intent_match,
                tool_results=tool_results,
                data_mode=data_mode
            )
            mode_used = "LOCAL_ASSISTANT"
            provider_used = "LOCAL_DETERMINISTIC"

        else:
            # Complex query requiring RAG synthesis or external model
            doc_chunks = []
            if settings.RAG_ENABLED and intent_match.intent == "DOCUMENTATION_QUERY":
                doc_chunks = knowledge_retriever.retrieve(resolved_query, top_k=settings.COPILOT_MAX_CONTEXT_CHUNKS)

            # Retrieve recent conversation history
            recent_msgs = await session_store.get_messages(db, session_id=session_id, limit=6, user_id=user_id)
            history_tuples = [{"role": m["role"], "content": m["content"]} for m in recent_msgs]

            messages = context_builder.assemble_context(
                user_query=resolved_query,
                tool_results=[tr.model_dump() for tr in tool_results],
                doc_chunks=doc_chunks,
                history_messages=history_tuples,
                data_mode=data_mode
            )

            try:
                # Attempt primary online LLM provider
                llm_start = time.perf_counter()
                llm_resp = await self.online_provider.generate(messages)
                llm_lat = (time.perf_counter() - llm_start) * 1000.0
                copilot_metrics.record_llm(llm_lat)

                answer_text = llm_resp.get("content", "")
                provider_used = llm_resp.get("provider", "OPENAI_COMPATIBLE")
                mode_used = "ONLINE_AI"

            except Exception as e:
                logger.warning(f"Online LLM failed or timed out: {e}. Gracefully failing over to Local Assistant.")
                # Automatic failover to local assistant without crashing
                answer_text, components = deterministic_fallback.format_fallback_response(
                    intent_match=intent_match,
                    tool_results=tool_results,
                    data_mode=data_mode
                )
                provider_used = "LOCAL_DETERMINISTIC"
                mode_used = "LOCAL_ASSISTANT"
                copilot_metrics.record_request(
                    latency_ms=0,
                    is_fallback=True
                )

        # 8. Fact Grounding & Anti-Hallucination Patching
        grounded_answer = grounding_verifier.verify_and_patch(
            answer=answer_text,
            tool_results=tool_results,
            data_mode=data_mode
        )

        # 9. Scrub secrets from output
        safe_answer = safety_engine.mask_secrets(grounded_answer)

        # Calculate Total Latency
        total_latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        copilot_metrics.record_request(
            latency_ms=total_latency_ms,
            is_fast_path=is_fast_path,
            is_llm=(mode_used == "ONLINE_AI")
        )

        # 10. Persist Messages to Session
        await session_store.save_message(
            db=db,
            session_id=session_id,
            role="user",
            content=req.message
        )

        tool_records = [
            ToolCallRecord(
                tool_name=tr.tool,
                arguments={},
                success=tr.success,
                error=tr.error
            )
            for tr in tool_results
        ]

        await session_store.save_message(
            db=db,
            session_id=session_id,
            role="assistant",
            content=safe_answer,
            latency_ms=total_latency_ms,
            provider=provider_used,
            model=settings.LLM_MODEL,
            data_mode=data_mode,
            sources=sources,
            components=components,
            tool_calls=[tr.model_dump() for tr in tool_records]
        )

        return ChatResponse(
            request_id=req_id,
            session_id=session_id,
            mode=mode_used,
            data_mode=data_mode,
            answer=safe_answer,
            reply=safe_answer,
            components=components,
            sources=sources,
            tool_calls=tool_records,
            latency_ms=total_latency_ms,
            grounded=True,
            provider=provider_used
        )

    async def stream_query(
        self,
        db: AsyncSession,
        query: str,
        session_id: Optional[str] = None,
        user_id: str = "operator"
    ) -> AsyncGenerator[str, None]:
        """Streams response with operational status steps and tokens via SSE."""
        from backend.app.copilot.streaming import stream_copilot_response

        # Execute full grounded processing
        chat_req = ChatRequest(message=query, session_id=session_id, stream=True)
        resp = await self.handle_query(db, chat_req, user_id=user_id)

        # Prepare operational status steps
        status_steps = [
            "Parsing operational query...",
            "Consulting live telemetry & risk engine...",
            "Validating sensor trust thresholds..."
        ]

        # Tokenize answer into small chunks for streaming effect
        words = resp.answer.split(" ")
        chunks = [w + " " for w in words]

        async for sse_event in stream_copilot_response(
            status_steps=status_steps,
            token_chunks=chunks,
            sources=resp.sources,
            components=resp.components,
            latency_ms=resp.latency_ms,
            request_id=resp.request_id,
            session_id=resp.session_id,
            mode=resp.mode,
            data_mode=resp.data_mode
        ):
            yield sse_event


copilot_orchestrator = CopilotOrchestrator()
