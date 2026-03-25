"""
CRI-RSK Chatbot — RAG pipeline orchestrator.
Connects all RAG stages: query transform → fusion retrieval → reranking → LLM.
"""

import logging
from typing import Optional

from langchain.docstore.document import Document
from langchain_community.vectorstores import Chroma
from rank_bm25 import BM25Okapi

from app.config import Settings
from app.agents.public_agent import get_public_system_prompt
from app.agents.internal_agent import (
    get_internal_system_prompt,
    handle_internal_query,
)
from app.services.query_transform import transform_query
from app.services.retrieval import fusion_retrieval
from app.services.reranking import rerank_documents
from app.services.llm_service import generate_response

logger = logging.getLogger(__name__)

# Simple in-memory cache
_rag_cache = {}


async def run_rag_pipeline(
    query: str,
    agent_type: str,
    language: str,
    settings: Settings,
    vectorstore: Optional[Chroma],
    bm25_index: Optional[BM25Okapi],
    bm25_docs: Optional[list[Document]],
    conversation_history: Optional[list[dict]] = None,
) -> dict:
    """
    Execute the full RAG pipeline:
    1. Query transformation
    2. Fusion retrieval (vector + BM25)
    3. CrossEncoder reranking
    4. LLM response generation

    Args:
        query: User's original question
        agent_type: 'public' or 'internal'
        language: Detected language code
        settings: App settings
        vectorstore: ChromaDB instance
        bm25_index: BM25 index (may be None)
        bm25_docs: BM25 document list (may be None)
        conversation_history: Previous messages

    """
    # --- Guard: no vector store available ---
    if vectorstore is None:
        logger.warning("RAG pipeline called but vector store is not available.")
        return {
            "response": _get_empty_context_fallback(language),
            "is_fallback": True,
        }

    # --- Step 0: Check Cache ---
    cache_key = f"{agent_type}_{language}_{query.lower().strip()}"
    if cache_key in _rag_cache:
        logger.info(f"RAG Cache hit for: {query[:50]}...")
        return _rag_cache[cache_key]

    # --- Internal agent: check for special queries first ---
    if agent_type == "internal":
        internal_result = handle_internal_query(query, language)
        if internal_result:
            return {
                "response": internal_result,
                "is_fallback": False,
            }

    # --- Step 1: Query Transformation ---
    try:
        transformed_query = await transform_query(
            query=query,
            llm_model=settings.llm_model,
            api_key=settings.gemini_api_key,
        )
    except Exception as e:
        logger.warning(f"Query transform failed, using original: {e}")
        transformed_query = query

    # --- Step 2: Fusion Retrieval ---
    # Reduced k for better performance (reranking is faster)
    candidates = fusion_retrieval(
        vectorstore=vectorstore,
        bm25_index=bm25_index,
        bm25_docs=bm25_docs,
        query=transformed_query,
        k=5, 
        alpha=settings.fusion_alpha,
    )

    if not candidates:
        logger.warning("No documents retrieved")
        return {
            "response": _get_empty_context_fallback(language),
            "is_fallback": True,
        }

    # --- Step 3: Reranking (Optional) ---
    if getattr(settings, "enable_reranking", True):
        top_docs = rerank_documents(
            query=transformed_query,
            documents=candidates,
            model_name=settings.reranker_model,
            top_k=settings.rerank_top_k,
        )
    else:
        top_docs = candidates[:3]

    # --- Step 4: Build context from top documents ---
    context = "\n\n---\n\n".join(
        doc.page_content for doc in top_docs
    )

    # --- Step 5: Get system prompt for the agent ---
    if agent_type == "internal":
        system_prompt = get_internal_system_prompt(language)
    else:
        system_prompt = get_public_system_prompt(language)

    # --- Step 6: Generate LLM response ---
    result = await generate_response(
        query=query,  # Use original query, not transformed
        context=context,
        system_prompt=system_prompt,
        language=language,
        llm_model=settings.llm_model,
        api_key=settings.gemini_api_key,
        conversation_history=conversation_history,
    )

    # --- Step 7: Update Cache ---
    if len(_rag_cache) > 200:
        # Simple FIFO-ish eviction
        _rag_cache.pop(next(iter(_rag_cache)))
    _rag_cache[cache_key] = result

    return result


def _get_empty_context_fallback(language: str) -> str:
    """Fallback message when no documents are found at all."""
    messages = {
        "fr": (
            "Je n'ai pas trouvé d'information précise sur ce sujet. "
            "Pour une réponse personnalisée, contactez le CRI-RSK :\n"
            "📞 05 37 77 64 00\n"
            "📧 contact@rabatinvest.ma"
        ),
        "ar": (
            "لم أجد معلومات دقيقة حول هذا الموضوع.\n"
            "للتواصل مع مركز الاستثمار الجهوي:\n"
            "📞 05 37 77 64 00\n"
            "📧 contact@rabatinvest.ma"
        ),
        "en": (
            "I couldn't find precise information on this topic. "
            "Please contact CRI-RSK directly:\n"
            "📞 05 37 77 64 00\n"
            "📧 contact@rabatinvest.ma"
        ),
    }
    return messages.get(language, messages["fr"])
