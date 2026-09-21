"""
PRAHARI Copilot Session-Scoped Conversation Memory
Maintains ephemeral dialogue context and resolves ambiguous pronouns ('it', 'these').
"""
from typing import Dict, Any, Optional, Tuple
import time
import re


class SessionContext:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.last_node: Optional[str] = None
        self.last_event: Optional[str] = None
        self.last_intent: Optional[str] = None
        self.last_updated: float = time.time()

    def update(self, node_id: Optional[str] = None, event_id: Optional[str] = None, intent: Optional[str] = None):
        if node_id:
            self.last_node = node_id
        if event_id:
            self.last_event = event_id
        if intent:
            self.last_intent = intent
        self.last_updated = time.time()


class ConversationMemory:
    """Session-scoped in-memory entity tracker."""

    def __init__(self, ttl_seconds: float = 1800.0):
        self._sessions: Dict[str, SessionContext] = {}
        self.ttl = ttl_seconds

    def get_or_create(self, session_id: str) -> SessionContext:
        ctx = self._sessions.get(session_id)
        if not ctx or (time.time() - ctx.last_updated > self.ttl):
            ctx = SessionContext(session_id)
            self._sessions[session_id] = ctx
        return ctx

    def resolve_pronouns(self, query: str, session_id: str) -> Tuple[str, Optional[str]]:
        """
        Resolves ambiguous pronouns like 'it', 'this node', 'that' to the previously discussed node.
        Example: 'Why is it critical?' -> 'Why is JALA-01 critical?'
        """
        ctx = self.get_or_create(session_id)
        resolved = query

        # Pronoun replacement for nodes
        if ctx.last_node:
            # Pattern matching "it", "this node", "that node"
            if re.search(r'\b(it|this node|that node|the node)\b', query, re.IGNORECASE):
                # Don't replace if another node is explicitly mentioned
                if not any(k in query.lower() for k in ["jala", "agni", "bhumi"]):
                    resolved = re.sub(r'\b(it|this node|that node|the node)\b', ctx.last_node, query, flags=re.IGNORECASE)

        return resolved, ctx.last_node


conversation_memory = ConversationMemory()
