"""
Vector database management using ChromaDB.

Handles embedding generation, storage, and retrieval of document vectors.
"""

import os
import time
from pathlib import Path
from typing import List, Optional
import chromadb
from chromadb.config import Settings
import numpy as np
from sentence_transformers import SentenceTransformer

from .data_ingestion import DocumentChunk
from src.config import get_rag_config


class VectorStoreManager:
    """Manages ChromaDB vector database for document embeddings."""

    def __init__(self):
        self.config = get_rag_config()
        self.model = None
        self.client = None
        self.collection = None

    def initialize(self):
        """Initialize the vector store and embedding model."""
        # Ensure data directory exists
        vector_db_path = Path(self.config.vector_db_path).parent
        vector_db_path.mkdir(parents=True, exist_ok=True)

        # Initialize embedding model
        self.model = SentenceTransformer(self.config.embedding_model)

        # Initialize ChromaDB client with consistent settings
        self.client = chromadb.PersistentClient(
            path=self.config.vector_db_path
        )

        # Get or create collection
        collection_name = "portfolio_rag"
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}  # Cosine similarity for embeddings
            )

        print(f"Initialized vector store with {self.collection.count()} documents")
        return True

    def add_documents(self, chunks: List[DocumentChunk]) -> bool:
        """Add document chunks to the vector store."""
        if not self.collection or not self.model:
            if not self.initialize():
                return False

        try:
            # Prepare data for batch insertion
            texts = []
            metadatas = []
            ids = []

            for i, chunk in enumerate(chunks):
                # Generate embedding for the chunk
                embedding = self.model.encode(chunk.text, normalize_embeddings=True)

                # Prepare metadata
                metadata = {
                    "source": chunk.source,
                    "section": chunk.section,
                    "text_length": len(chunk.text),
                    **chunk.metadata
                }

                texts.append(chunk.text)
                metadatas.append(metadata)
                ids.append(f"{chunk.source}_{chunk.section}_{i}_{int(time.time())}")

            # Check for existing documents (avoid duplicates)
            existing_ids = set(self.collection.get()["ids"])
            new_ids = [id for id in ids if id not in existing_ids]
            new_texts = [text for id, text in zip(ids, texts) if id not in existing_ids]
            new_metadatas = [metadata for id, metadata in zip(ids, metadatas) if id not in existing_ids]

            if new_texts:
                # Generate embeddings for new texts
                embeddings = self.model.encode(new_texts, normalize_embeddings=True)

                # Add to collection
                self.collection.add(
                    embeddings=embeddings.tolist(),
                    documents=new_texts,
                    metadatas=new_metadatas,
                    ids=new_ids
                )

                print(f"Added {len(new_texts)} new documents to vector store")
            else:
                print("No new documents to add")

            return True

        except Exception as e:
            print(f"Error adding documents to vector store: {e}")
            return False

    def search_similar(
        self,
        query: str,
        n_results: int = 5,
        source_filter: Optional[str] = None,
        section_filter: Optional[str] = None
    ) -> dict:
        """Search for similar documents in the vector store."""
        if not self.collection or not self.model:
            if not self.initialize():
                return {"documents": [], "metadatas": [], "distances": []}

        try:
            # Generate query embedding
            query_embedding = self.model.encode(query, normalize_embeddings=True)

            # Prepare filter if needed
            where_clause = {}
            if source_filter:
                where_clause["source"] = source_filter
            if section_filter:
                where_clause["section"] = section_filter

            # Search collection
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=n_results,
                where=where_clause if where_clause else None,
                include=["documents", "metadatas", "distances"]
            )

            return results

        except Exception as e:
            print(f"Error searching vector store: {e}")
            return {"documents": [], "metadatas": [], "distances": []}

    def get_document_count(self) -> int:
        """Get the total number of documents in the store."""
        if self.collection:
            return self.collection.count()
        return 0

    def reset_collection(self) -> bool:
        """Reset the entire collection (use with caution)."""
        try:
            if self.collection:
                self.client.delete_collection(self.collection.name)
                self.collection = self.client.create_collection(
                    name="portfolio_rag",
                    metadata={"hnsw:space": "cosine"}
                )
                print("Vector store collection reset successfully")
                return True
        except Exception as e:
            print(f"Error resetting vector store: {e}")
        return False

    def get_stats(self) -> dict:
        """Get statistics about the vector store."""
        if not self.collection:
            return {"total_documents": 0, "sources": {}, "sections": {}}

        try:
            results = self.collection.get(include=["metadatas"])
            metadatas = results.get("metadatas", [])

            sources = {}
            sections = {}

            for metadata in metadatas:
                source = metadata.get("source", "unknown")
                section = metadata.get("section", "unknown")

                sources[source] = sources.get(source, 0) + 1
                sections[section] = sections.get(section, 0) + 1

            return {
                "total_documents": len(metadatas),
                "sources": sources,
                "sections": sections
            }
        except Exception as e:
            print(f"Error getting vector store stats: {e}")
            return {"total_documents": 0, "sources": {}, "sections": {}}


if __name__ == "__main__":
    import asyncio
    from .data_ingestion import process_all_documents

    async def test_vector_store():
        print("Testing vector store...")

        # Process documents
        print("Processing documents...")
        chunks = await process_all_documents()
        print(f"Generated {len(chunks)} chunks")

        if not chunks:
            print("No documents to index")
            return

        # Initialize and populate vector store
        store = VectorStoreManager()
        success = store.initialize()
        if not success:
            print("Failed to initialize vector store")
            return

        print("Adding documents...")
        success = store.add_documents(chunks)
        if not success:
            print("Failed to add documents")

        # Test search
        print("\nTesting search...")
        test_queries = [
            "What are your machine learning skills?",
            "Tell me about your experience with AI",
            "What projects have you worked on?",
            "What is your educational background?"
        ]

        for query in test_queries:
            print(f"\nQuery: {query}")
            results = store.search_similar(query, n_results=2)
            documents = results.get("documents", [])
            for i, doc in enumerate(documents):
                print(f"  Result {i+1}: {doc[:100]}...")

        # Show stats
        stats = store.get_stats()
        print(f"\nVector Store Stats: {stats}")

    asyncio.run(test_vector_store())
