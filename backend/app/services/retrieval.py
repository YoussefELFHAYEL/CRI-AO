"""
CRI-RSK Chatbot — Fusion retrieval: vector search + BM25.
Combines semantic similarity with keyword matching for robust multilingual retrieval.
"""

import logging
from typing import Optional

import numpy as np
from rank_bm25 import BM25Okapi
from langchain.docstore.document import Document
from langchain_community.vectorstores import Chroma

from app.config import Settings

logger = logging.getLogger(__name__)

# Module-level BM25 cache
_bm25_index: Optional[BM25Okapi] = None
_bm25_docs: Optional[list[Document]] = None


def get_bm25_index(
    settings: Settings,
) -> tuple[Optional[BM25Okapi], Optional[list[Document]]]:
    """
    Get or create the BM25 index.
    Loads documents, chunks them, and builds a BM25 index.
    Returns (bm25_index, document_list) or (None, None) if no data.
    """
    global _bm25_index, _bm25_docs

    if _bm25_index is not None:
        return _bm25_index, _bm25_docs

    # Try to load from the vector store's existing documents
    # If ChromaDB is populated, we rebuild BM25 from it
    try:
        from app.vectorstore.chroma_store import get_vectorstore

        vectorstore = get_vectorstore(settings)
        collection = vectorstore._collection
        count = collection.count()

        if count > 0:
            # Get all documents from ChromaDB
            result = collection.get(
                include=["documents", "metadatas"],
                limit=count,
            )
            _bm25_docs = [
                Document(
                    page_content=doc,
                    metadata=meta if meta else {},
                )
                for doc, meta in zip(
                    result["documents"], result["metadatas"]
                )
            ]
            _bm25_index = _build_bm25(_bm25_docs)
            logger.info(
                f"BM25 index built from {count} ChromaDB documents"
            )
            return _bm25_index, _bm25_docs
    except Exception as e:
        logger.warning(f"Could not build BM25 from ChromaDB: {e}")

    logger.warning(
        "No documents available for BM25. "
        "Run load_documents.py first."
    )
    return None, None


def build_bm25_from_documents(
    documents: list[Document],
) -> tuple[BM25Okapi, list[Document]]:
    """Build a BM25 index from a list of documents."""
    global _bm25_index, _bm25_docs
    _bm25_docs = documents
    _bm25_index = _build_bm25(documents)
    return _bm25_index, _bm25_docs


def _build_bm25(documents: list[Document]) -> BM25Okapi:
    """Create a BM25 index from documents."""
    tokenized = [doc.page_content.split() for doc in documents]
    return BM25Okapi(tokenized)


def fusion_retrieval(
    vectorstore: Chroma,
    bm25_index: Optional[BM25Okapi],
    bm25_docs: Optional[list[Document]],
    query: str,
    k: int = 10,
    alpha: float = 0.5,
) -> list[Document]:
    """
    Fusion retrieval combining vector similarity + BM25 keyword search.

    Args:
        vectorstore: ChromaDB vector store
        bm25_index: Pre-computed BM25 index (can be None)
        bm25_docs: Documents corresponding to BM25 index
        query: Search query
        k: Number of results to return
        alpha: Weight for vector scores (1-alpha for BM25)

    Returns:
        Top-k documents ranked by combined score.
    """
    # If no BM25 index, fall back to pure vector search
    if bm25_index is None or bm25_docs is None:
        logger.info("No BM25 index — using pure vector search")
        return vectorstore.similarity_search(query, k=k)

    epsilon = 1e-8

    # Vector search — get all scored results
    try:
        vector_results = vectorstore.similarity_search_with_score(
            query, k=len(bm25_docs)
        )
    except Exception:
        # Fallback: get just top-k
        vector_results = vectorstore.similarity_search_with_score(
            query, k=min(k * 5, 50)
        )

    if not vector_results:
        return []

    # BM25 search
    bm25_scores = bm25_index.get_scores(query.split())

    # Normalize vector scores (lower distance = better, so invert)
    vector_scores = np.array([score for _, score in vector_results])
    score_range = np.max(vector_scores) - np.min(vector_scores) + epsilon
    vector_scores_norm = 1 - (
        (vector_scores - np.min(vector_scores)) / score_range
    )

    # Normalize BM25 scores
    bm25_range = np.max(bm25_scores) - np.min(bm25_scores) + epsilon
    bm25_scores_norm = (bm25_scores - np.min(bm25_scores)) / bm25_range

    # Build a mapping from document content to vector scores
    vector_score_map = {}
    for i, (doc, _) in enumerate(vector_results):
        vector_score_map[doc.page_content] = vector_scores_norm[i]

    # Combine scores for all BM25 documents
    combined = []
    for i, doc in enumerate(bm25_docs):
        v_score = vector_score_map.get(doc.page_content, 0.0)
        b_score = bm25_scores_norm[i] if i < len(bm25_scores_norm) else 0.0
        combined_score = alpha * v_score + (1 - alpha) * b_score
        combined.append((doc, combined_score))

    # Sort by combined score (descending) and return top-k
    combined.sort(key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in combined[:k]]
