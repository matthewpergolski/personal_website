#!/usr/bin/env python3
"""
Build script for RAG system preprocessing.

This script is designed to run during deployment build time to:
1. Process resume PDF and GitHub projects
2. Generate embeddings and vector database
3. Store results for runtime usage

For Vercel deployment, call this in your build command:
  python build_rag.py

Output will be stored in data/rag/ for inclusion in deployment.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.rag.data_ingestion import process_all_documents
from src.services.rag.vector_store import VectorStoreManager
from src.config import get_rag_config
from datetime import datetime

async def build_rag_system():
    """
    Build the complete RAG system by processing documents and creating vector database.

    This function is designed to run during deployment build time (not runtime).
    """
    print("🏗️  Starting RAG system build...")

    # Get configuration
    config = get_rag_config()
    start_time = datetime.now()

    try:
        # Step 1: Document ingestion
        print("📄 Processing documents...")
        chunks = await process_all_documents()

        if not chunks:
            print("❌ No documents processed. Check your RESUME_URL configuration.")
            print("Set RESUME_URL environment variable to your resume PDF URL.")
            return False

        print(f"✅ Processed {len(chunks)} document chunks")

        # Step 2: Vector store setup
        print("🗄️  Setting up vector store...")
        vector_store = VectorStoreManager(
            persist_directory=config.vector_db_path,
            collection_name="portfolio_docs"
        )

        # Step 3: Generate embeddings and store
        print("🧮 Generating embeddings...")
        await vector_store.add_documents(chunks)
        print("✅ Embeddings generated and stored")

        # Step 4: Build statistics
        stats = {
            "total_chunks": len(chunks),
            "build_time": (datetime.now() - start_time).total_seconds(),
            "timestamp": datetime.now().isoformat(),
            "config": {
                "chunk_size": config.chunk_size,
                "chunk_overlap": config.chunk_overlap,
                "embedding_model": config.embedding_model
            }
        }

        # Save build statistics
        stats_path = Path(config.vector_db_path) / "build_stats.json"
        stats_path.parent.mkdir(parents=True, exist_ok=True)

        with open(stats_path, 'w') as f:
            import json
            json.dump(stats, f, indent=2)

        print("📊 Build statistics saved")
        print(".1f")
        print(f"💾 Vector database stored at: {config.vector_db_path}")
        print("✅ RAG system build complete!")

        # Test retrieval (optional, but good for validation)
        test_retrieval = await vector_store.similarity_search("software engineering", 3)
        print(f"🧪 Test retrieval: Found {len(test_retrieval)} relevant chunks")

        return True

    except Exception as e:
        print(f"❌ Build failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point for build script."""
    # Ensure we're in the right working directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    print("📁 Working directory:", script_dir)
    print("🔧 Python path:", sys.path)
    print("🐍 Python:", sys.version)

    # Check required environment variables
    required_env_vars = {
        'GITHUB_USERNAME': 'Your GitHub username',
        'GITHUB_TOKEN': 'Your GitHub API token',
        'RESUME_URL': 'URL to your resume PDF'
    }

    missing_vars = []
    for var_name, description in required_env_vars.items():
        if not os.getenv(var_name):
            missing_vars.append(f"{var_name}: {description}")

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   • {var}")
        print("\nSet these in your .env file, envs.sh, or Vercel environment variables.")
        sys.exit(1)

    print("🔧 Checking required environment variables...")
    for var_name in required_env_vars:
        print(f"   ✅ {var_name}")

    print("\n💡 Important: Ensure your RESUME_URL is publicly accessible!")
    print("   Google Drive PDFs must have share permissions set to 'Anyone with the link can view'")
    print()

    # Run the build
    success = asyncio.run(build_rag_system())

    if success:
        print("\n🎉 RAG system successfully built!")
        print("📦 Ready for deployment. The vector database is included in the build.")
        sys.exit(0)
    else:
        print("\n😞 RAG system build failed.")
        print("🔍 Check the error messages above and fix any issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()
