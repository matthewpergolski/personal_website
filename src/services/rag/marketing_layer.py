"""
Marketing layer for positive framing and strategic positioning.

Adds professional presentation, positive messaging, and strategic CTAs
to RAG responses for better user engagement and business results.
"""

import re
from typing import List, Dict, Any
from datetime import datetime


class MarketingLayer:
    """Enhances RAG responses with positive marketing elements."""

    def __init__(self):
        self.contact_methods = {
            "linkedin": "LinkedIn: /matthew-pergolski",
            "email": "matthew.pergolski@gmail.com",
            "location": "Greater Madison, WI area"
        }

        self.value_propositions = [
            "strategic AI/ML implementation",
            "operational efficiency gains",
            "data-driven decision making",
            "ML model production optimization",
            "automated quality control systems"
        ]

    def enhance_response(self, response: str, context: Dict[str, Any] = None) -> str:
        """Add marketing enhancements to the raw response."""
        if not response or len(response.strip()) < 10:
            return self._get_fallback_marketing_response()

        enhanced = self._apply_positive_framing(response)
        enhanced = self._add_call_to_action(enhanced, context)
        enhanced = self._optimize_engagement(enhanced)

        return enhanced

    def _apply_positive_framing(self, response: str) -> str:
        """Apply positive language patterns and framing."""
        positive_subs = {
            # Emphasize achievements with stronger language
            r"I (worked|developed|built|created)": r"I successfully \1",
            r"I (led|managed|directed)": r"I strategically led",
            r"(reduced|improved|increased)": r"achieved \1",
            r"(successfully|effectively)": r"consistently \1",

            # Enhance technical accomplishments
            r"(built|developed) ([a-zA-Z\s]+) system": r"architected robust \2 systems",
            r"(implemented|deployed) ([a-zA-Z\s]+) model": r"successfully deployed production-grade \2 models",

            # Add result-oriented language
            r"with ([0-9]+)% ": r"demonstrating \1% ",

            # Enhance credibility markers
            r"experience": r"proven expertise",
            r"skills": r"technical proficiency",
            r"(in|with) ([a-zA-Z\s,&]+)": r"specifically in \2 technologies",
        }

        result = response
        for pattern, replacement in positive_subs.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        # Add confidence boosters
        confidence_markers = [
            "As demonstrated in my recent projects",
            "Drawing from my experience leading enterprise ML initiatives",
            "Based on my proven track record with",
            "Leveraging my expertise developed through"
        ]

        # Add one confidence marker if missing
        if not any(marker.lower() in result.lower() for marker in confidence_markers):
            for marker in confidence_markers[:2]:  # Try first two
                if len(result.split()) < 30:  # Only for shorter responses
                    result = f"{marker}, {result.lower()}{result[1:]}"
                    break

        return result

    def _add_call_to_action(self, response: str, context: Dict[str, Any] = None) -> str:
        """Add strategic call-to-action based on response content."""
        response_lower = response.lower()

        # Determine CTA type based on content
        cta_options = {
            "technical_skills": [
                "I'd love discuss how my Python/PyTorch expertise could accelerate your ML initiatives. Available for consulting or direct hire.",
                "Let's explore how my automation experience could streamline your current workflows. I'm available for 30-minute discovery calls.",
            ],
            "leadership": [
                "I bring strategic vision combined with hands-on ML implementation. Interested in discussing senior leadership roles.",
                "My track record leading cross-functional AI teams might complement your organization's goals. I welcome strategic discussions.",
            ],
            "problem_solving": [
                "Facing similar challenges? I specialize in turning complex ML problems into production solutions. Let's connect to explore possibilities.",
                "I'd be happy to share more about my approach to manufacturing automation and predictive maintenance systems.",
            ],
            "project_work": [
                "I'm currently accepting select consulting engagements focused on ML deployment and automation. What challenges are you facing?",
                "My availability for project work focuses on manufacturing AI, quality control systems, and data pipeline optimization.",
            ]
        }

        # Select appropriate CTA
        selected_cta = None

        if any(keyword in response_lower for keyword in ["python", "pytorch", "ml", "model", "automation"]):
            selected_cta = cta_options["technical_skills"][0]
        elif any(keyword in response_lower for keyword in ["led", "managed", "strategic", "leadership"]):
            selected_cta = cta_options["leadership"][0]
        elif any(keyword in response_lower for keyword in ["solution", "challenge", "problem"]):
            selected_cta = cta_options["problem_solving"][0]
        elif any(keyword in response_lower for keyword in ["project", "consulting", "engagement"]):
            selected_cta = cta_options["project_work"][0]
        else:
            # Default CTA
            selected_cta = "I'm available for both direct hire and consulting opportunities. Would you like to discuss how my background aligns with your needs?"

        # Enhance CTA with contacts
        enhanced_cta = selected_cta

        # Add specific contact method based on context
        if context and context.get("user_location") == "remote":
            enhanced_cta += " Best to connect via LinkedIn or email to explore next steps."
        elif context and context.get("urgency") == "high":
            enhanced_cta += " I can typically respond within 24 hours via email."

        # Always include LinkedIn as primary CTA
        if "linkedin" not in enhanced_cta.lower():
            enhanced_cta += " My LinkedIn profile is /matthew-pergolski - feel free to connect!"

        # Ensure response doesn't get too long
        combined_response = f"{response[:500].rstrip('.')} \n\n{enhanced_cta}"

        return combined_response[:800]  # Vercel response limit

    def _optimize_engagement(self, response: str) -> str:
        """Optimize the response for better user engagement."""
        optimization_rules = {
            # Length optimization
            "long_sentences": self._break_long_sentences,
            "remove_redundancy": self._remove_redundancy,
            "add_conversational_flow": self._add_conversational_elements,
        }

        result = response

        for rule_name, func in optimization_rules.items():
            result = func(result)

        return result

    def _break_long_sentences(self, text: str) -> str:
        """Break overly long sentences for better readability."""
        # Find sentences longer than 150 characters
        sentences = re.split(r'[.!?]+', text)

        optimized_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 150:
                # Break at natural breakpoints (comma, semicolon, etc.)
                parts = re.split(r'[,;]', sentence)
                if len(parts) > 1 and max(len(p) for p in parts) < 120:
                    # Only break if parts are reasonably balanced
                    sentence = ', '.join(parts)

            optimized_sentences.append(sentence)

        return '. '.join(filter(None, optimized_sentences)).rstrip('.') + '.'

    def _remove_redundancy(self, text: str) -> str:
        """Remove redundant or repetitive content."""
        # Simple deduplication for very similar phrases
        sentences = text.split('.')
        seen = set()
        deduplicated = []

        for sentence in sentences:
            sentence = sentence.strip()
            # Simple hash-based deduplication
            simplified = re.sub(r'[^(A-Za-z0-9\s)]', '', sentence.lower()).strip()
            if simplified and simplified not in seen and len(simplified) > 15:
                seen.add(simplified)
                deduplicated.append(sentence)

        return '. '.join(deduplicated) + '.'

    def _add_conversational_elements(self, text: str) -> str:
        """Add conversational elements to make response more engaging."""
        conversational_openers = [
            "Absolutely",
            "Great question",
            "Experience shows that",
            "Drawing from my work",
            "I'd add that"
        ]

        # Only add if response starts formally
        first_words = text[:50].strip()
        if not first_words.startswith(tuple(conversational_openers)):
            # Add a conversational element to the beginning (25% chance)
            if hash(text) % 4 == 0:
                conversational_phrase = "Drawing from my experience,"
                text = f"{conversational_phrase} {text.lower()}{text[1:]}" if text else text

        return text

    def _get_fallback_marketing_response(self) -> str:
        """Generate professional fallback response when model fails."""
        return """With 6+ years of experience in AI/ML engineering and data science, I've led numerous projects delivering real business value. My expertise spans Python, ML frameworks, cloud infrastructure, and turning complex problems into deployable solutions.

I'm particularly passionate about manufacturing automation and predictive systems, having reduced prediction errors by 35% and automated workflows saving 20+ hours weekly.

Whether you're looking to hire or consult with an experienced ML engineer, I'd welcome a conversation about your challenges and opportunities.

Feel free to connect on LinkedIn (/matthew-pergolski) or email me at matthew.pergolski@gmail.com - I typically respond within 24 hours."""


class ResponseOptimizer:
    """Optimizes response content for different contexts."""

    @staticmethod
    def optimize_for_context(response: str, context: Dict[str, Any]) -> str:
        """Optimize response based on visitor context."""
        optimizations = []

        # Technical depth based on visitor profile
        visitor_tech_level = context.get("tech_level", "intermediate")

        if visitor_tech_level == "expert":
            # Add more technical details
            optimizations.append(ResponseOptimizer._add_technical_depth)
        elif visitor_tech_level == "beginner":
            # Simplify technical concepts
            optimizations.append(ResponseOptimizer._simplify_technical_terms)

        # Time availability
        if context.get("urgency") == "high":
            optimizations.append(ResponseOptimizer._prioritize_immediate_actions)

        # Geographic considerations
        if context.get("location", "").lower() in ["remote", "virtual"]:
            optimizations.append(ResponseOptimizer._emphasize_remote_work)

        # Apply all relevant optimizations
        result = response
        for opt_func in optimizations:
            result = opt_func(result)

        return result

    @staticmethod
    def _add_technical_depth(response: str) -> str:
        """Add technical depth for expert-level conversations."""
        # Would expand with technical details specific to their expertise
        # For now, just return as-is since our responses are already technically strong
        return response

    @staticmethod
    def _simplify_technical_terms(response: str) -> str:
        """Simplify complex technical terms for broader accessibility."""
        simplifications = {
            "gradient boosting": "advanced prediction techniques",
            "convolutional neural networks": "specialized ML models for images and patterns",
            "reinforcement learning": "AI systems that learn by trial and improvement",
            "distributed computing": "running computations across multiple computers",
            "containerization": "packaging applications for easy deployment",
        }

        result = response
        for term, simple in simplifications.items():
            result = result.replace(term, f"{simple} (technical term: {term})")

        return result

    @staticmethod
    def _prioritize_immediate_actions(response: str) -> str:
        """Prioritize immediate actionable steps for urgent inquiries."""
        # Add urgency-aware language
        urgent_prefixes = [
            "I can help address this quickly:",
            "Let's focus on immediate solutions:",
            "For urgent needs, I recommend:"
        ]

        if not any(prefix.lower() in response.lower() for prefix in urgent_prefixes):
            response = f"{urgent_prefixes[0]} {response}"

        return response

    @staticmethod
    def _emphasize_remote_work(response: str) -> str:
        """Emphasize remote work capabilities for distributed teams."""
        remote_indicators = [
            "remote collaboration",
            "distributed team environment",
            "virtual work",
            "location independent"
        ]

        result = response

        # Add remote-friendly messaging
        if not any(indicator in result.lower() for indicator in remote_indicators):
            result += f" I'm comfortable working in distributed team environments and fully equipped for remote collaboration."

        return result


# Test the marketing layer
def test_marketing_layer():
    """Test the marketing enhancements."""
    marketing = MarketingLayer()

    test_responses = [
        "I developed a machine learning system for quality control.",
        "I led a team that improved prediction accuracy by 35%.",
        "I have experience with Python and TensorFlow.",
    ]

    print("Testing Marketing Layer Enhancements:")
    print("=" * 50)

    for i, response in enumerate(test_responses, 1):
        print(f"\\n🔧 Test {i}:")
        print(f"Original: {response}")

        enhanced = marketing.enhance_response(response)
        print(f"Enhanced: {enhanced}")

        print("-" * 30)

    print("\\nMarketing layer test complete!")


if __name__ == "__main__":
    test_marketing_layer()
