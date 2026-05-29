"""
Complete RAG (Retrieval-Augmented Generation) Pipeline

Orchestrates data ingestion, vector storage, generation, and marketing
layers into a cohesive conversational AI assistant.
"""

import asyncio
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict

from .data_ingestion import process_all_documents, DocumentChunk
from .vector_store import VectorStoreManager
from .generation import GenerationEngine
from .marketing_layer import MarketingLayer, ResponseOptimizer
from src.config import get_rag_config, RAGConfig


@dataclass
class QueryContext:
    """Context information for query processing."""
    query: str
    user_location: Optional[str] = None
    tech_level: str = "intermediate"  # beginner, intermediate, expert
    urgency: str = "normal"  # low, normal, high
    industry: Optional[str] = None
    timestamp: Optional[str] = None


@dataclass
class RAGResponse:
    """Structured response from RAG pipeline."""
    query: str
    response: str
    confidence: float
    sources_used: List[str]
    processing_time: float
    model_used: bool = False


class RAGPipeline:
    """
    Complete Retrieval-Augmented Generation pipeline for portfolio chatbot.

    Handles end-to-end processing:
    1. Query understanding and context enrichment
    2. Document retrieval from vector store
    3. Model-based response generation
    4. Marketing layer enhancement
    5. Response optimization and delivery
    """

    def __init__(self, config: Optional[RAGConfig] = None):
        self.config = config or get_rag_config()

        # Initialize components
        self.vector_store = VectorStoreManager()
        self.generation_engine = GenerationEngine(self.config)
        self.marketing_layer = MarketingLayer()

        # State tracking
        self.initialized = False
        self.documents_loaded = False
        self.document_count = 0

    async def initialize(self) -> bool:
        """
        Initialize the complete RAG pipeline.

        Returns True if successfully initialized, False otherwise.
        """
        try:
            print("🔧 Initializing RAG Pipeline...")

            # Initialize vector store
            if not self.vector_store.initialize():
                print("❌ Vector store initialization failed")
                return False

            # Load and process documents
            print("📄 Processing document sources...")
            chunks = await process_all_documents()

            if not chunks:
                print("⚠️  No documents available for indexing")
                self.initialized = True
                return True

            # Add documents to vector store
            print(f"🗄️  Indexing {len(chunks)} document chunks...")

            if self.vector_store.add_documents(chunks):
                self.documents_loaded = True
                self.document_count = len(chunks)
                print(f"✅ Successfully indexed {self.document_count} chunks")
            else:
                print("❌ Document indexing failed")
                return False

            self.initialized = True
            print("🎉 RAG Pipeline initialized successfully!")
            return True

        except Exception as e:
            print(f"❌ RAG Pipeline initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def process_query(
        self,
        query: str,
        context: Optional[QueryContext] = None
    ) -> RAGResponse:
        """
        Process a user query through the complete RAG pipeline.

        Args:
            query: The user's question
            context: Additional context about the query

        Returns:
            Structured RAG response
        """
        import time
        start_time = time.time()

        try:
            if not self.initialized:
                if not await self.initialize():
                    return self._get_error_response(query, "Pipeline initialization failed", start_time)

            # Enrich query context
            query_context = context or QueryContext(query=query)

            # 1. Semantic retrieval
            print(f"🔍 Retrieving relevant documents for: '{query}'")
            retrieval_results = self.vector_store.search_similar(
                query,
                n_results=3,  # Top 3 most relevant chunks
            )

            if not retrieval_results.get("documents"):
                return self._get_fallback_response(query, "No relevant documents found", start_time)

            # Extract relevant chunks
            relevant_texts = retrieval_results.get("documents", [])
            relevant_metadatas = retrieval_results.get("metadatas", [])

            # Combine retrieved information
            combined_context = self._prepare_context_chunks(relevant_texts, relevant_metadatas)

            # 2. Generate response using model + fallback
            print("🧠 Generating response...")
            raw_response = self.generation_engine.generate_response(query, combined_context)

            if not raw_response or len(raw_response.strip()) < 15:
                raw_response = self._get_smart_fallback_response(query, combined_context)

            # 3. Apply marketing layer
            print("✨ Applying marketing enhancements...")
            marketing_context = asdict(query_context) if query_context else {}
            enhanced_response = self.marketing_layer.enhance_response(raw_response, marketing_context)

            # 4. Final optimization
            final_response = ResponseOptimizer.optimize_for_context(enhanced_response, marketing_context)

            # Extract sources used
            sources_used = self._extract_sources(relevant_metadatas)

            # Calculate confidence (simple heuristic)
            confidence = self._calculate_confidence(relevant_texts, query)

            processing_time = time.time() - start_time

            # Build structured response
            response_obj = RAGResponse(
                query=query,
                response=final_response,
                confidence=confidence,
                sources_used=sources_used,
                processing_time=processing_time,
                model_used=bool(raw_response and len(raw_response) > 15)
            )

            print(f"Processing time: {processing_time:.2f}")
            return response_obj

        except Exception as e:
            print(f"❌ Query processing failed: {e}")
            import traceback
            traceback.print_exc()
            return self._get_error_response(query, str(e), start_time)

    def _prepare_context_chunks(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> str:
        """Prepare retrieved chunks for generation context."""
        # Combine most relevant information
        context_parts = []

        for i, (text, metadata) in enumerate(zip(texts, metadatas)):
            try:
                # Handle ChromaDB list of lists format
                if isinstance(metadata, list):
                    metadata = metadata[0] if metadata else {}

                # Additional safety: handle nested lists in metadata values
                if isinstance(metadata, dict):
                    metadata = {k: (v[0] if isinstance(v, list) and len(v) > 0 else str(v)) for k, v in metadata.items()}
                else:
                    metadata = {}

                # Add source/section information
                source_info = f"Source: {metadata.get('source', 'unknown')}"
                section_info = f"Section: {metadata.get('section', 'general')}"
                context_parts.append(f"{source_info} / {section_info}")
                context_parts.append(str(text)[:300])  # Ensure text is string
                context_parts.append("")  # Empty line for separation

            except Exception as e:
                # Ultimate fallback for any metadata processing issues
                context_parts.append("Source: document / Section: general")
                context_parts.append(str(text)[:300])
                context_parts.append("")

            if i >= 2:  # Limit to top 3 chunks to avoid context overflow
                break

        # Add overall statistics if available
        if self.document_count > 0:
            stats_info = f"Total available information: {self.document_count} indexed chunks covering resume, GitHub projects, and professional experience."
            context_parts.append(stats_info)

        # Ensure all items are strings before joining
        context_parts = [str(part) for part in context_parts if part is not None]
        return "\n".join(context_parts)

    def _extract_sources(self, metadatas: List[Dict[str, Any]]) -> List[str]:
        """Extract unique sources from retrieved metadata."""
        sources = set()
        for metadata in metadatas:
            # Handle ChromaDB list of lists format
            if isinstance(metadata, list):
                metadata = metadata[0] if metadata else {}

            source = metadata.get('source', 'unknown')
            section = metadata.get('section', 'general')

            # Create readable source descriptions
            if source == 'resume_pdf':
                sources.add(f"Resume - {section}")
            elif source == 'github':
                sources.add(f"GitHub Projects - {section}")
            else:
                sources.add(f"{source} - {section}")

        return list(sources)[:5]  # Limit to top 5 sources

    def _calculate_confidence(self, texts: List[str], query: str) -> float:
        """Calculate response confidence score."""
        if not texts:
            return 0.0

        # Handle ChromaDB list of lists format
        processed_texts = []
        for text in texts:
            if isinstance(text, list):
                # Handle nested lists - join list items
                text = " ".join([str(item) for item in text])
            elif isinstance(text, list):
                # Handle single list - convert to string
                text = str(text[0]) if text else ""
            else:
                text = str(text)
            processed_texts.append(text)

        # Simple confidence based on content relevance and length
        query_words = set(query.lower().split())
        match_score = 0.0

        for text in processed_texts:
            if text and isinstance(text, str):
                text_words = set(text.lower().split())
                overlap = len(query_words & text_words)
                relevance = overlap / max(len(query_words), 1)
                match_score += relevance

        # Normalize to 0-1 range
        confidence = min(match_score / len(processed_texts), 1.0)

        # Boost confidence if we have multiple strong matches
        if len(processed_texts) >= 2:
            confidence *= 1.1

        return round(min(confidence, 1.0), 2)

    def _get_smart_fallback_response(self, query: str, context: str) -> str:
        """Generate intelligent fallback when model fails."""
        query_lower = query.lower()

        # Extract some context-aware information from available chunks
        context_lower = context.lower()

        # Technical skills check
        if any(skill in query_lower for skill in ["python", "ml", "machine learning", "ai"]):
            if "python" in context_lower:
                return "I have extensive experience with Python for machine learning and data science, including PyTorch, TensorFlow, and scikit-learn. I've used these technologies in production environments to build automated quality control systems."

        # Leadership/Project management check
        elif any(term in query_lower for term in ["led", "project", "team", "leadership"]):
            if "prediction error" in context_lower or "automated" in context_lower:
                return "I led cross-functional AI projects that achieved significant business impact, including a 35% reduction in prediction errors and automation saving 20+ hours weekly. I excel at bridging technical implementation with business outcomes."

        # Default professional response
        return f"Based on my experience in AI/ML engineering, I'd be happy to discuss how my background in manufacturing automation, Python development, and machine learning could help with your specific needs. My recent projects involve predictive maintenance systems and quality control optimization."

    def _get_fallback_response(self, query: str, reason: str, start_time: float) -> RAGResponse:
        """Get fallback response when processing fails."""
        fallback_text = f"It looks like I can't access that information right now. However, I'd be happy to discuss my experience in AI/ML engineering, Python development, and manufacturing automation projects."

        return RAGResponse(
            query=query,
            response=fallback_text,
            confidence=0.0,
            sources_used=["fallback"],
            processing_time=time.time() - start_time,
            model_used=False
        )

    def _get_error_response(self, query: str, error: str, start_time: float) -> RAGResponse:
        """Get error response when pipeline fails."""
        error_text = "I apologize, but I'm having trouble accessing my information right now. Please feel free to reach out directly about my AI/ML engineering background and project experience."

        print(f"⚠️  RAG Error: {error}")

        return RAGResponse(
            query=query,
            response=error_text,
            confidence=0.0,
            sources_used=["error"],
            processing_time=time.time() - start_time,
            model_used=False
        )

    # Additional utility methods
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive pipeline statistics."""
        base_stats = self.vector_store.get_stats()

        return {
            "pipeline_status": "initialized" if self.initialized else "uninitialized",
            "documents_loaded": self.documents_loaded,
            "total_chunks": self.document_count,
            "generation_engine_loaded": self.generation_engine.model_loaded,
            "vector_store": base_stats,
            "components": {
                "vector_store": True,
                "generation_engine": True,
                "marketing_layer": True,
                "response_optimizer": True
            }
        }

    def reset_pipeline(self) -> bool:
        """Reset the entire pipeline (for development/debugging)."""
        try:
            print("🔄 Resetting RAG Pipeline...")

            # Reset vector store
            self.vector_store.reset_collection()

            # Reset state
            self.initialized = False
            self.documents_loaded = False
            self.document_count = 0

            print("✅ Pipeline reset successfully")
            return True

        except Exception as e:
            print(f"❌ Pipeline reset failed: {e}")
            return False


# Test the complete RAG pipeline
async def test_rag_pipeline():
    """Test the complete RAG pipeline integration."""
    print("🚀 TESTING COMPLETE RAG PIPELINE")
    print("=" * 60)

    # Create pipeline
    pipeline = RAGPipeline()

    # Test queries
    test_queries = [
        "What Python experience do you have?",
        "Tell me about your ML projects",
        "How do you optimize manufacturing processes?",
        "What's your leadership experience?"
    ]

    try:
        # Initialize
        if await pipeline.initialize():
            print("✅ Pipeline initialized successfully")

            # Test queries
            for i, query in enumerate(test_queries, 1):
                print(f"\\n🔍 Test Query {i}: '{query}'")
                print("-" * 40)

                # Process query
                response = await pipeline.process_query(query)

                print(f"Processing time: {response.processing_time:.2f}")
                print(f"Source: {response.sources_used}")
                print(f"Model Used: {response.model_used}")
                print(f"Confidence: {response.confidence}")

                print(f"\\n✨ Response:\\n{response.response[:300]}...")

                print("=" * 40)

        else:
            print("❌ Pipeline initialization failed")

    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()

    print("\\n🎯 COMPLETE RAG PIPELINE TEST FINISHED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_rag_pipeline())
