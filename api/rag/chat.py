"""
RAG Chat API for Vercel Serverless

Handles conversational queries through the complete RAG pipeline.
Optimized for Vercel serverless with efficient processing and caching.
"""

import json
import os
import time
from typing import Dict, Any, Optional
import asyncio
from pathlib import Path

# Add src to path
current_dir = Path(__file__).resolve()
project_root = current_dir.parent.parent
src_dir = project_root / "src"
if str(src_dir) not in os.environ.get('PYTHONPATH', '').split(':'):
    os.environ['PYTHONPATH'] = f"{src_dir}:{os.environ.get('PYTHONPATH', '')}"

try:
    from src.services.rag.rag_pipeline import RAGPipeline, QueryContext, RAGResponse
    from src.config import get_rag_config
    RAG_AVAILABLE = True
except ImportError as e:
    print(f"Warning: RAG components not available: {e}")
    RAG_AVAILABLE = False

# Global RAG pipeline instance (cached for serverless)
_rag_pipeline: Optional[RAGPipeline] = None


async def initialize_rag_pipeline() -> bool:
    """
    Initialize or retrieve cached RAG pipeline.

    In serverless, this should be cached between requests.
    """
    global _rag_pipeline

    if _rag_pipeline is None and RAG_AVAILABLE:
        try:
            print("🔧 Initializing RAG Pipeline for serverless...")
            _rag_pipeline = RAGPipeline()

            success = await _rag_pipeline.initialize()
            if success:
                print("✅ RAG Pipeline initialized successfully")
                return True
            else:
                print("❌ RAG Pipeline initialization failed")
                return False

        except Exception as e:
            print(f"❌ RAG Pipeline initialization error: {e}")
            return False

    elif _rag_pipeline is not None:
        print("✅ Using cached RAG Pipeline")
        return True

    return False


def create_vercel_response(status_code: int = 200,
                          body: Any = None,
                          headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Create Vercel serverless function response.

    Args:
        status_code: HTTP status code
        body: Response body (will be JSON serialized)
        headers: Additional headers

    Returns:
        Vercel response dict
    """
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }

    if headers:
        default_headers.update(headers)

    return {
        'statusCode': status_code,
        'headers': default_headers,
        'body': json.dumps(body, default=str) if body is not None else None
    }


def create_error_response(error: str, status_code: int = 500) -> Dict[str, Any]:
    """
    Create standardized error response.

    Args:
        error: Error message
        status_code: HTTP status code

    Returns:
        Error response dict
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps({
            'success': False,
            'error': error,
            'timestamp': int(time.time())
        })
    }


def transform_rag_response(rag_response: RAGResponse) -> Dict[str, Any]:
    """
    Transform RAG response to API-friendly format.

    Args:
        rag_response: Raw RAG response object

    Returns:
        API response dict
    """
    return {
        'success': True,
        'query': rag_response.query,
        'response': rag_response.response,
        'metadata': {
            'confidence': rag_response.confidence,
            'sources': rag_response.sources_used,
            'processing_time': f"{rag_response.processing_time:.2f}s",
            'model_used': rag_response.model_used,
            'timestamp': int(time.time())
        }
    }


async def handle_chat_request(event: Dict[str, Any],
                            context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Main handler for RAG chat requests.

    Accepts POST requests with JSON body containing:
    {
        "message": "User's question",
        "context": {
            "user_location": "remote",
            "tech_level": "expert",
            "urgency": "normal"
        }
    }
    """
    try:
        # Handle preflight OPTIONS request for CORS
        if event.get('httpMethod') == 'OPTIONS':
            return create_vercel_response(200, {'message': 'OK'})

        # Only allow POST requests
        if event.get('httpMethod') != 'POST':
            return create_error_response('Method not allowed. Use POST.', 405)

        # Parse request body
        body_str = event.get('body', '{}')
        if not body_str:
            return create_error_response('Missing request body', 400)

        try:
            request_data = json.loads(body_str)
        except json.JSONDecodeError:
            return create_error_response('Invalid JSON in request body', 400)

        # Extract message
        message = request_data.get('message', '').strip()
        if not message:
            return create_error_response('Message is required and cannot be empty', 400)

        # Validate message length
        if len(message) > 1000:
            return create_error_response('Message too long (max 1000 characters)', 400)

        print(f"💬 Processing chat request: '{message[:100]}{'...' if len(message) > 100 else ''}'")

        # Check if RAG is available
        if not RAG_AVAILABLE:
            fallback_response = {
                'success': True,
                'query': message,
                'response': """I'm currently setting up my conversational capabilities. Here's what I can tell you about my background as an AI/ML Engineer:

• 6+ years of experience in manufacturing automation and predictive systems
• Led projects that reduced prediction errors by 35%
• Automated 20+ hours of weekly reporting through intelligent systems
• Expertise in Python, PyTorch, TensorFlow, AWS cloud infrastructure
• Currently working on predictive maintenance and quality control ML models

Feel free to connect with me directly at matthew.pergolski@gmail.com or on LinkedIn (/matthew-pergolski) to discuss your specific needs.""",
                'metadata': {
                    'fallback': True,
                    'sources': ['Manual Response'],
                    'processing_time': '0.00s'
                }
            }
            return create_vercel_response(200, fallback_response)

        # Initialize RAG pipeline if needed
        pipeline_ready = await initialize_rag_pipeline()
        if not pipeline_ready:
            return create_error_response('RAG system initialization failed', 500)

        # Create query context
        user_context = request_data.get('context', {})
        query_context = QueryContext(
            query=message,
            user_location=user_context.get('user_location'),
            tech_level=user_context.get('tech_level', 'intermediate'),
            urgency=user_context.get('urgency', 'normal'),
            industry=user_context.get('industry')
        )

        # Process query through RAG pipeline
        print("🤖 Processing through RAG pipeline...")
        rag_response = await _rag_pipeline.process_query(message, query_context)

        if not rag_response:
            return create_error_response('Failed to process query', 500)

        # Transform and return response
        api_response = transform_rag_response(rag_response)

        print(f"✅ RAG response generated in {rag_response.processing_time:.2f}s")

        return create_vercel_response(200, api_response)

    except Exception as e:
        print(f"❌ Chat API error: {e}")
        import traceback
        traceback.print_exc()

        return create_error_response(f'Internal server error: {str(e)}', 500)


# Vercel serverless function entry point
def handler(event: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Vercel serverless function entry point.

    Args:
        event: Vercel event dict
        context: Vercel context

    Returns:
        Vercel response dict
    """
    try:
        # Run the async handler in event loop
        result = asyncio.run(handle_chat_request(event, context))
        return result

    except Exception as e:
        print(f"❌ Handler error: {e}")
        return create_error_response('Unhandled error in handler', 500)


# Test function
async def test_chat_api():
    """Test the chat API functionality."""
    print("🧪 Testing Chat API...")

    test_event = {
        'httpMethod': 'POST',
        'body': json.dumps({
            'message': 'What Python experience do you have?',
            'context': {
                'user_location': 'remote',
                'tech_level': 'expert'
            }
        })
    }

    result = await handle_chat_request(test_event)

    print(f"Status: {result['statusCode']}")
    if result.get('body'):
        response_data = json.loads(result['body'])
        print(f"Success: {response_data.get('success', False)}")

        if response_data.get('response'):
            print(f"Response: {response_data['response'][:200]}...")

        if response_data.get('metadata'):
            metadata = response_data['metadata']
            print(f"Processing time: {metadata.get('processing_time')}")
            print(f"Model used: {metadata.get('model_used')}")
            print(f"Sources: {metadata.get('sources')}")

    print("✅ Chat API test complete!")


if __name__ == "__main__":
    # Local testing
    asyncio.run(test_chat_api())
