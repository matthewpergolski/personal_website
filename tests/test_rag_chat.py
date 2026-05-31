import pytest

import src.services.rag.simple_chat as simple_chat
from src.services.rag.simple_chat import handle_chat_payload, retrieve_sources


def test_retrieve_sources_finds_experience_context():
    sources = retrieve_sources("Lockheed Martin AI machine learning models")

    labels = [source.label for source in sources]
    assert any("Experience" in label for label in labels)
    assert sources[0].label.startswith("Experience")


def test_retrieve_sources_can_use_synced_resume_text(monkeypatch):
    monkeypatch.setattr(
        simple_chat,
        "load_experience",
        lambda _root: {
            "summary": "General portfolio summary.",
            "resume_text": "Patent analytics roadmap with ontology cleanup and claim clustering.",
        },
    )
    monkeypatch.setattr(simple_chat, "_load_site_json", lambda: {})

    sources = retrieve_sources("claim clustering ontology")

    assert sources[0].label == "Resume text"
    assert "claim clustering" in sources[0].text


@pytest.mark.asyncio
async def test_chat_falls_back_without_hugging_face(monkeypatch):
    monkeypatch.delenv("HUGGINGFACE_API_KEY", raising=False)
    monkeypatch.delenv("HF_TOKEN", raising=False)

    result = await handle_chat_payload(
        {"message": "What AI experience does Matthew have?"}
    )

    assert result["success"] is True
    assert result["provider"] == "local"
    assert result["provider_label"] == "Local portfolio retrieval"
    assert "portfolio context" in result["response"].lower()
    assert result["sources"]
    assert {"label", "snippet"} <= set(result["sources"][0])


@pytest.mark.asyncio
async def test_chat_rejects_empty_message():
    result = await handle_chat_payload({"message": "   "})

    assert result["success"] is False
    assert "required" in result["error"].lower()


@pytest.mark.asyncio
async def test_chat_uses_recent_user_history_for_retrieval(monkeypatch):
    monkeypatch.delenv("HUGGINGFACE_API_KEY", raising=False)
    monkeypatch.delenv("HF_TOKEN", raising=False)
    monkeypatch.setattr(
        simple_chat,
        "load_experience",
        lambda _root: {
            "summary": "General portfolio summary.",
            "experience": [
                {
                    "title": "AI Platform Engineer",
                    "company": "Lockheed Martin",
                    "period": "2025 - Present",
                    "bullets": [
                        "Built coordinated LLM agents for requirements workflows."
                    ],
                }
            ],
            "skills": {"programming": ["Python"]},
        },
    )
    monkeypatch.setattr(simple_chat, "_load_site_json", lambda: {})

    result = await handle_chat_payload(
        {
            "message": "What about that platform?",
            "history": [
                {
                    "role": "user",
                    "content": "Tell me about coordinated LLM agents.",
                }
            ],
        }
    )

    assert result["success"] is True
    assert any("Experience" in source["label"] for source in result["sources"])
