"""
CRI-RSK Chatbot — FastAPI Application Entry Point.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import chat, conversations, ratings, otp, dossiers, health, admin

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize resources on startup."""
    settings = get_settings()
    logging.basicConfig(level=getattr(logging, settings.log_level))
    logger.info("Starting CRI-RSK Chatbot API...")

    # Import here to avoid circular imports and defer heavy loading
    from app.vectorstore.chroma_store import get_vectorstore
    from app.services.retrieval import get_bm25_index
    from app.services.reranking import _get_cross_encoder
    from app.services.otp_service import init_otp_service

    # Initialize vector store and BM25 index
    vectorstore = get_vectorstore(settings)
    if vectorstore is None:
        logger.warning(
            "Vector store unavailable — RAG queries will return fallback responses. "
            "Populate the knowledge base by running: python -m scripts.load_documents"
        )
    bm25_index, bm25_docs = get_bm25_index(settings)

    # Store in app state for access from routers
    app.state.settings = settings
    app.state.vectorstore = vectorstore
    app.state.bm25_index = bm25_index
    app.state.bm25_docs = bm25_docs

    # Pre-load CrossEncoder
    if settings.enable_reranking:
        logger.info(f"Pre-loading Reranker model: {settings.reranker_model}...")
        _get_cross_encoder(settings.reranker_model)

    # Initialize OTP service with Upstash Redis
    if settings.upstash_redis_url and settings.upstash_redis_token:
        init_otp_service(settings.upstash_redis_url, settings.upstash_redis_token)
        logger.info("OTP service initialized with Upstash Redis")
    else:
        logger.warning("Upstash not configured — OTP will use in-memory fallback")

    logger.info("CRI-RSK Chatbot API ready.")
    yield
    logger.info("Shutting down CRI-RSK Chatbot API.")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="CRI-RSK Chatbot API",
        description=(
            "API for the CRI Rabat-Salé-Kénitra intelligent chatbot "
            "with RAG pipeline, multilingual support (FR/AR/EN), "
            "and dual agent system (Public + Internal)."
        ),
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS — allow frontend origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Tighten in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(health.router, prefix="/api", tags=["Health"])
    app.include_router(chat.router, prefix="/api", tags=["Chat"])
    app.include_router(
        conversations.router, prefix="/api", tags=["Conversations"]
    )
    app.include_router(ratings.router, prefix="/api", tags=["Ratings"])
    app.include_router(otp.router, prefix="/api", tags=["OTP"])
    app.include_router(dossiers.router, prefix="/api", tags=["Dossiers"])
    app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

    return app


app = create_app()
