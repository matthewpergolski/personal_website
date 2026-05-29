#!/usr/bin/env python3
"""
Final integration test for the complete RAG vector store pipeline.
Tests Phase 3: Vector Database & Embeddings end-to-end.
"""

import os
import sys
import asyncio

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.abspath(os.path.join(parent_dir, "src"))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from src.services.rag.vector_store import VectorStoreManager
from src.services.rag.data_ingestion import process_all_documents
from src.config import get_rag_config


async def test_complete_rag_vector_store():
    """Test end-to-end RAG vector store integration."""

    print("🚀 PHASE 3: VECTOR DATABASE & EMBEDDINGS")
    print("🔥 COMPREHENSIVE INTEGRATION TEST")
    print("=" * 70)

    try:
        # STEP 1: Configuration Check
        print("📋 STEP 1: Configuration")
        config = get_rag_config()
        print(f"   ✅ Embedding model: {config.embedding_model}")
        print(f"   ✅ Vector DB path: {config.vector_db_path}")
        print(f"   ✅ Chunk size: {config.chunk_size}")

        # STEP 2: Document Processing
        print("\\n📄 STEP 2: Document Processing")
        chunks = await process_all_documents()

        if not chunks:
            print("   ❌ No document chunks generated")
            return False

        print(f"   ✅ Processed {len(chunks)} document chunks")
        sections = {chunk.section for chunk in chunks}
        sources = {chunk.source for chunk in chunks}

        print(f"   📊 Sections: {sorted(sections)}")
        print(f"   🔗 Sources: {sorted(sources)}")

        # STEP 3: Vector Store Initialization
        print("\\n🗄️  STEP 3: Vector Store Initialization")
        manager = VectorStoreManager()

        result = manager.initialize()
        if result is None:
            print("   ❌ Vector store initialization failed - returned None")
            return False
        elif result is True:
            print("   ✅ Vector store initialized successfully!")
        else:
            print(f"   ❓ Unexpected initialization result: {result}")
            return False

        # STEP 4: Document Addition
        print("\\n📝 STEP 4: Adding Documents to Vector Store")
        success = manager.add_documents(chunks)

        if not success:
            print("   ❌ Failed to add documents to vector store")
            return False

        print("   ✅ Documents successfully added to vector store")

        # STEP 5: Statistics & Verification
        print("\\n📊 STEP 5: Statistics & Verification")
        stats = manager.get_stats()

        doc_count = stats.get("total_documents", 0)
        sources_counts = stats.get("sources", {})

        print(f"   📈 Total documents indexed: {doc_count}")
        print(f"   🔗 Source distribution: {sources_counts}")
        print(f"   ✅ Expected {len(chunks)} documents, got {doc_count}")

        if doc_count != len(chunks):
            print("   ⚠️  Document count mismatch")
            return False

        # STEP 6: Vector Search Testing
        print("\\n🔍 STEP 6: Vector Search Testing")

        test_queries = [
            "What are your machine learning skills?",
            "Tell me about your experience with AI projects",
            "What programming languages do you use?"
        ]

        all_tests_passed = True
        for i, query in enumerate(test_queries, 1):
            print(f"   Query {i}: '{query}'")

            try:
                results = manager.search_similar(query, n_results=3)

                if not results:
                    print("     ❌ No search results returned")
                    all_tests_passed = False
                    continue

                documents = results.get("documents", [])
                metadatas = results.get("metadatas", [])
                distances = results.get("distances", [])

                print(f"     ✅ Found {len(documents)} relevant documents")

                if documents and metadatas and len(documents) > 0:
                    source = metadatas[0].get("source", "unknown")
                    section = metadatas[0].get("section", "unknown")
                    print(f"     📄 Top result: [{source}/{section}]")
                    print(f"     📝 Content: {documents[0][:80]}...")

                # Verify results have expected structure
                if (not documents or not metadatas or not distances or
                    len(documents) != len(metadatas) or len(documents) != len(distances[0])):
                    print("     ⚠️  Search result structure issue"                    all_tests_passed = False

            except Exception as e:
                print(f"     ❌ Search failed: {e}")
                all_tests_passed = False

        print("\\n" + "=" * 70)
        if all_tests_passed:
            print("🎉 PHASE 3: VECTOR DATABASE & EMBEDDINGS - COMPLETE! 🎉")
            print("✅ All tests passed - Vector store fully functional")
            print("🔥 Ready to proceed to Phase 4: Model Inference & Generation")
            return True
        else:
            print("❌ Some tests failed - Vector store needs fixes")
            return False

    except Exception as e:
        print(f"❌ Integration test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Starting RAG Vector Store Integration Test...")

    success = asyncio.run(test_complete_rag_vector_store())
    sys.exit(0 if success else 1)
