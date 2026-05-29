"""
Comprehensive RAG generation engine supporting multiple free inference APIs.

Supports:
- HuggingFace Inference API (totally free, no rate limits for small models)
- Groq API (free tier)
- Together AI (free tier)
- Local models for those who can deploy them

Optimized for Vercel serverless constraints.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Any, Dict
from datetime import datetime

# Import requests for API calls
import requests
from src.config import get_rag_config, RAGConfig


class GenerationEngine:
    """
    Universal generation engine supporting multiple free inference backends.

    Priority order:
    1. HuggingFace Inference API (free, no download)
    2. Groq API (free tier)
    3. Together AI (free tier)
    4. Local llama-cpp-python (if model exists)
    5. Fallback responses (guaranteed)
    """

    def __init__(self, config: RAGConfig):
        self.config = config
        self.model_loaded = False
        self.backend = "fallback"  # Will be set to actual backend

        # Initialize all possible backends
        self.backends = self._init_backends()

    def _init_backends(self) -> Dict[str, Dict[str, Any]]:
        """Initialize all available generation backends."""
        backends = {}

        # Backend 1: HuggingFace Inference API (TOTALLY FREE)
        hf_token = os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_API_KEY")
        if hf_token or not hf_token:  # HF allows anonymous requests for some models
            backends["huggingface"] = {
                "api_key": hf_token,
                "base_url": "https://api-inference.huggingface.co/models",
                "models": {
                    "phi-2": "microsoft/phi-2",  # Free, ~2.7GB - Default
                    "tinyllama": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # Free, ~636MB
                },
                "enabled": True
            }

        # Backend 2: Groq API (free tier available)
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            backends["groq"] = {
                "api_key": groq_key,
                "base_url": "https://api.groq.com/openai/v1/chat/completions",
                "models": ["mixtral-8x7b-32768", "llama2-70b-4096"],
                "enabled": True
            }

        # Backend 3: Together AI (free tier)
        together_key = os.getenv("TOGETHER_API_KEY")
        if together_key:
            backends["together"] = {
                "api_key": together_key,
                "base_url": "https://api.together.ai/v1/chat/completions",
                "models": ["togethercomputer/llama-2-7b-chat", "mistralai/Mixtral-8x7B-Instruct-v0.1"],
                "enabled": True
            }

        # Backend 4: Local llama-cpp-python (for those who can deploy)
        try:
            from llama_cpp import Llama
            backends["local"] = {
                "enabled": True,
                "model_path": self._get_local_model_path(),
            }
        except ImportError:
            backends["local"] = {
                "enabled": False,
                "reason": "llama-cpp-python not installed"
            }

        # Backend 5: Fallback (always available)
        backends["fallback"] = {
            "enabled": True,
            "responses": self._get_fallback_responses()
        }

        print(f"🤖 Available generation backends: {list(backends.keys())}")
        return backends

    def _get_local_model_path(self) -> Optional[str]:
        """Check if local model exists for fallback processing."""
        models_dir = Path("/tmp/rag_models")

        # Check for any local model file (fallback for Vercel/serverless)
        for model_file in models_dir.glob("*.gguf"):
            if model_file.stat().st_size > 100000000:  # Minimum size for usable model
                return str(model_file)

        return None

    def generate_response(self, query: str, context_chunks: str) -> str:
        """
        Generate response using available backends (prioritized).

        Priority: HF Inference → Groq → Together → Local → Fallback
        """
        # Try each backend in priority order
        backends_priority = ["huggingface", "groq", "together", "local", "fallback"]

        for backend_name in backends_priority:
            if backend_name in self.backends and self.backends[backend_name]["enabled"]:
                try:
                    print(f"🔄 Trying {backend_name} backend...")

                    if backend_name == "huggingface":
                        response = self._call_huggingface(query, context_chunks)
                    elif backend_name == "groq":
                        response = self._call_groq(query, context_chunks)
                    elif backend_name == "together":
                        response = self._call_together(query, context_chunks)
                    elif backend_name == "local":
                        response = self._call_local_model(query, context_chunks)
                    elif backend_name == "fallback":
                        response = self._get_contextual_fallback(query, context_chunks)

                    if response and len(response.strip()) > 10:
                        print(f"✅ {backend_name.capitalize()} backend successful")
                        print(f"📝 Response: {response[:100]}...")
                        self.backend = backend_name
                        return response

                except Exception as e:
                    print(f"⚠️ {backend_name} failed: {e}")
                    continue

        # Ultimate fallback
        fallback_response = self._get_contextual_fallback(query, context_chunks)
        print(f"🔄 Using contextual fallback")
        print(f"📝 Fallback response: {fallback_response[:100]}...")
        return fallback_response

    def _call_huggingface(self, query: str, context: str) -> Optional[str]:
        """Call HuggingFace Inference API (totally free, no authentication needed)."""
        try:
            # Use phi-2 (free, no auth required)
            model_id = "microsoft/phi-2"
            url = f"https://api-inference.huggingface.co/models/{model_id}"

            system_prompt = """You are Matt Pergolski, an AI/ML engineer helping visitors understand my background.
Keep responses under 200 words, focused on my experience in Python, ML, and manufacturing automation.
Always end with a call-to-action."""

            prompt = f"{system_prompt}\n\nContext: {context[:500]}\n\nUser: {query}\n\nMatt:"

            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 150,
                    "temperature": 0.3,
                    "do_sample": True,
                    "return_full_text": False
                }
            }

            # Headers (optional token for higher rate limits)
            headers = {"Content-Type": "application/json"}
            hf_token = self.backends["huggingface"]["api_key"]
            if hf_token:
                headers["Authorization"] = f"Bearer {hf_token}"

            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated = result[0].get("generated_text", "").strip()
                    if len(generated) > 10:
                        return self._clean_response(generated)

            return None

        except Exception as e:
            print(f"HF API error: {e}")
            return None

    def _call_groq(self, query: str, context: str) -> Optional[str]:
        """Call Groq API (free tier available)."""
        try:
            url = self.backends["groq"]["base_url"]
            api_key = self.backends["groq"]["api_key"]

            messages = [
                {
                    "role": "system",
                    "content": "You are Matt Pergolski, an AI/ML engineer. Keep responses focused, under 200 words. Always suggest next steps like connecting on LinkedIn."
                },
                {
                    "role": "user",
                    "content": f"Context about Matt: {context[:500]}\n\nQuestion: {query}"
                }
            ]

            payload = {
                "model": "mixtral-8x7b-32768",
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 200,
                "top_p": 0.9
            }

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                return self._clean_response(content)

        except Exception as e:
            print(f"Groq API error: {e}")

        return None

    def _call_together(self, query: str, context: str) -> Optional[str]:
        """Call Together AI API (free tier available)."""
        try:
            url = self.backends["together"]["base_url"]
            api_key = self.backends["together"]["api_key"]

            messages = [
                {
                    "role": "system",
                    "content": "You are Matt Pergolski, an AI/ML engineer helping portfolio visitors. Keep responses focused, professional, and end with call-to-actions."
                },
                {
                    "role": "user",
                    "content": f"Based on this context about Matt: {context[:500]}\n\nAnswer this question: {query}"
                }
            ]

            payload = {
                "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 200
            }

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                return self._clean_response(content)

        except Exception as e:
            print(f"Together AI error: {e}")

        return None

    def _call_local_model(self, query: str, context: str) -> Optional[str]:
        """Call local llama-cpp-python model (if available)."""
        if not self.backends["local"]["enabled"]:
            return None

        try:
            from llama_cpp import Llama

            model_path = self.backends["local"]["model_path"]
            if not model_path:
                return None

            # Load model (only once)
            if not self.model_loaded:
                self.model = Llama(
                    model_path=model_path,
                    n_ctx=512,
                    n_threads=1,
                    verbose=False
                )
                self.model_loaded = True

            prompt = f"""You are Matt Pergolski, an AI/ML engineer.
Context: {context[:500]}
User: {query}
Matt: """

            output = self.model(
                prompt,
                max_tokens=150,
                temperature=0.3,
                echo=False
            )

            if output and len(output) > 0:
                response = output[0].get("text", "").strip()
                return self._clean_response(response)

        except Exception as e:
            print(f"Local model error: {e}")

        return None

    def _clean_response(self, response: str) -> str:
        """Clean and sanitize model responses."""
        if not response:
            return ""

        # Remove common artifacts
        artifacts = [
            "AI:", "Assistant:", "Matt:", "Response:",
            "###", "---", "*", "_", "You:", "User:"
        ]

        for artifact in artifacts:
            response = response.replace(artifact, "").strip()
            if "\n" in response:
                response = "\n".join([line for line in response.split("\n") if not line.startswith(artifact)])

        return response.strip()[:500]  # Limit length

    def _get_contextual_fallback(self, query: str, context: str) -> str:
        """Generate contextual fallback responses based on query type."""
        query_lower = query.lower()

        # Context-aware responses
        context_lower = context.lower()

        base_responses = {
            "python": [
                "I've been working with Python for 6+ years, specializing in machine learning and automation. I've led projects using TensorFlow, PyTorch, and scikit-learn to reduce prediction errors by 35%. My current work involves predictive maintenance systems and quality control."
            ],
            "experience": [
                "In my role as Senior AI/ML Engineer at Lockheed Martin, I led cross-functional teams that automated 20+ hours of weekly reporting through intelligent prediction systems. I work primarily with AWS infrastructure, Docker containers, and advanced ML pipelines.",
                "With 6+ years in manufacturing AI and data science, I've focused on predictive maintenance and quality control systems. My recent project reduced prediction errors by 35% while automating manual workflows."
            ],
            "project": [
                "One of my key projects involved building an automated quality control system that saved 20+ hours weekly. I used Python, TensorFlow, AWS, and Docker to create a scalable solution that reduced prediction errors significantly."
            ],
            "default": [
                "I specialize in AI/ML engineering with a focus on manufacturing automation and predictive systems. I've led projects that achieved measurable business impact through data-driven approaches.",
                "As an AI/ML engineer with defense contracting experience, I excel at deploying reliable systems that combine domain expertise with cutting-edge technology.",
                "My background spans 6+ years in ML automation, predictive maintenance, and data pipeline optimization. I'm passionate about creating systems that deliver real business value."
            ]
        }

        # Choose response based on query
        response_key = "default"
        if "python" in query_lower:
            response_key = "python"
        elif any(word in query_lower for word in ["experience", "background", "work", "job", "role"]):
            response_key = "experience"
        elif any(word in query_lower for word in ["project", "build", "system", "automation"]):
            response_key = "project"

        responses = base_responses[response_key]
        response = responses[0]  # Pick first response

        # Add call-to-action
        response += " I'd love to connect on LinkedIn (/matthew-pergolski) to discuss how my experience could benefit your projects!"

        return response

    def _get_fallback_responses(self) -> Dict[str, List[str]]:
        """Get pre-defined fallback responses."""
        return {
            "general": [
                "I'm Matt Pergolski, an AI/ML engineer with 6+ years in manufacturing automation and data science. I specialize in creating intelligent prediction systems that drive business value.",
                "With experience at Lockheed Martin and in various AI projects, I focus on predictive maintenance, quality control, and automated data pipelines."
            ],
            "technical": [
                "My technical expertise includes Python, TensorFlow, PyTorch, AWS, Docker, and ML automation. I've led teams that reduced prediction errors by 35% through optimized AI systems.",
                "I excel in deploying ML models at scale, with experience in model optimization, deployment automation, and system reliability engineering."
            ]
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get backend statistics and status."""
        return {
            "current_backend": self.backend,
            "available_backends": {k: v["enabled"] for k, v in self.backends.items()},
            "model_loaded": self.model_loaded,
            "backends_status": {
                k: {
                    "enabled": v["enabled"],
                    "has_api_key": bool(v.get("api_key", "")),
                    "models_available": len(v.get("models", []))
                }
                for k, v in self.backends.items()
            }
        }
