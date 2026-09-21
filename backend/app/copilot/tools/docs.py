"""
Copilot Project Documentation Retrieval Tool
Performs local BM25 ranking over project architecture and node specs.
"""
from typing import Dict, Any, List
from backend.app.copilot.retrieval import knowledge_retriever


async def search_project_documentation(query: str, top_k: int = 3) -> Dict[str, Any]:
    """Search project documentation files for architectural, algorithmic, or deployment explanations."""
    chunks = knowledge_retriever.retrieve(query, top_k=top_k)
    return {
        "query": query,
        "results_count": len(chunks),
        "chunks": chunks
    }
