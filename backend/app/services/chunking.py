"""
CRI-RSK Chatbot — Semantic chunking with contextual headers.
Uses HuggingFace multilingual embeddings for semantic splitting.
"""

import logging
from typing import Optional

from langchain.docstore.document import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)


def get_embeddings(model_name: str) -> HuggingFaceEmbeddings:
    """Create HuggingFace embeddings instance."""
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def chunk_documents(
    documents: list[Document],
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2",
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> list[Document]:
    """
    Chunk documents using a hybrid approach:
    - FAQ items: kept as-is (already atomic Q&A pairs)
    - Short docs (<chunk_size): kept as-is
    - Long docs: semantic chunking with fallback to recursive splitting

    Each chunk gets a contextual header prepended for better retrieval.
    """
    embeddings = get_embeddings(embedding_model)
    all_chunks = []

    for doc in documents:
        doc_type = doc.metadata.get("document_type", "")

        # FAQ items are already atomic — keep as-is
        if doc_type == "faq":
            header = _build_header(doc)
            doc.page_content = f"{header}\n{doc.page_content}"
            all_chunks.append(doc)
            continue

        # Short documents — keep as-is
        if len(doc.page_content) < chunk_size:
            header = _build_header(doc)
            doc.page_content = f"{header}\n{doc.page_content}"
            all_chunks.append(doc)
            continue

        # Long documents — try semantic chunking first
        try:
            chunks = _semantic_chunk(doc, embeddings)
        except Exception as e:
            logger.warning(
                f"Semantic chunking failed for {doc.metadata.get('filename')}"
                f", falling back to recursive: {e}"
            )
            chunks = _recursive_chunk(doc, chunk_size, chunk_overlap)

        # Add contextual headers to each chunk
        header = _build_header(doc)
        for i, chunk in enumerate(chunks):
            chunk.page_content = f"{header}\n{chunk.page_content}"
            chunk.metadata["chunk_index"] = i
            chunk.metadata["total_chunks"] = len(chunks)

        all_chunks.extend(chunks)

    logger.info(
        f"Created {len(all_chunks)} chunks from {len(documents)} documents"
    )
    return all_chunks


def _build_header(doc: Document) -> str:
    """
    Build a contextual chunk header from document metadata.
    Example: "Source: CRI invest | Catégorie: FAQ | Préparation de dossier"
    """
    parts = []

    source = doc.metadata.get("source", "")
    if source:
        parts.append(f"Source: {source}")

    category = doc.metadata.get("category", "")
    if category:
        parts.append(f"Catégorie: {category}")

    doc_type = doc.metadata.get("document_type", "")
    if doc_type == "procedure":
        title = doc.metadata.get("procedure_title", "")
        if title:
            parts.append(f"Procédure: {title}")
    elif doc_type == "faq":
        faq_cat = doc.metadata.get("faq_category", "")
        if faq_cat:
            parts.append(f"FAQ: {faq_cat}")

    return " | ".join(parts) if parts else ""


def _semantic_chunk(
    doc: Document,
    embeddings: HuggingFaceEmbeddings,
) -> list[Document]:
    """Split a document using semantic chunking."""
    chunker = SemanticChunker(
        embeddings,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=85,
    )
    chunks = chunker.create_documents(
        [doc.page_content],
        metadatas=[doc.metadata],
    )
    return chunks


def _recursive_chunk(
    doc: Document,
    chunk_size: int,
    chunk_overlap: int,
) -> list[Document]:
    """Fallback: split using recursive character splitter."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.create_documents(
        [doc.page_content],
        metadatas=[doc.metadata],
    )
    return chunks
