"""
PRAHARI Copilot Session Store
Persists and retrieves chat conversations, messages, tool executions, and feedback.
"""
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy import select, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.copilot import ChatSession, ChatMessage, CopilotToolCall, CopilotFeedback
from backend.app.copilot.schemas import StructuredComponent


class SessionStore:
    """Async database repository for Copilot conversation history."""

    async def get_or_create_session(
        self,
        db: AsyncSession,
        session_id: Optional[str] = None,
        user_id: str = "operator",
        title: str = "Operational Inquiry"
    ) -> ChatSession:
        if session_id:
            res = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
            sess = res.scalar_one_or_none()
            if sess and (sess.user_id == user_id or user_id == "admin"):
                return sess
            if sess:
                session_id = None

        new_sess = ChatSession(
            id=session_id or str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            mode="LOCAL_ASSISTANT",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(new_sess)
        await db.commit()
        await db.refresh(new_sess)
        return new_sess

    async def list_sessions(
        self,
        db: AsyncSession,
        user_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        query = select(ChatSession).order_by(desc(ChatSession.updated_at)).limit(limit)
        if user_id and user_id != "admin":
            query = query.where(ChatSession.user_id == user_id)

        res = await db.execute(query)
        sessions = res.scalars().all()
        results = []

        for s in sessions:
            # Count messages
            msg_res = await db.execute(select(ChatMessage).where(ChatMessage.session_id == s.id))
            count = len(msg_res.scalars().all())
            results.append({
                "id": s.id,
                "user_id": s.user_id,
                "title": s.title,
                "mode": s.mode,
                "created_at": s.created_at.isoformat(),
                "updated_at": s.updated_at.isoformat(),
                "message_count": count
            })
        return results

    async def delete_session(self, db: AsyncSession, session_id: str, user_id: str) -> bool:
        query = select(ChatSession).where(ChatSession.id == session_id)
        if user_id != "admin":
            query = query.where(ChatSession.user_id == user_id)
        res = await db.execute(query)
        sess = res.scalar_one_or_none()
        if not sess:
            return False

        # Delete messages and session
        await db.execute(delete(ChatMessage).where(ChatMessage.session_id == session_id))
        await db.execute(delete(ChatSession).where(ChatSession.id == session_id))
        await db.commit()
        return True

    async def save_message(
        self,
        db: AsyncSession,
        session_id: str,
        role: str,
        content: str,
        latency_ms: float = 0.0,
        provider: str = "LOCAL_DETERMINISTIC",
        model: str = "local-expert-v1",
        data_mode: str = "REAL",
        sources: Optional[List[str]] = None,
        components: Optional[List[StructuredComponent]] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None
    ) -> ChatMessage:
        msg = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role=role,
            content=content,
            created_at=datetime.now(timezone.utc),
            latency_ms=latency_ms,
            provider=provider,
            model=model,
            data_mode=data_mode,
            sources=sources or [],
            components=[c.model_dump() for c in (components or [])],
            tool_calls=tool_calls or []
        )
        db.add(msg)

        # Update session updated_at
        sess_res = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
        sess = sess_res.scalar_one_or_none()
        if sess:
            sess.updated_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(msg)
        return msg

    async def get_messages(
        self,
        db: AsyncSession,
        session_id: str,
        limit: int = 50,
        user_id: str = "operator",
    ) -> List[Dict[str, Any]]:
        owner_query = select(ChatSession.id).where(ChatSession.id == session_id)
        if user_id != "admin":
            owner_query = owner_query.where(ChatSession.user_id == user_id)
        if (await db.execute(owner_query)).scalar_one_or_none() is None:
            return []
        query = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
        )
        res = await db.execute(query)
        msgs = res.scalars().all()
        return [
            {
                "id": m.id,
                "session_id": m.session_id,
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at.isoformat(),
                "latency_ms": m.latency_ms,
                "provider": m.provider,
                "model": m.model,
                "data_mode": m.data_mode,
                "sources": m.sources or [],
                "components": m.components or [],
                "tool_calls": m.tool_calls or []
            }
            for m in msgs
        ]

    async def record_feedback(
        self,
        db: AsyncSession,
        message_id: str,
        user_id: str,
        rating: str,
        issue_type: Optional[str] = None,
        comment: Optional[str] = None
    ) -> CopilotFeedback:
        fb = CopilotFeedback(
            id=str(uuid.uuid4()),
            message_id=message_id,
            user_id=user_id,
            rating=rating,
            issue_type=issue_type,
            comment=comment,
            created_at=datetime.now(timezone.utc)
        )
        db.add(fb)
        await db.commit()
        await db.refresh(fb)
        return fb


session_store = SessionStore()
