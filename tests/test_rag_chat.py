import pytest

import src.services.rag.simple_chat as simple_chat
from src.services.rag.simple_chat import handle_chat_payload, retrieve_sources


def test_retrieve_sources_finds_experience_context():
    sources = retrieve_sources("Lockheed Martin AI machine learning models")

    labels = [source.label for source in sources]
    assert any("Experience" in label for label in labels)
    assert sources[0].label.startswith("Experience")


def test_python_work_query_prioritizes_experience_over_skills():
    sources = retrieve_sources("How have you used Python in your AI/ML work?")

    assert sources[0].label.startswith("Experience")
    assert "Python" in sources[0].text


def test_general_ai_query_does_not_surface_site_profile():
    sources = retrieve_sources("What AI/ML work have you done?")

    assert "Site profile" not in [source.label for source in sources]


def test_lockheed_summary_prioritizes_recent_roles():
    sources = retrieve_sources("Summarize your Lockheed Martin experience.")

    assert sources[0].label == "Experience: A/AI Machine Learning Engineer Staff"
    assert sources[1].label == "Experience: A/AI Machine Learning Engineer Senior"


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
    assert "strongest matches" in result["response"].lower()
    assert result["sources"]
    assert {"label", "snippet"} <= set(result["sources"][0])


@pytest.mark.asyncio
async def test_chat_greeting_does_not_reuse_prior_context(monkeypatch):
    monkeypatch.delenv("HUGGINGFACE_API_KEY", raising=False)
    monkeypatch.delenv("HF_TOKEN", raising=False)

    result = await handle_chat_payload(
        {
            "message": "Hello",
            "history": [
                {
                    "role": "user",
                    "content": "What AI/ML work have you done?",
                }
            ],
        }
    )

    assert result["success"] is True
    assert "Hi, I can answer questions" in result["response"]
    assert result["sources"] == []


@pytest.mark.asyncio
async def test_role_fit_query_gets_target_role_answer(monkeypatch):
    monkeypatch.delenv("HUGGINGFACE_API_KEY", raising=False)
    monkeypatch.delenv("HF_TOKEN", raising=False)

    result = await handle_chat_payload(
        {"message": "What kind of roles are you targeting?"}
    )

    assert result["success"] is True
    assert "Good target roles include" in result["response"]
    assert "AI/ML engineer" in result["response"]


@pytest.mark.asyncio
async def test_lockheed_summary_gets_career_level_answer(monkeypatch):
    monkeypatch.delenv("HUGGINGFACE_API_KEY", raising=False)
    monkeypatch.delenv("HF_TOKEN", raising=False)

    result = await handle_chat_payload(
        {"message": "Summarize your Lockheed Martin experience."}
    )

    assert result["success"] is True
    assert "spans operations, data science, and AI/ML engineering" in result["response"]
    assert "A/AI Machine Learning Engineer Staff" in result["response"]


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
        {"message": "What about that platform?"},
        history=[
            {
                "role": "user",
                "content": "Tell me about coordinated LLM agents.",
            }
        ],
    )

    assert result["success"] is True
    assert any("Experience" in source["label"] for source in result["sources"])


@pytest.mark.asyncio
async def test_chat_payload_history_is_ignored(monkeypatch):
    captured = {}

    async def fake_answer_chat(query, *, history=None):
        captured["history"] = history
        return {"success": True, "response": "ok", "sources": []}

    monkeypatch.setattr(simple_chat, "answer_chat", fake_answer_chat)

    result = await handle_chat_payload(
        {
            "message": "What about that?",
            "history": [{"role": "user", "content": "client controlled"}],
        }
    )

    assert result["success"] is True
    assert captured["history"] == []
