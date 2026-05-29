# Implementation Plan for FastHTML Chatbot Portfolio Deployment

## Overview
Update and deploy the existing FastHTML portfolio website with a complete chatbot implementation that indexes GitHub projects and resume data. The system uses RAG (Retrieval-Augmented Generation) to provide contextual responses based on professional experience, with Vercel serverless deployment and local testing capabilities.

## Types
Describe the data structures and interfaces for the chatbot system including message objects, context handling, and response formats.

Message Structure:
```python
class ChatMessage:
    content: str
    role: str  # 'user' or 'assistant'
    timestamp: str
    context: Dict[str, Any]  # tech_level, urgency, user_location
```

Query Context:
```python
class QueryContext:
    query: str
    user_location: Optional[str] = None
    tech_level: str = "intermediate"
    urgency: str = "normal"
    industry: Optional[str] = None
```

RAG Response:
```python
class RAGResponse:
    query: str
    response: str
    confidence: float
    sources_used: List[str]
    processing_time: float
```

## Files
Identify existing files and modifications needed for complete deployment setup.

New files to create:
- `.devcontainer/Dockerfile` (updated to include Vercel CLI)
- `api/__init__.py` (if missing for proper package structure)
- `build_rag.py` (already exists, ensure proper data ingestion)

Existing files to modify:
- `envs.sh` (add missing environment variables for production)
- `src/main.py` (already includes chat widget, verify integration)
- `src/config.py` (already configured, ensure proper env handling)
- `src/services/rag/rag_pipeline.py` (already implemented, verify model setup)
- `src/components/chat/widget.py` (already implemented, test functionality)
- `api/rag/chat.py` (already implemented for Vercel serverless)
- `vercel.json` (exists, verify routing)

Files to delete/migrate: None identified.

Configuration updates:
- `pyproject.toml` (ensure dependencies for AI models and vector store)
- `requirements.txt` (duplicate of pyproject.toml, can be removed)

## Functions
Specify functions for querying data, processing responses, and managing deployment.

New functions:
- `install_vercel_cli()` (added to Dockerfile)
- `validate_environment()` (in build_rag.py or src/config.py)

Modified functions:
- `initialize_rag_pipeline()` (already in api/rag/chat.py, add error handling)
- `process_query()` (already in rag_pipeline.py, optimize for Vercel limits)
- `render_chat_widget()` (already in widget.py, ensure responsive design)

Removed functions: None identified.

## Classes
Update class representations for data handling and API interactions.

New classes:
- `VercelClient` (utility for Vercel deployment operations)
- `EnvironmentValidator` (for configuration validation)

Modified classes:
- `ChatWidget` (already implemented in widget.py, enhance with theme support)
- `RAGPipeline` (already implemented, add health check methods)
- `VectorStoreManager` (already implemented, verify ChromaDB compatibility)

Removed classes: None identified.

## Dependencies
Specify required packages and development tools for full system operation.

New packages:
- `vercel` (CLI for deployment management)
- `huggingface-hub` (optional, for API interactions)
- `uvicorn` (for local development server)

Version changes: None required, current versions in pyproject.toml are compatible.

Integration requirements:
- HuggingFace API for model inference
- ChromaDB vector store (already configured)
- GitHub API for projects integration
- Google Docs API for resume access

## Testing
Establish comprehensive testing strategy for local development and deployment validation.

Test requirements:
- `tests/test_chat_integration.py` (end-to-end chat functionality)
- `tests/test_vercel_deployment.py` (deployment simulation)
- `tests/test_rag_pipeline.py` (data processing and response generation)

Existing test modifications:
- `tests/test_rag_components.py` (enhance with API endpoint testing)
- `test_simple_vector_store.py` (validate data persistence)

Validation strategies:
- Local testing with `uv run python src/main.py`
- API endpoint testing with curl/postman
- Vercel deployment simulation with build scripts
- Environment variable validation before deployment

## Implementation Order
Define the sequence for testing, deployment setup, and production readiness.

1. Review current RAG pipeline implementation and data ingestion
2. Test local chatbot functionality with existing components
3. Verify HuggingFace API integration and Qwen model availability
4. Validate Vercel serverless API endpoints
5. Install Vercel CLI in devcontainer environment
6. Configure production environment variables
7. Test complete deployment pipeline locally
8. Execute Vercel deployment with health checks
9. Validate production chatbot functionality
10. Monitor and optimize for Vercel performance limits
