#!/usr/bin/env python3
"""
Test script to examine ChromaDB schema and collection structure.

This shows how the vector database is organized with collections,
documents, embeddings, and metadata.
"""

import sys
import os
from pathlib import Path

# Add src to path
current_dir = Path(__file__).resolve().parent.parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

import chromadb
from chromadb.config import Settings
import json
from datetime import datetime

def inspect_chroma_collection():
    """Inspect the portfolio_rag collection schema and data."""

    print("🔍 CHROMADB INSPECTION REPORT")
    print("=" * 60)

    try:
        # Connect to ChromaDB
        client = chromadb.PersistentClient(
            path="data/rag/vectors.db"
        )

        # Get portfolio_rag collection
        collection = client.get_collection("portfolio_rag")

        # Get collection statistics
        count = collection.count()
        print(f"📊 Collection: portfolio_rag")
        print(f"📄 Document Count: {count}")
        print(f"📋 Status: {collection.status if hasattr(collection, 'status') else 'Active'}\\n")

        if count > 0:
            # Sample retrieval to inspect structure
            print("📖 SAMPLE DATA INSPECTION:")
            print("-" * 40)

            # Get first few documents with their metadata
            results = collection.get(
                limit=3,
                include=["documents", "metadatas", "embeddings"]
            )

            # Display schema structure
            for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
                print(f"\\n📝 Document {i+1}:")
                print(f"   Content: {doc[:100]}..." if len(doc) > 100 else f"   Content: {doc}")
                print(f"   Metadata: {json.dumps(metadata, indent=2)}")

                # Get embedding dimensions (show first 5 values)
                if results.get('embeddings') is not None and len(results.get('embeddings', [])) > i:
                    emb = results['embeddings'][i]
                    emb_sample = [round(x, 4) for x in emb[:5]]
                    print(f"   Embedding: {emb_sample}... (length: {len(emb)})")

            # Search test
            print("\\n🔍 SEARCH TEST:")
            print("-" * 30)

            search_results = collection.query(
                query_texts=["Python"],
                n_results=2,
                include=["documents", "metadatas", "distances"]
            )

            for i, (doc, metadata, distance) in enumerate(zip(
                search_results['documents'][0],
                search_results['metadatas'][0],
                search_results['distances'][0]
            )):
                print(f"\\nSearch Result {i+1}:")
                print(f"   Distance: {distance:.4f}")
                print(f"   Content: {doc[:150]}...")

        # Collection metadata
        print("\\nℹ️  COLLECTION METADATA:")
        print("-" * 30)

        # Try to get collection info
        try:
            meta = collection.metadata
            print(f"Collection Metadata: {meta}")
        except:
            print("Collection Metadata: Not available")

        # Show total embeddings dimension
        if count > 0 and results.get('embeddings') is not None and len(results.get('embeddings', [])) > 0:
            emb_dim = len(results['embeddings'][0])
            print(f"Embeddings Dimension: {emb_dim}")

        print("\\n✅ ChromaDB Inspection Complete!")
        print("=" * 60)

    except Exception as e:
        print(f"❌ ChromaDB Inspection Failed: {e}")
        import traceback
        traceback.print_exc()

        print("\\n🔧 CHROMADB DIAGNOSTICS:")
        print("-" * 30)

        # Check if database files exist
        db_path = Path("data/rag/vectors.db")
        if not db_path.exists():
            print(f"❌ Database path not found: {db_path.absolute()}")
            print("💡 Ensure data/rag/ directory exists and is writable")
        else:
            print(f"✅ Database path exists: {db_path.absolute()}")

            # List contents
            if db_path.is_dir():
                files = list(db_path.iterdir())
                print(f"📁 Database files: {[f.name for f in files]}")

if __name__ == "__main__":
    inspect_chroma_collection()
