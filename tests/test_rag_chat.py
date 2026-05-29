import pytest

from src.services.rag.simple_chat import handle_chat_payload, retrieve_sources


def test_retrieve_sources_finds_experience_context():
    sources = retrieve_sources("Lockheed Martin AI machine learning models")

    labels = [source.label for source in sources]
    assert any("Experience" in label for label in labels)


@pytest.mark.asyncio
async def test_chat_falls_back_without_hugging_face(monkeypatch):
    monkeypatch.delenv("HUGGINGFACE_API_KEY", raising=False)
    monkeypatch.delenv("HF_TOKEN", raising=False)

    result = await handle_chat_payload(
        {"message": "What AI experience does Matthew have?"}
    )

    assert result["success"] is True
    assert result["provider"] == "local"
    assert "portfolio context" in result["response"].lower()
    assert result["sources"]


@pytest.mark.asyncio
async def test_chat_rejects_empty_message():
    result = await handle_chat_payload({"message": "   "})

    assert result["success"] is False
    assert "required" in result["error"].lower()
