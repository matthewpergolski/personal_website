"""
Test suite for ChromaDB vector store functionality.

Tests embedding generation, storage, and retrieval.
"""

import os
import sys
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock
import pytest
from unittest.mock import patch

import asyncio
from src.services.rag.vector_store import VectorStoreManager
from src.services.rag.data_ingestion import DocumentChunk
from src.config import get_rag_config


@pytest.mark.asyncio
async def test_vector_store_integration():
    """Integration test with real document processing."""
    from src.services.rag.data_ingestion import process_all_documents

    # Process real documents
    chunks = await process_all_documents()

    if not chunks:
        pytest.skip("No documents to process")
        return

    assert len(chunks) > 0
    assert all(isinstance(chunk, DocumentChunk) for chunk in chunks)

    # Test VectorStoreManager with real data
    manager = VectorStoreManager()

    # Check configuration
    config = get_rag_config()
    assert config.embedding_model != ""
    assert config.vector_db_path != ""

    # Initialize the system
    success = manager.initialize()
    assert success, "Failed to initialize vector store"

    # Add documents
    success = manager.add_documents(chunks)
    assert success, "Failed to add documents"

    # Verify documents were added
    doc_count = manager.get_document_count()
    assert doc_count == len(chunks), f"Expected {len(chunks)} documents, got {doc_count}"

    # Get stats
    stats = manager.get_stats()
    assert "total_documents" in stats
    assert stats["total_documents"] == len(chunks)

    # Test search with real queries
    test_queries = [
        "What are your machine learning skills?",
        "Tell me about your experience with AI projects",
        "What programming languages do you use?"
    ]

    for query in test_queries:
        results = manager.search_similar(query, n_results=3)

        documents = results.get("documents", [])
        metadatas = results.get("metadatas", [])
        distances = results.get("distances", [])

        # Should have some results
        assert len(documents) > 0, f"No results for query: {query}"
        assert len(metadatas) > 0
        assert len(distances) > 0


def test_vector_store_basic_operations():
    """Test basic vector store operations with mocked dependencies."""
    # Mock the embedding model and ChromaDB to test basic functionality
    with patch('chromadb.PersistentClient') as mock_client:
        with patch('sentence_transformers.SentenceTransformer') as mock_model:
            # Setup minimal mock model that returns a fake embedding
            mock_embedding_model = Mock()
            mock_embedding_model.encode.return_value = [0.1, 0.2, 0.3, 0.4, 0.5] * 10  # 50-dim embedding
            mock_model.return_value = mock_embedding_model

            # Setup ChromaDB mock
            mock_collection = Mock()
            mock_collection.count.return_value = 0
            mock_collection.get.return_value = {"ids": []}
            mock_collection.add.return_value = None  # ChromaDB add returns None on success
            mock_client_instance = Mock()
            mock_client_instance.get_collection.return_value = mock_collection
            mock_client_instance.create_collection.return_value = mock_collection
            mock_client.return_value = mock_client_instance

            # Initialize manager
            manager = VectorStoreManager()
            manager.initialize()

            # Create test documents
            test_chunks = [
                DocumentChunk(
                    text="Python machine learning engineer with 6 years experience",
                    metadata={"source": "resume", "section": "summary"},
                    source="resume_pdf",
                    section="summary"
                ),
                DocumentChunk(
                    text="Developing AI models using TensorFlow and PyTorch",
                    metadata={"source": "resume", "section": "experience"},
                    source="resume_pdf",
                    section="experience"
                )
            ]

            # Test adding documents
            success = manager.add_documents(test_chunks)

            assert success, "Failed to add documents"
            # Verify the mock was called correctly
            mock_model.return_value.encode.assert_called()


def test_vector_store_search_with_mocks():
    """Test search functionality with mocked ChromaDB."""

    with patch('chromadb.PersistentClient') as mock_client:
        with patch('sentence_transformers.SentenceTransformer') as mock_model:

            mock_embedding_model = Mock()
            mock_embedding_model.encode.return_value = [0.1, 0.2, 0.3] * 10  # 30-dim embedding
            mock_model.return_value = mock_embedding_model

            # Mock search results
            mock_search_results = {
                "documents": ["Python developer with ML experience", "TensorFlow and AI projects"],
                "metadatas": [
                    {"source": "resume", "section": "experience"},
                    {"source": "github", "section": "project"}
                ],
                "distances": [[0.1, 0.2]]
            }

            mock_collection = Mock()
            mock_collection.count.return_value = 2
            mock_collection.get.return_value = {"ids": ["test1", "test2"], "metadatas": ["meta1", "meta2"]}
            mock_collection.query.return_value = mock_search_results

            mock_client_instance = Mock()
            mock_client_instance.get_collection.return_value = mock_collection
            mock_client.return_value = mock_client_instance

            manager = VectorStoreManager()
            manager.initialize()

            results = manager.search_similar("Python experience", n_results=2)

            assert len(results["documents"]) == 2
            assert "Python developer" in results["documents"][0]
            assert "TensorFlow" in results["documents"][1]


if __name__ == "__main__":
    # Run a quick integration test
    print("🧪 Running Vector Store Integration Test...")

    async def integration_test():
        try:
            # Import the document processing functions
            from src.services.rag.data_ingestion import process_all_documents

            # Process real documents
            print("Processing real documents...")
            chunks = await process_all_documents()

            if not chunks:
                print("❌ No documents to process")
                return

            print(f"✅ Generated {len(chunks)} chunks for embedding")

            # Test VectorStoreManager with real data
            print("Initializing VectorStoreManager...")
            manager = VectorStoreManager()

            # Check configuration
            config = get_rag_config()
            print(f"Embedding model: {config.embedding_model}")
            print(f"Vector DB path: {config.vector_db_path}")

            # Initialize the system
            success = manager.initialize()
            if success:
                print("✅ Vector store initialized successfully")
            else:
                print("❌ Vector store initialization failed")
                return

            # Add documents
            print("Adding documents...")
            success = manager.add_documents(chunks)
            if success:
                print("✅ Successfully added documents to vector store")

                # Get stats
                stats = manager.get_stats()
                print(f"📊 Vector Store Stats: {stats}")

            else:
                print("❌ Failed to add documents")

            # Test search with real queries
            print("\\n🔍 Testing vector search...")

            test_queries = [
                "What are your machine learning skills?",
                "Tell me about your experience with AI projects",
                "What programming languages do you use?"
            ]

            for i, query in enumerate(test_queries[:2]):  # Just first 2 for quick test
                print(f"Query {i+1}: {query}")
                results = manager.search_similar(query, n_results=2)

                documents = results.get("documents", [])
                metadatas = results.get("metadatas", [])
                print(f"  -> Found {len(documents)} results")

                if documents:
                    source = metadatas[0].get('source', 'unknown') if metadatas else 'unknown'
                    print(f"  -> Top result: [{source}] {documents[0][:60]}...")

            print("\\n✅ VECTOR STORE INTEGRATION COMPLETE!")
            print("🔥 Ready to move to Phase 4: Model Inference & Generation")

        except Exception as e:
            print(f"❌ Integration test failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Clean up ChromaDB file if it was created in /tmp
            try:
                config = get_rag_config()
                if config.vector_db_path.startswith('/tmp') and os.path.exists(config.vector_db_path):
                    import shutil
                    shutil.rmtree(config.vector_db_path)
                    print("🧹 Cleaned up temporary ChromaDB files")
            except Exception as e:
                print(f"Error during cleanup: {e}")

    print("Starting async integration test...")
    asyncio.run(integration_test())
