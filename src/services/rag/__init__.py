"""
Retrieval-Augmented Generation (RAG) Service

Provides conversational AI assistant capabilities for the portfolio site,
enabling natural language interaction with resume content and GitHub projects.
"""

from .data_ingestion import (
    DocumentChunk,
    process_resume_pdf,
    process_github_projects,
    process_all_documents
)
from .vector_store import VectorStoreManager

# TODO: Add these modules as they are implemented
# from .retrieval import RetrievalEngine
# from .generation import GenerationEngine
# from .rag_pipeline import RAGPipeline

__all__ = [
    "DocumentChunk",
    "process_resume_pdf",
    "process_github_projects",
    "process_all_documents",
    "VectorStoreManager",
    # "RetrievalEngine",
    # "GenerationEngine",
    # "RAGPipeline"
]
