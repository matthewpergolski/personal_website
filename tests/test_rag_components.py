"""
Comprehensive RAG system component tests using pytest.

Tests individual components and their integration for the portfolio RAG chatbot.
"""

import os
import sys
import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for testing
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from src.services.rag.data_ingestion import (
    process_resume_pdf,
    process_github_projects,
    process_all_documents,
    DocumentChunk
)
from src.services.rag.vector_store import VectorStoreManager
from src.config import get_rag_config


class TestDataIngestion:
    """Test data ingestion components."""

    @pytest.mark.asyncio
    async def test_resume_pdf_processing(self):
        """Test resume PDF download and text extraction."""
        chunks = await process_resume_pdf()

        if not chunks:  # Skip if no resume URL configured
            pytest.skip("No resume PDF configured or available")

        assert isinstance(chunks, list)
        assert len(chunks) > 0

        # Verify chunk structure
        for chunk in chunks:
            assert isinstance(chunk, DocumentChunk)
            assert chunk.text.strip()
            assert chunk.source
            assert chunk.section
            assert chunk.metadata

        # Check for expected sections
        sections = {chunk.section for chunk in chunks}
        expected_sections = {"experience", "skills", "education", "summary"}
        assert sections & expected_sections  # At least one expected section

    @pytest.mark.asyncio
    async def test_github_projects_processing(self):
        """Test GitHub projects data processing."""
        chunks = await process_github_projects()

        if not chunks:  # Skip if no GitHub token
            pytest.skip("GitHub credentials not configured")

        assert isinstance(chunks, list)
        assert len(chunks) > 0

        # Verify chunk structure
        for chunk in chunks:
            assert isinstance(chunk, DocumentChunk)
            assert chunk.text.strip()
            assert chunk.source == "github"
            assert chunk.section == "project_description"
            assert "project" in chunk.metadata

    @pytest.mark.asyncio
    async def test_combined_document_processing(self):
        """Test processing both resume and GitHub data."""
        all_chunks = await process_all_documents()

        assert isinstance(all_chunks, list)

        if len(all_chunks) > 0:
            # Check for expected sources
            sources = {chunk.source for chunk in all_chunks}
            expected_sources = {"resume_pdf", "github"}
            assert sources & expected_sources  # At least one expected source


class TestVectorStoreComponents:
    """Test vector store individual components."""

    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database path for testing."""
        db_path = tempfile.mkdtemp(prefix="rag_test_")
        yield db_path

        # Cleanup
        if os.path.exists(db_path):
            shutil.rmtree(db_path)

    def test_chromadb_basic_functionality(self, temp_db_path):
        """Test ChromaDB basic operations."""
        import chromadb

        # Test client creation
        client = chromadb.PersistentClient(
            path=temp_db_path,
            settings=chromadb.config.Settings(anonymized_telemetry=False)
        )
        assert client is not None

        # Test collection creation
        collection = client.create_collection(
            name="test_collection",
            metadata={"hnsw:space": "cosine"}
        )
        assert collection is not None
        assert collection.name == "test_collection"

        # Test basic operations
        assert collection.count() == 0

        # Clean up collection
        client.delete_collection("test_collection")

    def test_sentence_transformers_basic(self):
        """Test sentence-transformers basic functionality."""
        from sentence_transformers import SentenceTransformer

        # Test model loading
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        model = SentenceTransformer(model_name)
        assert model is not None

        # Test encoding
        test_texts = ["Hello world", "Machine learning is amazing"]
        embeddings = model.encode(test_texts, normalize_embeddings=True)

        assert embeddings.shape[0] == 2
        assert embeddings.shape[1] == 384  # Standard dimension for this model

        # Check embeddings are normalized
        import numpy as np
        norms = np.linalg.norm(embeddings, axis=1)
        np.testing.assert_allclose(norms, 1.0, atol=1e-6)

    def test_vector_store_manager_initialization(self):
        """Test VectorStoreManager initialization with mocks."""
        with patch('chromadb.PersistentClient') as mock_client:
            with patch('sentence_transformers.SentenceTransformer') as mock_model:
                # Setup mock model
                mock_embedding_model = Mock()
                mock_embedding_model.encode.return_value = [[0.1, 0.2, 0.3]]
                mock_model.return_value = mock_embedding_model

                # Setup mock ChromaDB
                mock_collection = Mock()
                mock_collection.count.return_value = 0
                mock_client.return_value.get_collection.return_value = mock_collection

                # Test initialization
                manager = VectorStoreManager()
                success = manager.initialize()

                assert success, "VectorStoreManager initialization should succeed"
                assert manager.model is not None
                assert manager.client is not None
                assert manager.collection is not None


class TestVectorStoreIntegration:
    """Test vector store full integration."""

    @pytest.fixture
    async def real_chunks(self):
        """Get real document chunks for testing."""
        chunks = await process_all_documents()
        if not chunks:
            pytest.skip("No document chunks available for testing")
        return chunks

    @pytest.fixture
    def temp_vector_store(self):
        """Create temporary vector store for testing."""
        vector_store_path = tempfile.mkdtemp(prefix="rag_integration_test_")

        # Mock the config to use temp path
        with patch('src.services.rag.vector_store.get_rag_config') as mock_get_config:
            mock_config = Mock()
            mock_config.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
            mock_config.vector_db_path = vector_store_path
            mock_config.chunk_size = 512
            mock_config.chunk_overlap = 128
            mock_get_config.return_value = mock_config

            manager = VectorStoreManager()
            manager.config = mock_config

            yield manager

            # Cleanup
            if os.path.exists(vector_store_path):
                shutil.rmtree(vector_store_path)

    @pytest.mark.asyncio
    async def test_vector_store_full_integration(self, real_chunks, temp_vector_store):
        """Test full vector store integration with real documents."""
        manager = temp_vector_store

        # Initialize vector store
        success = manager.initialize()
        assert success, "Vector store should initialize successfully"

        # Add real documents
        success = manager.add_documents(real_chunks)
        assert success, "Documents should be added successfully"

        # Verify documents were added
        doc_count = manager.get_document_count()
        assert doc_count == len(real_chunks), f"Expected {len(real_chunks)} documents, got {doc_count}"

        # Get stats
        stats = manager.get_stats()
        assert "total_documents" in stats
        assert stats["total_documents"] == len(real_chunks)
        assert "sources" in stats
        assert "sections" in stats

        # Test search with real queries
        test_queries = [
            "What are your machine learning skills?",
            "Tell me about your AI experience"
        ]

        for query in test_queries:
            results = manager.search_similar(query, n_results=3)

            assert "documents" in results
            assert "metadatas" in results
            assert "distances" in results

            documents = results["documents"]
            metadatas = results["metadatas"]

            # Should return some results
            if len(real_chunks) > 0:
                assert len(documents) > 0, f"No search results for query: {query}"

                # Check metadata structure
                if documents and metadatas:
                    assert len(metadatas) == len(documents)
                    for metadata in metadatas:
                        assert "source" in metadata
                        assert "section" in metadata


class TestEndToEndRAG:
    """Test complete RAG pipeline end-to-end."""

    @pytest.mark.asyncio
    async def test_rag_pipeline_components(self):
        """Test RAG pipeline component integration."""
        # This would test the full RAGOracle pipeline when implemented
        # For now, test the foundational components

        chunks = await process_all_documents()

        if not chunks:
            pytest.skip("No documents available for RAG testing")

        # Test that we have diverse sources
        sources = {chunk.source for chunk in chunks}
        assert len(sources) >= 1, "Should have at least one data source"

        # Test that chunks have meaningful content
        for chunk in chunks[:5]:  # Test first few chunks
            assert len(chunk.text.strip()) > 10, "Chunk should have meaningful content"
            assert chunk.metadata.get("text_length", 0) == len(chunk.text), "Metadata should match content"


if __name__ == "__main__":
    # Run quick integration test
    import asyncio

    async def quick_test():
        print("🧪 QUICK RAG SYSTEM INTEGRATION TEST")
        print("=" * 60)

        try:
            # Test data processing
            print("📄 Processing documents...")
            chunks = await process_all_documents()

            if not chunks:
                print("❌ No documents available for testing")
                return

            print(f"✅ Generated {len(chunks)} chunks")

            # Show some stats
            sources = {chunk.source for chunk in chunks}
            sections = {chunk.section for chunk in chunks}
            print(f"📊 Sources: {sorted(sources)}")
            print(f"📑 Sections: {sorted(sections)}")

            # Show sample chunks
            for i, chunk in enumerate(chunks[:3]):
                print(f"\\nSample {i+1}:")
                print(f"  Source: {chunk.source}")
                print(f"  Section: {chunk.section}")
                print(f"  Text: {chunk.text[:100]}...")

            print("\\n🎉 DATA PROCESSING WORKING!")
            print("Next step: Vector store integration complete")

        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()

    print("Running quick integration test...")
    asyncio.run(quick_test())
