"""
CRI-RSK Chatbot — CrossEncoder reranking service.
Uses multilingual cross-encoder to rerank retrieved documents.
"""

import logging
from typing import Optional

from langchain.docstore.document import Document
from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)

# Module-level cache for the model
_cross_encoder: Optional[CrossEncoder] = None


def _get_cross_encoder(model_name: str) -> CrossEncoder:
    """Load and cache the CrossEncoder model."""
    global _cross_encoder
    if _cross_encoder is None:
        logger.info(f"Loading CrossEncoder model: {model_name}")
        _cross_encoder = CrossEncoder(model_name)
        logger.info("CrossEncoder model loaded.")
    return _cross_encoder


def rerank_documents(
    query: str,
    documents: list[Document],
    model_name: str = "cross-encoder/ms-marco-multilingual-MiniLM-L6-v2",
    top_k: int = 3,
) -> list[Document]:
    """
    Rerank documents using a CrossEncoder model.

    Takes the top candidates from fusion retrieval and reranks them
    based on query-document relevance, returning the best top_k.

    Args:
        query: The search query
        documents: List of candidate documents to rerank
        model_name: CrossEncoder model name
        top_k: Number of documents to return after reranking

    Returns:
        Top-k most relevant documents.
    """
    if not documents:
        return []

    if len(documents) <= top_k:
        return documents

    cross_encoder = _get_cross_encoder(model_name)

    # Create query-document pairs
    pairs = [[query, doc.page_content] for doc in documents]

    # Get relevance scores
    scores = cross_encoder.predict(pairs)

    # Sort by score (descending) and return top_k
    scored_docs = sorted(
        zip(documents, scores), key=lambda x: x[1], reverse=True
    )

    top_docs = [doc for doc, _ in scored_docs[:top_k]]

    logger.debug(
        f"Reranked {len(documents)} docs → top {top_k}. "
        f"Score range: {min(scores):.3f} to {max(scores):.3f}"
    )

    return top_docs
