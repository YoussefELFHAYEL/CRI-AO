"""
CRI-RSK Chatbot — ChromaDB vector store setup and management.
"""

import logging
import os
from typing import Optional

os.environ["ANONYMIZED_TELEMETRY"] = "False"

import chromadb
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from app.config import Settings

logger = logging.getLogger(__name__)

# Nom fixe de la collection - JAMAIS changer
COLLECTION_NAME = "cri_rsk_knowledge"

# Module-level cache
_vectorstore: Optional[Chroma] = None


def get_embeddings(model_name: str) -> HuggingFaceEmbeddings:
    """Create HuggingFace embeddings instance."""
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def get_vectorstore(settings: Settings) -> Chroma:
    """
    Get or create the ChromaDB vector store.
    """
    global _vectorstore

    if _vectorstore is not None:
        return _vectorstore

    embeddings = get_embeddings(settings.embedding_model)
    persist_dir = settings.chroma_persist_dir

    # Créer UN SEUL client ChromaDB
    client = chromadb.PersistentClient(path=persist_dir)

    # Vérifier si la collection existe
    existing = client.list_collections()
    existing_names = [c.name for c in existing]

    if COLLECTION_NAME in existing_names:
        count = client.get_collection(COLLECTION_NAME).count()
        logger.info(f"Loading existing ChromaDB from {persist_dir}")
        logger.info(f"Collection '{COLLECTION_NAME}' found with {count} documents")
    else:
        count = 0
        logger.warning(
            f"Collection '{COLLECTION_NAME}' not found. "
            "Run: python -m scripts.load_documents"
        )

    # Charger via LangChain en passant LE MÊME client
    _vectorstore = Chroma(
        client=client,                    # ← PASSER LE CLIENT DIRECTEMENT
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
    )

    logger.info(f"Loaded ChromaDB with {count} documents")
    return _vectorstore


def populate_vectorstore(
    documents: list[Document],
    settings: Settings,
) -> Chroma:
    """
    Populate the vector store with documents.
    """
    global _vectorstore

    embeddings = get_embeddings(settings.embedding_model)
    persist_dir = settings.chroma_persist_dir

    logger.info(f"Populating ChromaDB with {len(documents)} chunks...")

    # UN SEUL client - cohérent avec get_vectorstore
    client = chromadb.PersistentClient(path=persist_dir)

    # Supprimer collection existante
    try:
        client.delete_collection(COLLECTION_NAME)
        logger.info("Deleted existing collection for fresh load.")
    except Exception:
        pass

    # Créer nouvelle collection
    _vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        client=client,                    # ← MÊME CLIENT
        collection_name=COLLECTION_NAME,
    )

    count = _vectorstore._collection.count()
    logger.info(f"ChromaDB populated with {count} chunks.")

    return _vectorstore