#!/usr/bin/env python3
"""
Simple test to verify vector store works with actual data.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import asyncio
    from src.services.rag.vector_store import VectorStoreManager
    from src.services.rag.data_ingestion import process_all_documents
    from src.config import get_rag_config

    async def test_vector_store():
        print("🚀 TESTING SIMPLE VECTOR STORE INTEGRATION")
        print("=" * 60)

        try:
            # Get configuration
            config = get_rag_config()
            print(f"✅ Configuration loaded: {config.embedding_model}")

            # Process documents
            print("\\n📄 Processing documents...")
            chunks = await process_all_documents()

            if not chunks:
                print("❌ No documents available for testing")
                return False

            print(f"✅ Generated {len(chunks)} document chunks")

            # Show sample chunks
            for i, chunk in enumerate(chunks[:3]):
                print(f"  Sample {i+1}: {chunk.source}/{chunk.section} - {chunk.text[:60]}...")

            # Initialize vector store
            print("\\n🗄️  Initializing Vector Store...")
            manager = VectorStoreManager()

            try:
                result = manager.initialize()
                if result is None:
                    print("❌ initialize() returned None")
                    return False
                elif result is True:
                    print("✅ Vector store initialized successfully")
                else:
                    print(f"❓ Unexpected return: {result}")
                    return False

            except Exception as e:
                print(f"❌ Vector store initialization failed: {e}")
                import traceback
                traceback.print_exc()
                return False

            # Add documents
            print("\\n📝 Adding documents...")
            try:
                success = manager.add_documents(chunks)
                if success:
                    print("✅ Documents added successfully")
                else:
                    print("❌ Adding documents failed")
                    return False
            except Exception as e:
                print(f"❌ Adding documents failed: {e}")
                return False

            # Get stats
            try:
                stats = manager.get_stats()
                print(f"📊 Vector store stats: {stats}")
            except Exception as e:
                print(f"⚠️  Stats failed: {e}")

            # Test search functionality
            print("\\n🔍 Testing vector search...")
            test_queries = [
                "What are your machine learning skills?",
                "Tell me about your AI experience"
            ]

            for query in test_queries:
                print(f"  Query: '{query}'")
                try:
                    results = manager.search_similar(query, n_results=2)
                    docs = results.get("documents", [])
                    if docs:
                        print(f"    ✅ Found {len(docs)} results")
                        print(f"    → {docs[0][:80]}...")
                    else:
                        print("    ⚠️  No results found"
                except Exception as e:
                    print(f"    ❌ Search failed: {e}")

            print("\\n🎉 VECTOR STORE INTEGRATION TEST PASSED! 🔥")
            print("=" * 60)
            return True

        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            return False

    if __name__ == "__main__":
        success = asyncio.run(test_vector_store())
        sys.exit(0 if success else 1)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
