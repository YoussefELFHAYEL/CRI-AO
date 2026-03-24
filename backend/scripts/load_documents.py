"""
CRI-RSK Chatbot — Document loading script.
Loads all knowledge base documents into ChromaDB.

Usage:
    cd backend
    python -m scripts.load_documents
"""

import logging
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

from app.config import get_settings
from app.services.document_loader import load_all_documents
from app.services.chunking import chunk_documents
from app.vectorstore.chroma_store import populate_vectorstore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Load all documents into ChromaDB."""
    settings = get_settings()

    # Resolve knowledge base path
    kb_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", settings.knowledge_base_path)
    )
    logger.info(f"Knowledge base path: {kb_path}")

    if not os.path.exists(kb_path):
        logger.error(f"Knowledge base directory not found: {kb_path}")
        sys.exit(1)

    # Step 1: Load documents
    logger.info("=" * 60)
    logger.info("Step 1: Loading documents from knowledge base...")
    logger.info("=" * 60)
    documents = load_all_documents(kb_path)
    if not documents:
        logger.error("No documents loaded. Check the knowledge base path.")
        sys.exit(1)
    logger.info(f"Loaded {len(documents)} documents")

    # Print document summary
    by_type: dict[str, int] = {}
    for doc in documents:
        doc_type = doc.metadata.get("document_type", "unknown")
        by_type[doc_type] = by_type.get(doc_type, 0) + 1
    for doc_type, count in by_type.items():
        logger.info(f"  {doc_type}: {count}")

    # Step 2: Chunk documents
    logger.info("=" * 60)
    logger.info("Step 2: Chunking documents...")
    logger.info("=" * 60)
    chunks = chunk_documents(
        documents,
        embedding_model=settings.embedding_model,
    )
    logger.info(f"Created {len(chunks)} chunks")

    # Step 3: Populate ChromaDB
    logger.info("=" * 60)
    logger.info("Step 3: Populating ChromaDB vector store...")
    logger.info("=" * 60)
    vectorstore = populate_vectorstore(chunks, settings)

    # Step 4: Verify
    logger.info("=" * 60)
    logger.info("Step 4: Verification...")
    logger.info("=" * 60)
    collection = vectorstore._collection
    count = collection.count()
    logger.info(f"ChromaDB contains {count} documents")

    # Test query
    test_results = vectorstore.similarity_search(
        "créer une entreprise", k=3
    )
    logger.info(f"Test query 'créer une entreprise' returned {len(test_results)} results")
    for i, doc in enumerate(test_results):
        logger.info(f"  Result {i+1}: {doc.page_content[:100]}...")

    logger.info("=" * 60)
    logger.info("✅ Document loading complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
